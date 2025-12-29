from __future__ import annotations

from decimal import Decimal
from contextlib import suppress
from datetime import timezone
from html import escape

from aiogram import F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from cachebot.deps import get_deps
from cachebot.keyboards import MenuAction
from cachebot.models.deal import Deal, DealStatus
from cachebot.models.user import UserRole, UserProfile

router = Router(name="deals")

SELL_MODE_USDT = "sell_mode:usdt"
SELL_MODE_RUB = "sell_mode:rub"
SELL_EDIT_AMOUNT = "sell_edit"
OPEN_DEALS_SORT_PREFIX = "open_deals_sort:"
OPEN_DEALS_VIEW_PREFIX = "open_deal_view:"
OPEN_DEALS_BACK_PREFIX = "open_deal_back:"
DEFAULT_DEALS_ORDER = "desc"
MAX_DEAL_BUTTONS = 10


class SellStates(StatesGroup):
    waiting_amount = State()
    confirm = State()


@router.message(Command("sell"))
async def sell_entry(message: Message, state: FSMContext) -> None:
    if not message.from_user:
        await message.answer("Команда доступна только в личном чате")
        return
    deps = get_deps()
    await deps.user_service.ensure_profile(
        message.from_user.id,
        full_name=message.from_user.full_name,
        username=message.from_user.username,
    )
    role = await deps.user_service.role_of(message.from_user.id)
    if role != UserRole.SELLER:
        await message.answer("Создание сделок доступно только продавцам.")
        return
    await state.set_state(SellStates.waiting_amount)
    await state.update_data(input_mode="usdt")
    await _send_sell_prompt(message.chat.id, message.bot, mode="usdt")


@router.callback_query(F.data == MenuAction.SELL.value)
async def sell_from_menu(callback: CallbackQuery, state: FSMContext) -> None:
    deps = get_deps()
    user = callback.from_user
    if not user:
        await callback.answer()
        return
    role = await deps.user_service.role_of(user.id)
    await deps.user_service.ensure_profile(
        user.id,
        full_name=user.full_name,
        username=user.username,
    )
    if role != UserRole.SELLER:
        await callback.answer("Создание сделок доступно только продавцам", show_alert=True)
        return
    await state.set_state(SellStates.waiting_amount)
    await state.update_data(input_mode="usdt")
    await _delete_callback_message(callback)
    await _send_sell_prompt(callback.message.chat.id, callback.bot, mode="usdt")
    await callback.answer()


@router.message(SellStates.waiting_amount)
async def sell_amount(message: Message, state: FSMContext) -> None:
    if not message.from_user:
        await message.answer("Команда доступна только в личном чате")
        return
    data = await state.get_data()
    mode = data.get("input_mode", "usdt")
    try:
        raw_amount = Decimal(message.text.replace(",", "."))
    except Exception:
        await message.answer("Не смог распознать число, попробуй еще раз.")
        return
    if raw_amount <= 0:
        await message.answer("Сумма должна быть больше 0.")
        return
    deps = get_deps()
    await deps.user_service.ensure_profile(
        message.from_user.id,
        full_name=message.from_user.full_name,
        username=message.from_user.username,
    )
    snapshot = await deps.rate_provider.snapshot()
    if mode == "usdt":
        cash_amount = snapshot.cash_amount(raw_amount)
        note = f"Введено: {raw_amount} USDT"
    else:
        cash_amount = raw_amount
        note = f"Введено: {raw_amount} RUB"
    if cash_amount <= 0:
        await message.answer("Сумма должна быть больше 0.")
        return
    total_usdt = snapshot.usdt_amount(cash_amount)
    summary = _format_sell_summary(
        cash_amount=cash_amount,
        usdt_amount=total_usdt,
        snapshot=snapshot,
        note=note,
    )
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Создать", callback_data="sell_confirm")
    builder.button(text="✏️ Изменить сумму", callback_data=SELL_EDIT_AMOUNT)
    builder.button(text="❌ Отмена", callback_data="sell_cancel")
    builder.adjust(1, 2)
    await state.update_data(
        usd_amount=str(cash_amount),
        total_usdt=str(total_usdt),
        input_mode=mode,
    )
    await message.answer(summary, reply_markup=builder.as_markup())
    await state.set_state(SellStates.confirm)


