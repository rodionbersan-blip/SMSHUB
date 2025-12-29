from __future__ import annotations

from contextlib import suppress
from datetime import datetime, timezone
from decimal import Decimal
from html import escape
from typing import List
from uuid import uuid4

from aiogram import F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message, ReplyKeyboardRemove
from aiogram.utils.keyboard import InlineKeyboardBuilder

from cachebot.deps import get_deps
from cachebot.keyboards import MenuAction, MenuButtons, base_keyboard, inline_menu
from cachebot.models.deal import Deal, DealStatus
from cachebot.models.user import ApplicationStatus, MerchantApplication, UserProfile, UserRole
from cachebot.services.users import MerchantRecord

router = Router(name="commands")
ROLE_SELLER = "role:seller"
ROLE_MERCHANT = "role:merchant"
BANK_OPTIONS = {
    "alpha": "Альфа",
    "sber": "Сбер",
    "ozon": "Ozon",
}
APP_VIEW_PREFIX = "app:view:"
APP_ACCEPT_PREFIX = "app:accept:"
APP_REJECT_PREFIX = "app:reject:"
MY_DEALS_PAGE_PREFIX = "mydeals:page:"
MY_DEALS_VIEW_PREFIX = "mydeals:view:"
DEAL_CANCEL_PREFIX = "dealact:cancel:"
DEAL_COMPLETE_PREFIX = "dealact:complete:"
DEALS_PER_PAGE = 4
ADMIN_PANEL_MENU = "admin:panel"
ADMIN_PANEL_MERCHANTS = "admin:panel:merchants"
ADMIN_PANEL_APPS = "admin:panel:apps"
ADMIN_PANEL_RATES = "admin:panel:rates"
ADMIN_MERCHANT_VIEW_PREFIX = "admin:merchant:view:"
ADMIN_MERCHANT_DEALS_PREFIX = "admin:merchant:deals:"
ADMIN_MERCHANT_EXCLUDE_PREFIX = "admin:merchant:exclude:"
ADMIN_RATE_SET = "admin:rate:set"
ADMIN_FEE_SET = "admin:fee:set"
STATUS_TITLES = {
    DealStatus.OPEN: "Ожидает покупателя",
    DealStatus.RESERVED: "Ожидаем оплату",
    DealStatus.PAID: "Оплата получена",
    DealStatus.COMPLETED: "Завершена",
    DealStatus.CANCELED: "Отменена",
    DealStatus.EXPIRED: "Истекла",
}
STATUS_SHORT = {
    DealStatus.OPEN: "Открыта",
    DealStatus.RESERVED: "В работе",
    DealStatus.PAID: "Оплачено",
    DealStatus.COMPLETED: "Закрыта",
    DealStatus.CANCELED: "Отменена",
    DealStatus.EXPIRED: "Истекла",
}
STATUS_BUTTON_LABELS = {
    DealStatus.OPEN: "🟡 Не оплачено",
    DealStatus.RESERVED: "🟡 Не оплачено",
    DealStatus.PAID: "💰 Оплачено",
    DealStatus.COMPLETED: "✅ Успешно",
    DealStatus.CANCELED: "⛔ Отменена",
    DealStatus.EXPIRED: "⏳ Истекла",
}


class MerchantApplicationState(StatesGroup):
    choosing_banks = State()
    personal_bank = State()
    risk_ack = State()
    waiting_photos = State()


class AdminRateState(StatesGroup):
    waiting_rate = State()
    waiting_fee = State()


def _command_args(message: Message) -> str:
    if not message.text:
        return ""
    parts = message.text.split(maxsplit=1)
    return parts[1] if len(parts) > 1 else ""


def _role_keyboard() -> InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()
    builder.button(text="💸 Продажа USDT", callback_data=ROLE_SELLER)
    builder.button(text="👔 Стать мерчантом", callback_data=ROLE_MERCHANT)
    builder.adjust(2)
    return builder


def _bank_keyboard(selected: List[str]) -> InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()
    for key, label in BANK_OPTIONS.items():
        prefix = "✅ " if key in selected else ""
        builder.button(text=f"{prefix}{label}", callback_data=f"bank:{key}")
    builder.button(text="Готово", callback_data="bank:done")
    builder.adjust(3, 1)
    return builder


def _yes_no_keyboard(prefix: str) -> InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()
    builder.button(text="Да", callback_data=f"{prefix}:yes")
    builder.button(text="Нет", callback_data=f"{prefix}:no")
    builder.adjust(2)
    return builder


async def _start_merchant_application(
    callback: CallbackQuery, state: FSMContext, deps=None
) -> bool:
    user = callback.from_user
    if not user:
        return False
    deps = deps or get_deps()
    if await deps.user_service.has_merchant_access(user.id):
        await deps.user_service.set_role(user.id, UserRole.BUYER)
        await _delete_callback_message(callback)
        await callback.message.answer("Меню покупателя", reply_markup=inline_menu(UserRole.BUYER))
        return True
    await deps.user_service.ensure_profile(
        user.id,
        full_name=user.full_name,
        username=user.username,
    )
    await state.set_state(MerchantApplicationState.choosing_banks)
    await state.update_data(
        banks=[],
        user_id=user.id,
        username=user.username,
    )
    kb = _bank_keyboard([])
    chat_id = callback.message.chat.id if callback.message else user.id
    await _delete_callback_message(callback)
    await callback.bot.send_message(
        chat_id,
        "Отлично, тогда немного вопросов для составления заявки.\n"
        "Какие банки из списка у вас присутствуют? Отметь и нажми «Готово».",
        reply_markup=kb.as_markup(),
    )
    return True


@router.message(CommandStart())
async def start(message: Message, state: FSMContext) -> None:
    await state.clear()
    deps = get_deps()
    user = message.from_user
    if user:
        await deps.user_service.ensure_profile(
            user.id,
            full_name=user.full_name,
            username=user.username,
        )
    is_admin = bool(user and user.id in deps.config.admin_ids)
    await message.answer(
        "Йо бро, это лучший бот для обмена USDT сразу в кэш 🚀\n"
        "Выбери свою роль:",
        reply_markup=_role_keyboard().as_markup(),
    )
    role = await deps.user_service.role_of(user.id) if user else None
    if role == UserRole.BUYER:
        await message.answer(
            "Ты уже мерчант. Нажми «Меню», чтобы открыть действия.",
            reply_markup=base_keyboard(is_admin),
        )
    else:
        await message.answer(
            "После выбора роли появится кнопка «Меню».",
            reply_markup=ReplyKeyboardRemove(),
        )