@router.callback_query(F.data == "sell_confirm", SellStates.confirm)
async def sell_confirm(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()
    data = await state.get_data()
    amount = Decimal(data["usd_amount"])
    deps = get_deps()
    deal = await deps.deal_service.create_deal(callback.from_user.id, amount)
    await state.clear()
    await callback.message.answer(
        f"✅ Сделка создана\nID: {deal.public_id}\n"
        f"Наличные: {deal.usd_amount} RUB\n"
        f"USDT к оплате: {deal.usdt_amount}\nОжидаем покупателя."
    )


@router.callback_query(F.data == "sell_cancel", SellStates.confirm)
async def sell_cancel(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer("Отменено")
    await state.clear()
    await callback.message.answer("Создание сделки отменено")


@router.callback_query(F.data == SELL_EDIT_AMOUNT, SellStates.confirm)
async def sell_edit_amount(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    mode = data.get("input_mode", "usdt")
    await state.set_state(SellStates.waiting_amount)
    await callback.answer("Измени сумму")
    await callback.message.edit_text(
        _sell_prompt_text(mode),
        reply_markup=_sell_prompt_keyboard(mode),
    )


@router.message(Command("deals"))
async def list_deals(message: Message) -> None:
    if not message.from_user:
        return
    deps = get_deps()
    await deps.user_service.ensure_profile(
        message.from_user.id,
        full_name=message.from_user.full_name,
        username=message.from_user.username,
    )
    await _send_open_deals(
        message.from_user.id,
        message.chat.id,
        message.bot,
        order=DEFAULT_DEALS_ORDER,
    )


@router.callback_query(F.data == SELL_MODE_USDT, SellStates.waiting_amount)
async def switch_mode_usdt(callback: CallbackQuery, state: FSMContext) -> None:
    await state.update_data(input_mode="usdt")
    await callback.message.edit_text(
        _sell_prompt_text("usdt"),
        reply_markup=_sell_prompt_keyboard("usdt"),
    )
    await callback.answer("Ввод в USDT")


@router.callback_query(F.data == SELL_MODE_RUB, SellStates.waiting_amount)
async def switch_mode_rub(callback: CallbackQuery, state: FSMContext) -> None:
    await state.update_data(input_mode="rub")
    await callback.message.edit_text(
        _sell_prompt_text("rub"),
        reply_markup=_sell_prompt_keyboard("rub"),
    )
    await callback.answer("Ввод в рублях")


@router.callback_query(F.data.startswith("deal_accept:"))
async def accept(callback: CallbackQuery) -> None:
    deps = get_deps()
    role = await deps.user_service.role_of(callback.from_user.id)
    if role != UserRole.BUYER:
        await callback.answer("Только мерчанты могут брать сделки", show_alert=True)
        return
    deal_id = callback.data.split(":", 1)[1]
    try:
        deal = await deps.deal_service.accept_deal(deal_id, callback.from_user.id)
    except Exception as exc:
        await callback.answer(str(exc), show_alert=True)
        return
    try:
        invoice = await deps.crypto_pay.create_invoice(
            amount=deal.usdt_amount,
            currency="USDT",
            description=f"Сделка {deal.public_id} на {deal.usd_amount} RUB",
            payload=deal.id,
        )
    except Exception as exc:
        await deps.deal_service.release_deal(deal.id)
        await callback.answer(f"Не удалось создать счет: {exc}", show_alert=True)
        return
    await deps.deal_service.attach_invoice(deal.id, invoice.invoice_id, invoice.pay_url)
    await callback.answer()
    await callback.message.answer(
        f"✅ Сделка {deal.public_id} закреплена за тобой.\n"
        f"Оплати {invoice.amount} {invoice.currency} через Crypto Pay:\n{invoice.pay_url}\n"
        f"У тебя есть {deps.config.payment_window_minutes} минут."
    )
    await callback.bot.send_message(
        deal.seller_id,
        f"Покупатель @%s взял сделку {deal.public_id}. Ожидаем оплату через Crypto Pay."
        % (callback.from_user.username or callback.from_user.id),
    )


@router.callback_query(F.data == MenuAction.OPEN_DEALS.value)
async def open_deals_from_menu(callback: CallbackQuery) -> None:
    user = callback.from_user
    if not user:
        await callback.answer()
        return
    deps = get_deps()
    await deps.user_service.ensure_profile(
        user.id,
        full_name=user.full_name,
        username=user.username,
    )
    has_list = await _send_open_deals(
        user.id,
        callback.message.chat.id,
        callback.bot,
        order=DEFAULT_DEALS_ORDER,
    )
    if has_list:
        await _delete_callback_message(callback)
    await callback.answer()


@router.callback_query(F.data.startswith(OPEN_DEALS_SORT_PREFIX))
async def open_deals_sort(callback: CallbackQuery) -> None:
    user = callback.from_user
    if not user:
        await callback.answer()
        return
    order = callback.data.split(":", 1)[1]
    if order not in {"asc", "desc"}:
        await callback.answer()
        return
    deps = get_deps()
    role = await deps.user_service.role_of(user.id)
    if role != UserRole.BUYER:
        await callback.answer("Нет доступа к сделкам", show_alert=True)
        return
    await deps.user_service.ensure_profile(
        user.id,
        full_name=user.full_name,
        username=user.username,
    )
    payload = await _build_open_deals_payload(user.id, order)
    message = callback.message
    if not payload:
        if message:
            await message.edit_text("Нет доступных сделок")
        await callback.answer("Нет доступных сделок", show_alert=True)
        return
    text, markup = payload
    if message:
        with suppress(TelegramBadRequest):
            await message.edit_text(text, reply_markup=markup)
    await callback.answer("Сортировка обновлена")


@router.callback_query(F.data.startswith(OPEN_DEALS_VIEW_PREFIX))
async def open_deals_view(callback: CallbackQuery) -> None:
    user = callback.from_user
    if not user:
        await callback.answer()
        return
    parts = callback.data.split(":")
    if len(parts) < 2:
        await callback.answer()
        return
    deal_id = parts[1]
    order = parts[2] if len(parts) > 2 else DEFAULT_DEALS_ORDER
    deps = get_deps()
    role = await deps.user_service.role_of(user.id)
    if role != UserRole.BUYER:
        await callback.answer("Нет доступа к сделкам", show_alert=True)
        return
    await deps.user_service.ensure_profile(
        user.id,
        full_name=user.full_name,
        username=user.username,
    )
    deal = await deps.deal_service.get_deal(deal_id)
    if not deal or deal.status != DealStatus.OPEN:
        await callback.answer("Сделка недоступна", show_alert=True)
        payload = await _build_open_deals_payload(user.id, DEFAULT_DEALS_ORDER)
        if payload and callback.message:
            text, markup = payload
            with suppress(TelegramBadRequest):
                await callback.message.edit_text(text, reply_markup=markup)
        return
    profile = await deps.user_service.profile_of(deal.seller_id)
    text = _format_deal_detail(deal, profile)
    builder = InlineKeyboardBuilder()
    profile_url = _profile_url(profile, deal.seller_id)
    if profile_url:
        builder.button(text="👤 Профиль продавца", url=profile_url)
    builder.row(
        InlineKeyboardButton(text="✅ Взять сделку", callback_data=f"deal_accept:{deal.id}"),
        InlineKeyboardButton(
            text="⬅️ Назад к списку", callback_data=f"{OPEN_DEALS_BACK_PREFIX}{order}"
        ),
    )
    if callback.message:
        with suppress(TelegramBadRequest):
            await callback.message.edit_text(text, reply_markup=builder.as_markup())
    await callback.answer()


@router.callback_query(F.data.startswith(OPEN_DEALS_BACK_PREFIX))
async def open_deals_back(callback: CallbackQuery) -> None:
    user = callback.from_user
    if not user:
        await callback.answer()
        return
    order = callback.data.split(":", 1)[1] if ":" in callback.data else DEFAULT_DEALS_ORDER
    deps = get_deps()
    role = await deps.user_service.role_of(user.id)
    if role != UserRole.BUYER:
        await callback.answer("Нет доступа к сделкам", show_alert=True)
        return
    await deps.user_service.ensure_profile(
        user.id,
        full_name=user.full_name,
        username=user.username,
    )
    payload = await _build_open_deals_payload(user.id, order)
    message = callback.message
    if not payload:
        if message:
            with suppress(TelegramBadRequest):
                await message.edit_text("Нет доступных сделок")
        await callback.answer("Нет доступных сделок", show_alert=True)
        return
    text, markup = payload
    if message:
        with suppress(TelegramBadRequest):
            await message.edit_text(text, reply_markup=markup)
    await callback.answer()


@router.message(Command("cancel"))
async def cancel_command(message: Message) -> None:
    if not message.from_user:
        await message.answer("Команда доступна только в личном чате")
        return
    deal_id = _command_arg(message)
    if not deal_id:
        await message.answer("Укажи ID сделки")
        return
    await _cancel_deal(message, deal_id)


@router.message(Command("complete"))
async def complete_command(message: Message) -> None:
    if not message.from_user:
        await message.answer("Команда доступна только в личном чате")
        return
    deal_id = _command_arg(message)
    if not deal_id:
        await message.answer("Укажи ID сделки")
        return
    await _complete_deal(message, deal_id)


async def _send_open_deals(user_id: int, chat_id: int, bot, *, order: str) -> bool:
    deps = get_deps()
    role = await deps.user_service.role_of(user_id)
    if role != UserRole.BUYER:
        await bot.send_message(chat_id, "Список сделок доступен только мерчантам.")
        return False
    deals = await deps.deal_service.list_open_deals()
    payload = _build_open_deals_markup(deals, order)
    if not payload:
        await bot.send_message(chat_id, "Нет доступных сделок")
        return False
    text, markup = payload
    await bot.send_message(chat_id, text, reply_markup=markup)
    return True


def _command_arg(message: Message) -> str:
    if not message.text:
        return ""
    parts = message.text.split(maxsplit=1)
    return parts[1].strip() if len(parts) > 1 else ""


async def _build_open_deals_payload(user_id: int, order: str):
    deps = get_deps()
    deals = await deps.deal_service.list_open_deals()
    return _build_open_deals_markup(deals, order)


def _build_open_deals_markup(deals: list[Deal], order: str):
    if not deals:
        return None
    reverse = order != "asc"
    sorted_deals = sorted(
        deals,
        key=lambda deal: (deal.usd_amount, deal.created_at),
        reverse=reverse,
    )
    visible = sorted_deals[:MAX_DEAL_BUTTONS]
    builder = InlineKeyboardBuilder()
    for deal in visible:
        builder.button(
            text=_open_deal_button_label(deal),
            callback_data=f"{OPEN_DEALS_VIEW_PREFIX}{deal.id}:{order}",
        )
    if visible:
        builder.adjust(1)
    asc_label = "🔼 Сумма ✅" if order == "asc" else "🔼 Сумма"
    desc_label = "🔽 Сумма ✅" if order == "desc" else "🔽 Сумма"
    builder.row(
        InlineKeyboardButton(
            text=asc_label,
            callback_data=f"{OPEN_DEALS_SORT_PREFIX}asc",
        ),
        InlineKeyboardButton(
            text=desc_label,
            callback_data=f"{OPEN_DEALS_SORT_PREFIX}desc",
        ),
    )
    builder.row(InlineKeyboardButton(text="⬅️ Назад", callback_data=MenuAction.BACK.value))
    text = _format_open_deals_text(total=len(deals), order=order)
    return text, builder.as_markup()


def _format_open_deals_text(*, total: int, order: str) -> str:
    order_text = "по возрастанию" if order == "asc" else "по убыванию"
    lines = [
        "<b>📋 Доступные сделки</b>",
        f"Всего: {total}",
        f"Сортировка: {order_text}",
        "",
        "Выбери сделку кнопками ниже.",
    ]
    if total > MAX_DEAL_BUTTONS:
        lines.append(f"Показаны первые {MAX_DEAL_BUTTONS} предложений.")
    return "\n".join(lines)


def _open_deal_button_label(deal: Deal) -> str:
    rub_amount = _format_decimal(deal.usd_amount)
    usdt_amount = _format_decimal(deal.usdt_amount)
    created = deal.created_at.astimezone(timezone.utc).strftime("%d.%m %H:%M")
    return f"₽{rub_amount} | {usdt_amount} USDT • {created}"


def _format_decimal(value: Decimal) -> str:
    quantized = value.quantize(Decimal("0.01"))
    text = format(quantized, "f")
    if "." in text:
        text = text.rstrip("0").rstrip(".")
    return text or "0"


def _format_deal_detail(deal: Deal, profile: UserProfile | None) -> str:
    rub_amount = _format_decimal(deal.usd_amount)
    usdt_amount = _format_decimal(deal.usdt_amount)
    rate = _format_decimal(deal.rate)
    created = deal.created_at.astimezone(timezone.utc).strftime("%d.%m.%Y %H:%M UTC")
    expires = deal.expires_at.astimezone(timezone.utc).strftime("%d.%m.%Y %H:%M UTC")
    payment_status = _format_payment_status(deal)
    name = escape(profile.full_name) if profile and profile.full_name else "—"
    username_link = _profile_link_text(profile, deal.seller_id)
    last_seen = _format_last_seen(profile)
    lines = [
        f"<b>Сделка {deal.public_id}</b>",
        f"Наличные: ₽{rub_amount}",
        f"USDT к оплате: {usdt_amount} USDT",
        f"Курс: 1 USDT = {rate} RUB",
        f"Комиссия: {deal.fee_percent}%",
        f"Создано: {created}",
        f"Действует до: {expires}",
        f"Статус оплаты: {payment_status}",
        "",
        "<b>Продавец</b>",
        f"Имя: {name}",
        f"Юзер: {username_link}",
        f"ID: {deal.seller_id}",
        f"Последний онлайн: {last_seen}",
    ]
    if deal.comment:
        lines.append("")
        lines.append(f"Комментарий: {escape(deal.comment)}")
    return "\n".join(lines)


def _profile_link_text(profile: UserProfile | None, user_id: int) -> str:
    if profile and profile.username:
        username = profile.username.lstrip("@")
        safe_username = escape(username)
        return f'<a href="https://t.me/{safe_username}">@{safe_username}</a>'
    return f'<a href="tg://user?id={user_id}">tg://user?id={user_id}</a>'


def _profile_url(profile: UserProfile | None, user_id: int) -> str | None:
    if profile and profile.username:
        return f"https://t.me/{profile.username.lstrip('@')}"
    return f"tg://user?id={user_id}"


def _format_last_seen(profile: UserProfile | None) -> str:
    if not profile or not profile.last_seen_at:
        return "нет данных"
    return profile.last_seen_at.astimezone(timezone.utc).strftime("%d.%m.%Y %H:%M UTC")


def _format_payment_status(deal: Deal) -> str:
    if deal.status in {DealStatus.PAID, DealStatus.COMPLETED}:
        return "💰 Оплачено"
    if deal.status == DealStatus.RESERVED:
        return "⏳ Ожидаем оплату"
    return "🟡 Не оплачено"


async def _cancel_deal(message: Message, deal_id: str) -> None:
    deps = get_deps()
    try:
        deal = await deps.deal_service.cancel_deal(deal_id, message.from_user.id)
    except Exception as exc:
        await message.answer(f"Не удалось отменить: {exc}")
        return
    await message.answer(f"Сделка {deal.public_id} отменена")


async def _complete_deal(message: Message, deal_id: str) -> None:
    deps = get_deps()
    try:
        deal = await deps.deal_service.complete_deal(deal_id, message.from_user.id)
    except Exception as exc:
        await message.answer(f"Не получилось: {exc}")
        return
    await message.answer(f"Сделка {deal.public_id} завершена")
    if deal.buyer_id:
        await message.bot.send_message(deal.buyer_id, f"Сделка {deal.public_id} закрыта продавцом")


async def _delete_callback_message(callback: CallbackQuery) -> None:
    message = callback.message
    if not message:
        return
    with suppress(TelegramBadRequest):
        await message.delete()


async def _send_sell_prompt(chat_id: int, bot, *, mode: str) -> None:
    await bot.send_message(
        chat_id,
        _sell_prompt_text(mode),
        reply_markup=_sell_prompt_keyboard(mode),
    )


def _sell_prompt_text(mode: str) -> str:
    if mode == "rub":
        return (
            "<b>💰 Ввод суммы</b>\n"
            "Укажи сумму в рублях, которую хочешь получить наличными.\n"
            "Нажми кнопку ниже, чтобы вводить в USDT."
        )
    return (
        "<b>💰 Ввод суммы</b>\n"
        "Укажи сумму в USDT для обмена на наличные.\n"
        "Нажми кнопку ниже, чтобы вводить в рублях."
    )


def _sell_prompt_keyboard(mode: str):
    builder = InlineKeyboardBuilder()
    if mode == "rub":
        builder.button(text="Ввести в USDT", callback_data=SELL_MODE_USDT)
    else:
        builder.button(text="Указать в рублях", callback_data=SELL_MODE_RUB)
    builder.adjust(1)
    return builder.as_markup()


def _format_sell_summary(*, cash_amount: Decimal, usdt_amount: Decimal, snapshot, note: str) -> str:
    return (
        "<b>📄 Предпросмотр сделки</b>\n"
        f"{note}\n"
        f"💵 Наличные: {cash_amount} RUB\n"
        f"💱 Курс: 1 USDT = {snapshot.usd_rate} RUB\n"
        f"⚖️ Комиссия: {snapshot.fee_percent}%\n"
        f"🪙 К оплате: {usdt_amount} USDT"
    )