@router.callback_query(F.data == ROLE_SELLER)
async def role_seller(callback: CallbackQuery) -> None:
    deps = get_deps()
    user = callback.from_user
    if not user:
        await callback.answer()
        return
    await deps.user_service.ensure_profile(
        user.id,
        full_name=user.full_name,
        username=user.username,
    )
    await deps.user_service.set_role(user.id, UserRole.SELLER)
    is_admin = user.id in deps.config.admin_ids
    with suppress(TelegramBadRequest):
        await callback.message.delete()
    await callback.message.answer("Отлично! переходи в меню", reply_markup=base_keyboard(is_admin))
    await callback.answer("Роль продавца установлена")


@router.callback_query(F.data == ROLE_MERCHANT)
async def role_merchant(callback: CallbackQuery, state: FSMContext) -> None:
    if not await _start_merchant_application(callback, state):
        await callback.answer()
        return
    await callback.answer()


@router.message(F.text == MenuButtons.SHOW_MENU.value)
async def open_menu(message: Message) -> None:
    deps = get_deps()
    user = message.from_user
    if not user:
        return
    role = await deps.user_service.role_of(user.id)
    if not role:
        await message.answer("Сначала выбери роль через /start")
        return
    title = "Меню продавца" if role == UserRole.SELLER else "Меню покупателя"
    await message.answer(title, reply_markup=inline_menu(role))


@router.callback_query(F.data.startswith("bank:"), MerchantApplicationState.choosing_banks)
async def merchant_choose_banks(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    banks = set(data.get("banks") or [])
    action = callback.data.split(":", 1)[1]
    if action == "done":
        if not banks:
            await callback.answer("Отметь хотя бы один банк", show_alert=True)
            return
        await state.update_data(banks=list(banks))
        await state.set_state(MerchantApplicationState.personal_bank)
        await callback.message.answer(
            "Личные банки ли вы будете использовать?",
            reply_markup=_yes_no_keyboard("personal").as_markup(),
        )
        await callback.answer()
        return
    if action in BANK_OPTIONS:
        if action in banks:
            banks.remove(action)
        else:
            banks.add(action)
        await state.update_data(banks=list(banks))
        await callback.message.edit_reply_markup(
            reply_markup=_bank_keyboard(list(banks)).as_markup()
        )
    await callback.answer()


@router.callback_query(F.data.startswith("personal:"), MerchantApplicationState.personal_bank)
async def merchant_personal(callback: CallbackQuery, state: FSMContext) -> None:
    answer = callback.data.split(":", 1)[1]
    uses_personal = answer == "yes"
    await state.update_data(uses_personal=uses_personal)
    await state.set_state(MerchantApplicationState.risk_ack)
    await callback.message.answer(
        "Весь риск блокировки берёте на себя? "
        "Т.к. используете свой банк и деньги могут быть разблокированы.",
        reply_markup=_yes_no_keyboard("risk").as_markup(),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("risk:"), MerchantApplicationState.risk_ack)
async def merchant_risk(callback: CallbackQuery, state: FSMContext) -> None:
    answer = callback.data.split(":", 1)[1]
    if answer == "no":
        await state.clear()
        await callback.message.answer(
            "К сожалению, мы не сможем сотрудничать. "
            "Если передумаете, заново напишите /start."
        )
        await callback.answer("Заявка остановлена")
        return
    await state.update_data(accepts_risk=True)
    await state.set_state(MerchantApplicationState.waiting_photos)
    await callback.message.answer("Пришлите, пожалуйста, скрины личных кабинетов.")
    await callback.answer()


@router.message(MerchantApplicationState.waiting_photos)
async def merchant_photos(message: Message, state: FSMContext) -> None:
    if not message.photo:
        await message.answer("Нужно отправить фото. Попробуй снова.")
        return
    deps = get_deps()
    data = await state.get_data()
    photo_id = max(message.photo, key=lambda ph: ph.file_size or 0).file_id
    photo_ids = list(data.get("photo_file_ids") or [])
    photo_ids.append(photo_id)
    await state.clear()
    application = MerchantApplication(
        id=str(uuid4()),
        user_id=data["user_id"],
        username=data.get("username"),
        banks=list(data.get("banks") or []),
        uses_personal_bank=bool(data.get("uses_personal")),
        accepts_risk=True,
        photo_file_ids=photo_ids,
        created_at=datetime.now(timezone.utc),
    )
    await deps.user_service.add_application(application)
    await message.answer("Отлично! заявка уже на рассмотрении, ожидайте сообщения.")
    summary = _format_application(application)
    for admin_id in deps.config.admin_ids:
        try:
            await message.bot.send_photo(
                admin_id,
                photo_id,
                caption=summary,
            )
        except Exception:
            await message.bot.send_message(admin_id, summary)


@router.message(Command("rate"))
async def show_rate(message: Message) -> None:
    deps = get_deps()
    snapshot = await deps.rate_provider.snapshot()
    await message.answer(
        f"Текущий курс: 1 USDT = {snapshot.usd_rate} RUB\n"
        f"Комиссия: {snapshot.fee_percent}%"
    )


@router.message(Command("setrate"))
async def set_rate(message: Message) -> None:
    deps = get_deps()
    user = message.from_user
    if not user:
        return
    if user.id not in deps.config.admin_ids:
        await message.answer("Команда доступна только администраторам")
        return
    raw = _command_args(message).strip()
    if not raw:
        await message.answer("Укажи курс и опционально комиссию: /setrate 1.02 0.5")
        return
    try:
        usd_rate, fee_percent = _parse_rate_input(raw)
    except ValueError:
        await message.answer("Не удалось распознать числа")
        return
    await _apply_rate_change(deps, message, usd_rate, fee_percent)


@router.message(Command("balance"))
async def show_balance(message: Message) -> None:
    user = message.from_user
    if not user:
        return
    await _send_balance(user.id, message.chat.id, message.bot)


@router.message(Command("profile"))
async def show_profile(message: Message) -> None:
    user = message.from_user
    if not user:
        return
    await _send_profile(user, message.chat.id, message.bot)


@router.message(Command("mydeals"))
async def my_deals(message: Message) -> None:
    user = message.from_user
    if not user:
        return
    await _render_my_deals(
        user.id,
        page=0,
        chat_id=message.chat.id,
        bot=message.bot,
    )


@router.message(F.text == MenuButtons.ADMIN_PANEL.value)
async def admin_panel_entry(message: Message) -> None:
    deps = get_deps()
    user = message.from_user
    if not user or user.id not in deps.config.admin_ids:
        await message.answer("Доступ только для владельцев")
        return
    await _send_admin_panel(message.chat.id, message.bot)


@router.message(Command("markpaid"))
async def mark_paid(message: Message) -> None:
    deps = get_deps()
    user = message.from_user
    if not user:
        return
    if user.id not in deps.config.admin_ids:
        await message.answer("Команда доступна только администраторам")
        return
    deal_id = _command_args(message).strip()
    if not deal_id:
        await message.answer("Укажи ID сделки")
        return
    await _mark_deal_paid(deps, message, deal_id)


# -- Menu action callbacks ---------------------------------------------------

@router.callback_query(F.data == MenuAction.BALANCE.value)
async def balance_from_menu(callback: CallbackQuery) -> None:
    user = callback.from_user
    if not user:
        await callback.answer()
        return
    chat_id = callback.message.chat.id if callback.message else user.id
    await _delete_callback_message(callback)
    await _send_balance(user.id, chat_id, callback.bot)
    await callback.answer()


@router.callback_query(F.data == MenuAction.PROFILE.value)
async def profile_from_menu(callback: CallbackQuery) -> None:
    user = callback.from_user
    if not user:
        await callback.answer()
        return
    chat_id = callback.message.chat.id if callback.message else user.id
    await _delete_callback_message(callback)
    await _send_profile(user, chat_id, callback.bot)
    await callback.answer()


@router.callback_query(F.data == MenuAction.SETTINGS.value)
async def settings_from_menu(callback: CallbackQuery, state: FSMContext) -> None:
    deps = get_deps()
    user = callback.from_user
    if not user:
        await callback.answer()
        return
    role = await deps.user_service.role_of(user.id)
    builder = InlineKeyboardBuilder()
    if role == UserRole.BUYER:
        builder.button(text="Продать USDT", callback_data=MenuAction.SETTINGS_SELLER.value)
    else:
        builder.button(text="Стать мерчантом", callback_data=MenuAction.SETTINGS_MERCHANT.value)
    builder.button(text="⬅️ Назад", callback_data=MenuAction.BACK.value)
    chat_id = callback.message.chat.id if callback.message else user.id
    await _delete_callback_message(callback)
    text = (
        "Раздел настроек. Здесь можно оставить заявку мерчанта."
        if role != UserRole.BUYER
        else "Ты уже мерчант. Можно открыть меню покупателя или перейти в режим продавца."
    )
    await callback.bot.send_message(chat_id, text, reply_markup=builder.as_markup())
    await callback.answer()


@router.callback_query(F.data == MenuAction.SETTINGS_MERCHANT.value)
async def settings_become_merchant(callback: CallbackQuery, state: FSMContext) -> None:
    deps = get_deps()
    user = callback.from_user
    if not user:
        await callback.answer()
        return
    role = await deps.user_service.role_of(user.id)
    if role == UserRole.BUYER:
        chat_id = callback.message.chat.id if callback.message else user.id
        await _delete_callback_message(callback)
        await callback.bot.send_message(chat_id, "Меню покупателя", reply_markup=inline_menu(UserRole.BUYER))
        await callback.answer("Открываю меню мерчанта")
        return
    await _start_merchant_application(callback, state, deps)
    await callback.answer()


@router.callback_query(F.data == MenuAction.SETTINGS_SELLER.value)
async def settings_switch_to_seller(callback: CallbackQuery) -> None:
    deps = get_deps()
    user = callback.from_user
    if not user:
        await callback.answer()
        return
    await deps.user_service.set_role(user.id, UserRole.SELLER)
    is_admin = user.id in deps.config.admin_ids
    chat_id = callback.message.chat.id if callback.message else user.id
    await _delete_callback_message(callback)
    await callback.bot.send_message(
        chat_id,
        "Отлично! переходи в меню",
        reply_markup=base_keyboard(is_admin),
    )
    await callback.answer("Переключено в режим продавца")


@router.callback_query(F.data == MenuAction.BACK.value)
async def back_to_menu(callback: CallbackQuery) -> None:
    deps = get_deps()
    user = callback.from_user
    if not user:
        await callback.answer()
        return
    role = await deps.user_service.role_of(user.id)
    if not role:
        await callback.message.answer("Сначала выбери роль через /start")
        await callback.answer()
        return
    title = "Меню продавца" if role == UserRole.SELLER else "Меню покупателя"
    deleted = False
    with suppress(TelegramBadRequest):
        await callback.message.delete()
        deleted = True
    if deleted:
        await callback.message.answer(title, reply_markup=inline_menu(role))
    else:
        try:
            await callback.message.edit_text(title, reply_markup=inline_menu(role))
        except TelegramBadRequest:
            await callback.message.answer(title, reply_markup=inline_menu(role))
    await callback.answer()


@router.callback_query(F.data == MenuAction.MY_DEALS.value)
async def my_deals_from_menu(callback: CallbackQuery) -> None:
    user = callback.from_user
    if not user:
        await callback.answer()
        return
    chat_id = callback.message.chat.id if callback.message else user.id
    await _delete_callback_message(callback)
    await _render_my_deals(
        user.id,
        page=0,
        chat_id=chat_id,
        bot=callback.bot,
    )
    await callback.answer()


@router.callback_query(F.data.startswith(MY_DEALS_PAGE_PREFIX))
async def my_deals_page(callback: CallbackQuery) -> None:
    user = callback.from_user
    if not user:
        await callback.answer()
        return
    payload = callback.data[len(MY_DEALS_PAGE_PREFIX) :]
    try:
        page = int(payload)
    except ValueError:
        await callback.answer()
        return
    await _render_my_deals(user.id, page=page, message=callback.message)
    await callback.answer()


@router.callback_query(F.data.startswith(MY_DEALS_VIEW_PREFIX))
async def my_deal_detail(callback: CallbackQuery) -> None:
    user = callback.from_user
    if not user:
        await callback.answer()
        return
    payload = callback.data[len(MY_DEALS_VIEW_PREFIX) :]
    try:
        page_str, deal_id = payload.split(":", 1)
        page = int(page_str)
    except ValueError:
        await callback.answer()
        return
    await _render_deal_detail(
        user.id,
        deal_id=deal_id,
        page=page,
        message=callback.message,
    )
    await callback.answer()


@router.callback_query(F.data.startswith(DEAL_CANCEL_PREFIX))
async def deal_cancel_action(callback: CallbackQuery) -> None:
    user = callback.from_user
    if not user:
        await callback.answer()
        return
    payload = callback.data[len(DEAL_CANCEL_PREFIX) :]
    try:
        page_str, deal_id = payload.split(":", 1)
        page = int(page_str)
    except ValueError:
        await callback.answer()
        return
    try:
        await _cancel_deal_core(user.id, deal_id)
    except Exception as exc:
        await callback.answer(str(exc), show_alert=True)
        return
    await _render_deal_detail(
        user.id,
        deal_id=deal_id,
        page=page,
        message=callback.message,
    )
    await callback.answer("Сделка отменена")


@router.callback_query(F.data.startswith(DEAL_COMPLETE_PREFIX))
async def deal_complete_action(callback: CallbackQuery) -> None:
    user = callback.from_user
    if not user:
        await callback.answer()
        return
    payload = callback.data[len(DEAL_COMPLETE_PREFIX) :]
    try:
        page_str, deal_id = payload.split(":", 1)
        page = int(page_str)
    except ValueError:
        await callback.answer()
        return
    try:
        await _complete_deal_core(user.id, deal_id, callback.bot)
    except Exception as exc:
        await callback.answer(str(exc), show_alert=True)
        return
    await _render_deal_detail(
        user.id,
        deal_id=deal_id,
        page=page,
        message=callback.message,
    )
    await callback.answer("Сделка завершена")


@router.callback_query(F.data == ADMIN_PANEL_MENU)
async def admin_panel_callback(callback: CallbackQuery) -> None:
    deps = get_deps()
    user = callback.from_user
    if not user or user.id not in deps.config.admin_ids:
        await callback.answer("Нет доступа", show_alert=True)
        return
    await _send_admin_panel(callback.message.chat.id, callback.bot)
    await callback.answer()


@router.callback_query(F.data == ADMIN_PANEL_APPS)
async def admin_panel_apps(callback: CallbackQuery) -> None:
    deps = get_deps()
    user = callback.from_user
    if not user or user.id not in deps.config.admin_ids:
        await callback.answer("Нет доступа", show_alert=True)
        return
    await _send_applications_list(callback.message.chat.id, callback.bot)
    await callback.answer()


@router.callback_query(F.data == ADMIN_PANEL_RATES)
async def admin_panel_rates(callback: CallbackQuery) -> None:
    deps = get_deps()
    user = callback.from_user
    if not user or user.id not in deps.config.admin_ids:
        await callback.answer("Нет доступа", show_alert=True)
        return
    snapshot = await deps.rate_provider.snapshot()
    builder = InlineKeyboardBuilder()
    builder.button(text="Изменить курс", callback_data=ADMIN_RATE_SET)
    builder.button(text="Изменить комиссию", callback_data=ADMIN_FEE_SET)
    builder.button(text="⬅️ Админ панель", callback_data=ADMIN_PANEL_MENU)
    text = (
        "<b>Управление ценой</b>\n"
        f"Текущий курс: 1 USDT = {snapshot.usd_rate} RUB\n"
        f"Комиссия: {snapshot.fee_percent}%"
    )
    await callback.bot.send_message(
        callback.message.chat.id,
        text,
        reply_markup=builder.as_markup(),
    )
    await callback.answer()


@router.callback_query(F.data == ADMIN_RATE_SET)
async def admin_rate_set(callback: CallbackQuery, state: FSMContext) -> None:
    deps = get_deps()
    user = callback.from_user
    if not user or user.id not in deps.config.admin_ids:
        await callback.answer("Нет доступа", show_alert=True)
        return
    await state.set_state(AdminRateState.waiting_rate)
    await callback.message.answer(
        "Введи новый курс (пример: 92.5). Для отмены напиши «Отмена».",
    )
    await callback.answer()


@router.callback_query(F.data == ADMIN_FEE_SET)
async def admin_fee_set(callback: CallbackQuery, state: FSMContext) -> None:
    deps = get_deps()
    user = callback.from_user
    if not user or user.id not in deps.config.admin_ids:
        await callback.answer("Нет доступа", show_alert=True)
        return
    await state.set_state(AdminRateState.waiting_fee)
    await callback.message.answer(
        "Введи новую комиссию в процентах (пример: 0.5). Для отмены напиши «Отмена».",
    )
    await callback.answer()


@router.callback_query(F.data == ADMIN_PANEL_MERCHANTS)
async def admin_panel_merchants(callback: CallbackQuery) -> None:
    deps = get_deps()
    user = callback.from_user
    if not user or user.id not in deps.config.admin_ids:
        await callback.answer("Нет доступа", show_alert=True)
        return
    await _send_merchants_list(callback.message.chat.id, callback.bot)
    await callback.answer()


@router.callback_query(F.data.startswith(ADMIN_MERCHANT_VIEW_PREFIX))
async def admin_view_merchant(callback: CallbackQuery) -> None:
    deps = get_deps()
    user = callback.from_user
    if not user or user.id not in deps.config.admin_ids:
        await callback.answer("Нет доступа", show_alert=True)
        return
    merchant_id = int(callback.data[len(ADMIN_MERCHANT_VIEW_PREFIX) :])
    await _send_merchant_detail(callback, merchant_id)
    await callback.answer()


@router.callback_query(F.data.startswith(ADMIN_MERCHANT_DEALS_PREFIX))
async def admin_view_merchant_deals(callback: CallbackQuery) -> None:
    deps = get_deps()
    user = callback.from_user
    if not user or user.id not in deps.config.admin_ids:
        await callback.answer("Нет доступа", show_alert=True)
        return
    merchant_id = int(callback.data[len(ADMIN_MERCHANT_DEALS_PREFIX) :])
    await _send_merchant_deals(callback, merchant_id)
    await callback.answer()


@router.callback_query(F.data.startswith(ADMIN_MERCHANT_EXCLUDE_PREFIX))
async def admin_exclude_merchant(callback: CallbackQuery) -> None:
    deps = get_deps()
    user = callback.from_user
    if not user or user.id not in deps.config.admin_ids:
        await callback.answer("Нет доступа", show_alert=True)
        return
    merchant_id = int(callback.data[len(ADMIN_MERCHANT_EXCLUDE_PREFIX) :])
    await deps.user_service.set_role(merchant_id, UserRole.SELLER, revoke_merchant=True)
    with suppress(Exception):
        await callback.bot.send_message(
            merchant_id,
            "⚠️ Доступ покупателя отключен администратором.",
        )
    with suppress(TelegramBadRequest):
        await callback.message.delete()
    await callback.message.answer(
        f"Пользователь {merchant_id} исключён из списка мерчантов.",
        reply_markup=_admin_panel_back_markup(),
    )
    await callback.answer("Права мерчанта сняты")


@router.callback_query(F.data.startswith(APP_VIEW_PREFIX))
async def application_detail(callback: CallbackQuery) -> None:
    deps = get_deps()
    user = callback.from_user
    if not user or user.id not in deps.config.admin_ids:
        await callback.answer("Нет доступа", show_alert=True)
        return
    app_id = callback.data[len(APP_VIEW_PREFIX) :]
    application = await deps.user_service.get_application(app_id)
    if not application:
        await callback.answer("Заявка не найдена", show_alert=True)
        return
    markup = None
    if application.status == ApplicationStatus.PENDING:
        builder = InlineKeyboardBuilder()
        builder.button(text="Принять", callback_data=f"{APP_ACCEPT_PREFIX}{application.id}")
        builder.button(text="Отклонить", callback_data=f"{APP_REJECT_PREFIX}{application.id}")
        builder.adjust(2)
        markup = builder.as_markup()
    summary = _format_application(application)
    if application.photo_file_ids:
        await callback.message.answer_photo(
            application.photo_file_ids[0],
            caption=summary,
            reply_markup=markup,
        )
    else:
        await callback.message.answer(summary, reply_markup=markup)
    await callback.answer()


@router.callback_query(F.data.startswith(APP_ACCEPT_PREFIX))
async def application_accept(callback: CallbackQuery) -> None:
    deps = get_deps()
    user = callback.from_user
    if not user or user.id not in deps.config.admin_ids:
        await callback.answer("Нет доступа", show_alert=True)
        return
    app_id = callback.data[len(APP_ACCEPT_PREFIX) :]
    application = await deps.user_service.update_application_status(
        app_id, ApplicationStatus.ACCEPTED
    )
    if not application:
        await callback.answer("Заявка не найдена", show_alert=True)
        return
    await deps.user_service.set_role(application.user_id, UserRole.BUYER)
    await callback.message.answer(f"Заявка {application.id} одобрена. Права покупателя выданы.")
    try:
        await callback.bot.send_message(
            application.user_id,
            "✅ Твоя заявка мерчанта одобрена! Теперь доступен режим покупателя. "
            "Нажми /start, чтобы обновить меню.",
        )
    except Exception:
        pass
    await callback.answer("Заявка принята")


@router.callback_query(F.data.startswith(APP_REJECT_PREFIX))
async def application_reject(callback: CallbackQuery) -> None:
    deps = get_deps()
    user = callback.from_user
    if not user or user.id not in deps.config.admin_ids:
        await callback.answer("Нет доступа", show_alert=True)
        return
    app_id = callback.data[len(APP_REJECT_PREFIX) :]
    application = await deps.user_service.update_application_status(
        app_id, ApplicationStatus.REJECTED
    )
    if not application:
        await callback.answer("Заявка не найдена", show_alert=True)
        return
    await callback.message.answer(f"Заявка {application.id} отклонена.")
    try:
        await callback.bot.send_message(
            application.user_id,
            "К сожалению, твоя заявка мерчанта отклонена. "
            "Если хочешь попробовать снова, напиши /start позже.",
        )
    except Exception:
        pass
    await callback.answer("Заявка отклонена")


def _parse_rate_input(text: str) -> tuple[Decimal, Decimal | None]:
    normalized = text.replace(",", ".").split()
    if not normalized:
        raise ValueError("empty")
    usd_rate = Decimal(normalized[0])
    if usd_rate <= 0:
        raise ValueError("rate")
    fee_percent: Decimal | None = None
    if len(normalized) > 1:
        fee_percent = Decimal(normalized[1])
        if fee_percent < 0:
            raise ValueError("fee")
    return usd_rate, fee_percent


async def _apply_rate_change(
    deps, message: Message, usd_rate: Decimal, fee_percent: Decimal | None
) -> None:
    snapshot = await deps.rate_provider.set_rate(usd_rate, fee_percent)
    await message.answer(
        f"Новые параметры:\nКурс: 1 USDT = {snapshot.usd_rate} RUB\nКомиссия: {snapshot.fee_percent}%"
    )


async def _mark_deal_paid(deps, message: Message, deal_id: str) -> None:
    try:
        deal = await deps.deal_service.mark_paid_manual(deal_id)
    except Exception as exc:
        await message.answer(f"Не удалось отметить оплату: {exc}")
        return
    await message.answer(f"Сделка {deal.public_id} отмечена как оплаченная")
    await message.bot.send_message(
        deal.seller_id,
        f"✅ Платеж по сделке {deal.public_id} подтвержден вручную администратором.",
    )
    if deal.buyer_id:
        await message.bot.send_message(
            deal.buyer_id,
            f"Сделка {deal.public_id} отмечена как оплаченная администратором. Ожидайте передачу наличных.",
        )


async def _send_balance(user_id: int, chat_id: int, bot) -> None:
    deps = get_deps()
    balance = await deps.deal_service.balance_of(user_id)
    builder = InlineKeyboardBuilder()
    builder.button(text="⬅️ Назад", callback_data=MenuAction.BACK.value)
    await bot.send_message(
        chat_id,
        f"Твой баланс: {balance} RUB",
        reply_markup=builder.as_markup(),
    )


async def _send_profile(user, chat_id: int, bot) -> None:
    deps = get_deps()
    profile = await deps.user_service.ensure_profile(
        user.id,
        full_name=user.full_name,
        username=user.username,
    )
    deals = await deps.deal_service.list_user_deals(user.id)
    builder = InlineKeyboardBuilder()
    builder.button(text="⬅️ Назад", callback_data=MenuAction.BACK.value)
    await bot.send_message(
        chat_id,
        _format_profile(profile, deals),
        reply_markup=builder.as_markup(),
    )


async def _render_my_deals(
    user_id: int,
    *,
    page: int,
    chat_id: int | None = None,
    bot=None,
    message: Message | None = None,
) -> None:
    deps = get_deps()
    deals = await deps.deal_service.list_user_deals(user_id)
    if not deals:
        text = "У тебя пока нет сделок"
        if message:
            with suppress(TelegramBadRequest):
                await message.edit_text(text, reply_markup=_back_only_markup())
        elif bot and chat_id is not None:
            await bot.send_message(chat_id, text, reply_markup=_back_only_markup())
        return
    total_pages = max(1, (len(deals) + DEALS_PER_PAGE - 1) // DEALS_PER_PAGE)
    page = max(0, min(page, total_pages - 1))
    start = page * DEALS_PER_PAGE
    chunk = deals[start : start + DEALS_PER_PAGE]
    total = len(deals)
    success = sum(1 for item in deals if item.status == DealStatus.COMPLETED)
    failed = sum(1 for item in deals if item.status in {DealStatus.CANCELED, DealStatus.EXPIRED})
    text = _format_deal_list_text(
        total=total,
        success=success,
        failed=failed,
        page=page + 1,
        total_pages=total_pages,
    )
    markup = _build_my_deals_keyboard(chunk, page, total_pages, start_index=start, user_id=user_id)
    if message:
        with suppress(TelegramBadRequest):
            await message.edit_text(text, reply_markup=markup)
    elif bot and chat_id is not None:
        await bot.send_message(chat_id, text, reply_markup=markup)


async def _render_deal_detail(
    user_id: int,
    *,
    deal_id: str,
    page: int,
    message: Message | None = None,
) -> None:
    deps = get_deps()
    deal = await deps.deal_service.get_deal(deal_id)
    if not deal or user_id not in {deal.seller_id, deal.buyer_id}:
        if message:
            with suppress(TelegramBadRequest):
                await message.edit_text("Сделка недоступна или уже удалена.", reply_markup=None)
        return
    text = _format_deal_detail(deal, user_id)
    markup = _build_deal_detail_keyboard(deal, page)
    if message:
        with suppress(TelegramBadRequest):
            await message.edit_text(text, reply_markup=markup)


def _build_my_deals_keyboard(
    deals: List[Deal],
    page: int,
    total_pages: int,
    *,
    start_index: int,
    user_id: int,
):
    builder = InlineKeyboardBuilder()
    for index, deal in enumerate(deals, start=start_index + 1):
        builder.row(
            InlineKeyboardButton(
                text=_deal_button_label(deal, user_id, index),
                callback_data=f"{MY_DEALS_VIEW_PREFIX}{page}:{deal.id}",
            )
        )
    if total_pages > 1:
        nav_buttons = []
        if page > 0:
            nav_buttons.append(
                InlineKeyboardButton(
                    text=f"⬅️ Стр. {page}",
                    callback_data=f"{MY_DEALS_PAGE_PREFIX}{page - 1}",
                )
            )
        if page < total_pages - 1:
            nav_buttons.append(
                InlineKeyboardButton(
                    text=f"Стр. {page + 2} ➡️",
                    callback_data=f"{MY_DEALS_PAGE_PREFIX}{page + 1}",
                )
            )
        if nav_buttons:
            builder.row(*nav_buttons)
    builder.row(
        InlineKeyboardButton(
            text="⬅️ Назад",
            callback_data=MenuAction.BACK.value,
        )
    )
    return builder.as_markup()


def _build_deal_detail_keyboard(deal: Deal, page: int):
    builder = InlineKeyboardBuilder()
    actions = []
    if deal.status in {DealStatus.OPEN, DealStatus.RESERVED}:
        actions.append(
            InlineKeyboardButton(
                text="⛔️ Отменить",
                callback_data=f"{DEAL_CANCEL_PREFIX}{page}:{deal.id}",
            )
        )
    if deal.status in {DealStatus.RESERVED, DealStatus.PAID}:
        actions.append(
            InlineKeyboardButton(
                text="✅ Завершить",
                callback_data=f"{DEAL_COMPLETE_PREFIX}{page}:{deal.id}",
            )
        )
    if actions:
        builder.row(*actions)
    builder.row(
        InlineKeyboardButton(
            text="⬅️ К списку",
            callback_data=f"{MY_DEALS_PAGE_PREFIX}{page}",
        )
    )
    builder.row(
        InlineKeyboardButton(
            text="⬅️ Назад",
            callback_data=MenuAction.BACK.value,
        )
    )
    return builder.as_markup()


def _deal_button_label(deal: Deal, user_id: int, index: int) -> str:
    role_icon = "💵" if deal.seller_id == user_id else "🛒"
    short_date = deal.created_at.strftime("%d.%m %H:%M")
    status_tag = STATUS_BUTTON_LABELS.get(deal.status, "")
    return f"{role_icon} #{index} · {deal.public_id} · {short_date} {status_tag}"


def _format_deal_list_text(
    *,
    total: int,
    success: int,
    failed: int,
    page: int,
    total_pages: int,
) -> str:
    lines = [
        "<b>📂 Мои сделки</b>",
        f"Всего: {total}",
        f"Успешных: {success}",
        f"Отменённых/истёкших: {failed}",
        f"Страница {page}/{total_pages}",
    ]
    lines.append("")
    lines.append("Выбери сделку кнопками ниже.")
    return "\n".join(lines)


def _format_deal_detail(deal: Deal, user_id: int) -> str:
    role = "Продавец" if deal.seller_id == user_id else "Покупатель"
    created = deal.created_at.astimezone(timezone.utc).strftime("%d.%m.%Y %H:%M UTC")
    expires = deal.expires_at.astimezone(timezone.utc).strftime("%d.%m.%Y %H:%M UTC")
    buyer = str(deal.buyer_id) if deal.buyer_id else "—"
    payment_status = _payment_status_line(deal)
    lines = [
        f"<b>Сделка {deal.public_id}</b>",
        f"Роль: {role}",
        f"Статус: {STATUS_TITLES.get(deal.status, deal.status.value)}",
        payment_status,
        f"Наличные: {deal.usd_amount} RUB",
        f"USDT к оплате: {deal.usdt_amount}",
        f"Создано: {created}",
        f"Действует до: {expires}",
        f"Покупатель: {buyer}",
    ]
    if deal.invoice_url:
        lines.append(f"Ссылка на оплату: {escape(deal.invoice_url)}")
    if deal.comment:
        lines.append(f"Комментарий: {escape(deal.comment)}")
    return "\n".join(lines)


def _format_profile(profile: UserProfile, deals: List[Deal]) -> str:
    total = len(deals)
    success = sum(1 for deal in deals if deal.status == DealStatus.COMPLETED)
    failed = sum(
        1 for deal in deals if deal.status in {DealStatus.CANCELED, DealStatus.EXPIRED}
    )
    name = escape(profile.full_name) if profile.full_name else "—"
    username_line = (
        f"Юзернейм: {escape('@' + profile.username)}"
        if profile.username
        else "Юзернейм: —"
    )
    registered = profile.registered_at.astimezone(timezone.utc).strftime(
        "%d.%m.%Y %H:%M UTC"
    )
    lines = [
        "<b>👤 Мой профиль</b>",
        "──────────────",
        f"Имя: {name}",
        username_line,
        f"ID: {profile.user_id}",
        f"Дата регистрации: {registered}",
        "",
        f"Сделок всего: {total}",
        f"Успешных: {success} ({_percent(success, total)})",
        f"Неуспешных: {failed} ({_percent(failed, total)})",
        "Отзывы: 0% (пока нет отзывов)",
    ]
    return "\n".join(lines)


def _percent(part: int, total: int) -> str:
    if total == 0:
        return "0%"
    value = round(part * 100 / total, 1)
    return f"{value}%"


def _payment_status_line(deal: Deal) -> str:
    if deal.status in {DealStatus.PAID, DealStatus.COMPLETED}:
        return "Статус оплаты: 💰 Оплачено"
    if deal.status == DealStatus.RESERVED:
        return "Статус оплаты: ⏳ Ожидаем оплату"
    return "Статус оплаты: 🟡 Не оплачено"


async def _cancel_deal_core(user_id: int, deal_id: str) -> Deal:
    deps = get_deps()
    return await deps.deal_service.cancel_deal(deal_id, user_id)


async def _complete_deal_core(user_id: int, deal_id: str, bot) -> Deal:
    deps = get_deps()
    deal = await deps.deal_service.complete_deal(deal_id, user_id)
    if deal.buyer_id:
        await bot.send_message(deal.buyer_id, f"Сделка {deal.public_id} закрыта продавцом")
    return deal


def _back_only_markup() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="⬅️ Назад", callback_data=MenuAction.BACK.value)
    builder.adjust(1)
    return builder.as_markup()


async def _delete_callback_message(callback: CallbackQuery) -> None:
    message = callback.message
    if not message:
        return
    with suppress(TelegramBadRequest):
        await message.delete()


async def _send_admin_panel(chat_id: int, bot) -> None:
    builder = InlineKeyboardBuilder()
    builder.button(text="👔 Мерчанты", callback_data=ADMIN_PANEL_MERCHANTS)
    builder.button(text="📥 Заявки", callback_data=ADMIN_PANEL_APPS)
    builder.button(text="💹 Управление ценой", callback_data=ADMIN_PANEL_RATES)
    builder.button(text="⬅️ Меню", callback_data=MenuAction.BACK.value)
    builder.adjust(1)
    await bot.send_message(
        chat_id,
        "Выбери раздел админ-панели:",
        reply_markup=builder.as_markup(),
    )


async def _send_applications_list(chat_id: int, bot) -> None:
    deps = get_deps()
    applications = await deps.user_service.list_applications()
    if not applications:
        await bot.send_message(
            chat_id,
            "Заявок пока нет",
            reply_markup=_admin_panel_back_markup(),
        )
        return
    keyboard = InlineKeyboardBuilder()
    for app in applications:
        label = f"@{app.username}" if app.username else str(app.user_id)
        keyboard.button(text=label, callback_data=f"{APP_VIEW_PREFIX}{app.id}")
    keyboard.button(text="⬅️ Админ панель", callback_data=ADMIN_PANEL_MENU)
    keyboard.adjust(1)
    await bot.send_message(
        chat_id,
        "Выбери заявку для просмотра:",
        reply_markup=keyboard.as_markup(),
    )


async def _send_merchants_list(chat_id: int, bot) -> None:
    deps = get_deps()
    merchants = await deps.user_service.list_merchants()
    if not merchants:
        await bot.send_message(
            chat_id,
            "Мерчантов пока нет",
            reply_markup=_admin_panel_back_markup(),
        )
        return
    builder = InlineKeyboardBuilder()
    for record in merchants:
        builder.button(
            text=_merchant_button_label(record),
            callback_data=f"{ADMIN_MERCHANT_VIEW_PREFIX}{record.user_id}",
        )
    builder.button(text="⬅️ Админ панель", callback_data=ADMIN_PANEL_MENU)
    builder.adjust(1)
    await bot.send_message(
        chat_id,
        "Выбери мерчанта:",
        reply_markup=builder.as_markup(),
    )


async def _send_merchant_detail(callback: CallbackQuery, merchant_id: int) -> None:
    deps = get_deps()
    profile = await deps.user_service.profile_of(merchant_id)
    since = await deps.user_service.merchant_since_of(merchant_id)
    deals = await deps.deal_service.list_user_deals(merchant_id)
    text = _format_merchant_summary(merchant_id, profile, since, deals)
    builder = InlineKeyboardBuilder()
    builder.button(
        text="📂 Сделки",
        callback_data=f"{ADMIN_MERCHANT_DEALS_PREFIX}{merchant_id}",
    )
    builder.button(
        text="🚫 Исключить",
        callback_data=f"{ADMIN_MERCHANT_EXCLUDE_PREFIX}{merchant_id}",
    )
    builder.button(text="⬅️ К списку", callback_data=ADMIN_PANEL_MERCHANTS)
    builder.button(text="⬅️ Админ панель", callback_data=ADMIN_PANEL_MENU)
    with suppress(TelegramBadRequest):
        await callback.message.delete()
    await callback.bot.send_message(
        callback.message.chat.id,
        text,
        reply_markup=builder.as_markup(),
    )


async def _send_merchant_deals(callback: CallbackQuery, merchant_id: int) -> None:
    deps = get_deps()
    deals = await deps.deal_service.list_user_deals(merchant_id)
    text = _format_merchant_deals_text(merchant_id, deals)
    builder = InlineKeyboardBuilder()
    builder.button(
        text="⬅️ К профилю",
        callback_data=f"{ADMIN_MERCHANT_VIEW_PREFIX}{merchant_id}",
    )
    builder.button(text="⬅️ Админ панель", callback_data=ADMIN_PANEL_MENU)
    with suppress(TelegramBadRequest):
        await callback.message.delete()
    await callback.message.answer(text, reply_markup=builder.as_markup())


def _merchant_button_label(record: MerchantRecord) -> str:
    if record.profile and record.profile.username:
        return f"@{record.profile.username}"
    if record.profile and record.profile.full_name:
        return record.profile.full_name
    return str(record.user_id)


def _format_merchant_summary(
    user_id: int,
    profile: UserProfile | None,
    merchant_since: datetime | None,
    deals: List[Deal],
) -> str:
    name = escape(profile.full_name) if profile and profile.full_name else "—"
    username = (
        f"@{profile.username}"
        if profile and profile.username
        else "—"
    )
    since_text = (
        merchant_since.astimezone(timezone.utc).strftime("%d.%m.%Y %H:%M UTC")
        if merchant_since
        else "—"
    )
    total = len(deals)
    success = sum(1 for deal in deals if deal.status == DealStatus.COMPLETED)
    failed = sum(
        1 for deal in deals if deal.status in {DealStatus.CANCELED, DealStatus.EXPIRED}
    )
    lines = [
        "<b>👔 Мерчант</b>",
        f"Имя: {name}",
        f"Юзернейм: {escape(username)}",
        f"ID: {user_id}",
        f"Мерчант с: {since_text}",
        "",
        f"Сделок всего: {total}",
        f"Успешных: {success}",
        f"Отменённых/истёкших: {failed}",
    ]
    return "\n".join(lines)


def _format_merchant_deals_text(user_id: int, deals: List[Deal]) -> str:
    if not deals:
        return f"У пользователя {user_id} пока нет сделок."
    lines = [f"<b>Сделки мерчанта {user_id}</b>"]
    for idx, deal in enumerate(deals, 1):
        status = STATUS_TITLES.get(deal.status, deal.status.value)
        created = deal.created_at.astimezone(timezone.utc).strftime("%d.%m.%Y %H:%M UTC")
        buyer = deal.buyer_id or "—"
        lines.extend(
            [
                f"{idx}. {deal.public_id} — {status}",
                f"   Наличные: {deal.usd_amount} RUB | USDT: {deal.usdt_amount}",
                f"   Продавец: {deal.seller_id} | Покупатель: {buyer}",
                f"   Создано: {created}",
            ]
        )
        if deal.invoice_url:
            lines.append(f"   Invoice: {escape(deal.invoice_url)}")
    return "\n".join(lines)


def _admin_panel_back_markup() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="⬅️ Админ панель", callback_data=ADMIN_PANEL_MENU)
    builder.adjust(1)
    return builder.as_markup()


def _format_application(application: MerchantApplication) -> str:
    banks = ", ".join(BANK_OPTIONS.get(bank, bank) for bank in application.banks) or "-"
    username = f"@{application.username}" if application.username else "-"
    uses_personal = "Да" if application.uses_personal_bank else "Нет"
    accepts_risk = "Да" if application.accepts_risk else "Нет"
    created = application.created_at.astimezone(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    status_map = {
        ApplicationStatus.PENDING: "Новая",
        ApplicationStatus.ACCEPTED: "Одобрена",
        ApplicationStatus.REJECTED: "Отклонена",
    }
    status = status_map.get(application.status, application.status.value)
    return (
        f"Заявка #{application.id}\n"
        f"Пользователь: {application.user_id} {username}\n"
        f"Банки: {banks}\n"
        f"Личные банки: {uses_personal}\n"
        f"Берёт риск: {accepts_risk}\n"
        f"Статус: {status}\n"
        f"Создано: {created}"
    )
@router.message(AdminRateState.waiting_rate)
async def admin_rate_input(message: Message, state: FSMContext) -> None:
    deps = get_deps()
    user = message.from_user
    if not user or user.id not in deps.config.admin_ids:
        await message.answer("Нет доступа.")
        await state.clear()
        return
    text = (message.text or "").strip()
    if text.lower() == "отмена":
        await state.clear()
        await message.answer("Изменение курса отменено.")
        return
    try:
        value = Decimal(text.replace(",", "."))
    except Exception:
        await message.answer("Не смог распознать число, попробуй снова.")
        return
    if value <= 0:
        await message.answer("Курс должен быть больше 0.")
        return
    snapshot = await deps.rate_provider.set_rate(usd_rate=value, fee_percent=None)
    await state.clear()
    await message.answer(
        f"Курс обновлён: 1 USDT = {snapshot.usd_rate} RUB\nКомиссия: {snapshot.fee_percent}%",
    )


@router.message(AdminRateState.waiting_fee)
async def admin_fee_input(message: Message, state: FSMContext) -> None:
    deps = get_deps()
    user = message.from_user
    if not user or user.id not in deps.config.admin_ids:
        await message.answer("Нет доступа.")
        await state.clear()
        return
    text = (message.text or "").strip()
    if text.lower() == "отмена":
        await state.clear()
        await message.answer("Изменение комиссии отменено.")
        return
    try:
        value = Decimal(text.replace(",", "."))
    except Exception:
        await message.answer("Не смог распознать число, попробуй снова.")
        return
    if value < 0:
        await message.answer("Комиссия не может быть отрицательной.")
        return
    snapshot = await deps.rate_provider.set_rate(usd_rate=None, fee_percent=value)
    await state.clear()
    await message.answer(
        f"Комиссия обновлена: {snapshot.fee_percent}%\nКурс: 1 USDT = {snapshot.usd_rate} RUB",
    )
