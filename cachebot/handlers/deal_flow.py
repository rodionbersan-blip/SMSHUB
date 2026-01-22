from __future__ import annotations

from decimal import Decimal, ROUND_UP
from contextlib import suppress
from datetime import datetime, timezone
from html import escape

from aiogram import F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from cachebot.constants import (
    PROFILE_VIEW_PREFIX,
    bank_label,
    QR_REQUEST_PREFIX,
    QR_VIEW_PREFIX,
    QR_SELLER_ATTACH_PREFIX,
    QR_SELLER_READY_PREFIX,
    QR_BUYER_DONE_PREFIX,
    QR_SELLER_DONE_PREFIX,
)
from cachebot.deps import get_deps
from cachebot.keyboards import MenuAction
from cachebot.models.deal import Deal, DealStatus, QrStage
from cachebot.models.dispute import Dispute
from cachebot.models.review import Review
from cachebot.models.user import UserRole, UserProfile

router = Router(name="deals")

SELL_MODE_USDT = "sell_mode:usdt"
SELL_MODE_RUB = "sell_mode:rub"
SELL_EDIT_AMOUNT = "sell_edit"
OPEN_DEALS_SORT_PREFIX = "open_deals_sort:"
OPEN_DEALS_VIEW_PREFIX = "open_deal_view:"
OPEN_DEALS_BACK_PREFIX = "open_deal_back:"
DEAL_INFO_PREFIX = "deal_info:"
MESSAGE_DEAL_PREFIX = "deal_message:"
DEAL_CANCEL_PREFIX = "dealact:cancel:"
MY_DEALS_PAGE_PREFIX = "mydeals:page:"
REVIEW_START_PREFIX = "review:start:"
DISPUTE_OPEN_PREFIX = "dispute:open:"
DISPUTE_APPEND_PREFIX = "dispute:append:"
DEFAULT_DEALS_ORDER = "desc"
MAX_DEAL_BUTTONS = 10

class SellStates(StatesGroup):
    waiting_amount = State()
    confirm = State()


class MessageRelayState(StatesGroup):
    waiting_text = State()


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
    await _send_sell_prompt(message.chat.id, message.bot, mode="usdt", state=state)


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
    await _send_sell_prompt(callback.message.chat.id, callback.bot, mode="usdt", state=state)
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
        cash_amount = raw_amount * snapshot.usd_rate
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
    builder.button(text="✅ Продать", callback_data="sell_confirm")
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
    chat_id = callback.message.chat.id if callback.message else callback.from_user.id
    await callback.answer()
    with suppress(TelegramBadRequest):
        if callback.message:
            await callback.message.delete()
    data = await state.get_data()
    amount = Decimal(data["usd_amount"])
    deps = get_deps()
    deal = await deps.deal_service.create_deal(callback.from_user.id, amount)
    await state.clear()
    builder = InlineKeyboardBuilder()
    builder.button(text="К сделке", callback_data=f"{DEAL_INFO_PREFIX}{deal.id}")
    rub_text = _format_decimal(deal.usd_amount)
    usdt_text = _format_decimal(deal.usdt_amount)
    await callback.bot.send_message(
        chat_id,
        f"✅ Сделка {deal.hashtag} создана.\n"
        f"Наличные: ₽{rub_text}\n"
        f"USDT к оплате: {usdt_text} USDT\n"
        "Ожидаем покупателя.",
        reply_markup=builder.as_markup(),
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
    await callback.answer()
    chat_id = callback.message.chat.id if callback.message else callback.from_user.id
    await _delete_callback_message(callback)
    info_builder = InlineKeyboardBuilder()
    info_builder.button(text="К сделке", callback_data=f"{DEAL_INFO_PREFIX}{deal.id}")
    await callback.bot.send_message(
        chat_id,
        f"Сделка {deal.hashtag} закреплена. Оплата подтверждена.",
        reply_markup=info_builder.as_markup(),
    )
    buyer_profile = await deps.user_service.ensure_profile(
        callback.from_user.id,
        full_name=callback.from_user.full_name,
        username=callback.from_user.username,
    )
    buyer_name = buyer_profile.full_name or buyer_profile.username or "Мерчант"
    builder = InlineKeyboardBuilder()
    builder.button(text="К сделке", callback_data=f"{DEAL_INFO_PREFIX}{deal.id}")
    await callback.bot.send_message(
        deal.seller_id,
        f"Покупатель {buyer_name} взял сделку {deal.hashtag}. Оплата подтверждена.",
        reply_markup=builder.as_markup(),
    )


@router.callback_query(F.data == MenuAction.OPEN_DEALS.value)
async def open_deals_from_menu(callback: CallbackQuery, state: FSMContext) -> None:
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
        state=state,
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
    seller_profile = await deps.user_service.profile_of(deal.seller_id)
    buyer_profile = (
        await deps.user_service.profile_of(deal.buyer_id) if deal.buyer_id else None
    )
    chat_id = callback.message.chat.id if callback.message else user.id
    await _delete_callback_message(callback)
    await _send_deal_card(
        bot=callback.bot,
        chat_id=chat_id,
        deal=deal,
        viewer_id=user.id,
        seller_profile=seller_profile,
        buyer_profile=buyer_profile,
        back_page=None,
        cancel_page=0,
        compact=True,
    )
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


@router.callback_query(F.data.startswith(DEAL_INFO_PREFIX))
async def show_deal_info(callback: CallbackQuery) -> None:
    user = callback.from_user
    if not user:
        await callback.answer()
        return
    deal_id = callback.data[len(DEAL_INFO_PREFIX) :]
    deps = get_deps()
    await deps.user_service.ensure_profile(
        user.id,
        full_name=user.full_name,
        username=user.username,
    )
    deal = await deps.deal_service.get_deal(deal_id)
    if not deal:
        await callback.answer("Сделка не найдена", show_alert=True)
        return
    if user.id not in {deal.seller_id, deal.buyer_id} and user.id not in deps.config.admin_ids:
        await callback.answer("Нет доступа", show_alert=True)
        return
    seller_profile = await deps.user_service.profile_of(deal.seller_id)
    buyer_profile = (
        await deps.user_service.profile_of(deal.buyer_id) if deal.buyer_id else None
    )
    chat_id = callback.message.chat.id if callback.message else user.id
    await _delete_callback_message(callback)
    await _send_deal_card(
        bot=callback.bot,
        chat_id=chat_id,
        deal=deal,
        viewer_id=user.id,
        seller_profile=seller_profile,
        buyer_profile=buyer_profile,
        back_page=None,
        cancel_page=0,
    )
    await callback.answer()


@router.callback_query(F.data.startswith(MESSAGE_DEAL_PREFIX))
async def prompt_message(callback: CallbackQuery, state: FSMContext) -> None:
    user = callback.from_user
    if not user:
        await callback.answer()
        return
    deal_id = callback.data[len(MESSAGE_DEAL_PREFIX) :]
    deps = get_deps()
    deal = await deps.deal_service.get_deal(deal_id)
    if not deal or not deal.buyer_id:
        await callback.answer("Сделка недоступна", show_alert=True)
        return
    if user.id not in {deal.seller_id, deal.buyer_id}:
        await callback.answer("Нет доступа", show_alert=True)
        return
    recipient = deal.buyer_id if user.id == deal.seller_id else deal.seller_id
    recipient_profile = await deps.user_service.profile_of(recipient)
    if recipient_profile:
        recipient_name = recipient_profile.full_name or recipient_profile.username or "—"
    else:
        recipient_name = "—"
    await state.set_state(MessageRelayState.waiting_text)
    await state.update_data(
        relay_target=recipient,
        relay_deal_id=deal.id,
        relay_tag=deal.hashtag,
    )
    chat_id = callback.message.chat.id if callback.message else user.id
    await callback.bot.send_message(
        chat_id,
        f"💬 Чат с {recipient_name} по сделке {deal.hashtag}",
    )
    await callback.answer()


@router.message(MessageRelayState.waiting_text)
async def relay_message(message: Message, state: FSMContext) -> None:
    if not message.text:
        await message.answer("Нужно отправить текстовое сообщение. Попробуй снова.")
        return
    text = message.text.strip()
    data = await state.get_data()
    target_id = data.get("relay_target")
    tag = data.get("relay_tag", "")
    deal_id = data.get("relay_deal_id")
    if text.lower() == "отмена":
        await state.clear()
        await message.answer("Отправка сообщения отменена.")
        return
    if not target_id:
        await state.clear()
        await message.answer("Не удалось определить получателя.")
        return
    sender_name = message.from_user.full_name or message.from_user.username or str(message.from_user.id)
    builder = InlineKeyboardBuilder()
    if deal_id:
        builder.button(text="Ответить", callback_data=f"{MESSAGE_DEAL_PREFIX}{deal_id}")
    await message.bot.send_message(
        target_id,
        f"💬 Сообщение по сделке {tag} от {sender_name}:\n\n{text}",
        reply_markup=builder.as_markup() if deal_id else None,
    )
    await message.answer("💬 Сообщение отправлено.")
    await state.clear()


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


async def _send_open_deals(
    user_id: int, chat_id: int, bot, *, order: str, state: FSMContext | None = None
) -> bool:
    deps = get_deps()
    role = await deps.user_service.role_of(user_id)
    if role != UserRole.BUYER:
        await bot.send_message(chat_id, "Список сделок доступен только мерчантам.")
        return False
    deals = await deps.deal_service.list_open_deals()
    payload = _build_open_deals_markup(deals, order)
    if not payload:
        sent = await bot.send_message(chat_id, "Нет доступных сделок")
        if state:
            await state.update_data(last_menu_message_id=sent.message_id, last_menu_chat_id=sent.chat.id)
        return False
    text, markup = payload
    sent = await bot.send_message(chat_id, text, reply_markup=markup)
    if state:
        await state.update_data(last_menu_message_id=sent.message_id, last_menu_chat_id=sent.chat.id)
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


def _qr_request_info_payload(deal_id: str) -> str:
    return f"{QR_REQUEST_PREFIX}info:{deal_id}"


def _qr_view_info_payload(deal_id: str) -> str:
    return f"{QR_VIEW_PREFIX}info:{deal_id}"


def _qr_attach_info_payload(deal_id: str) -> str:
    return f"{QR_SELLER_ATTACH_PREFIX}info:{deal_id}"


def _qr_ready_info_payload(deal_id: str) -> str:
    return f"{QR_SELLER_READY_PREFIX}info:{deal_id}"


def _qr_buyer_done_info_payload(deal_id: str) -> str:
    return f"{QR_BUYER_DONE_PREFIX}info:{deal_id}"


def _qr_seller_done_info_payload(deal_id: str) -> str:
    return f"{QR_SELLER_DONE_PREFIX}info:{deal_id}"


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
    text = _format_open_deals_text(total=len(deals), order=order)
    return text, builder.as_markup()


def _format_open_deals_text(*, total: int, order: str) -> str:
    order_text = "по возрастанию" if order == "asc" else "по убыванию"
    lines = [
        "<b>📋 Купить USDT</b>",
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
    quantized = value.quantize(Decimal("0.001"))
    text = format(quantized, "f")
    if "." in text:
        text = text.rstrip("0").rstrip(".")
    return text or "0"


def _format_deal_detail(
    deal: Deal,
    profile: UserProfile | None,
    *,
    viewer_id: int | None = None,
    buyer_profile: UserProfile | None = None,
    show_seller_block: bool = True,
    compact: bool = False,
    review: Review | None = None,
    dispute: Dispute | None = None,
) -> str:
    rub_amount = _format_decimal(deal.usd_amount)
    usdt_amount = _format_decimal(deal.usdt_amount)
    rate = _format_decimal(deal.rate)
    created = deal.created_at.astimezone(timezone.utc).strftime("%d.%m %H:%M")
    name = escape(profile.full_name) if profile and profile.full_name else "—"
    last_seen = _format_last_seen(profile)
    role = "Продавец"
    if viewer_id:
        if viewer_id == deal.buyer_id:
            role = "Покупатель"
        elif viewer_id not in {deal.seller_id, deal.buyer_id}:
            role = "Наблюдатель"
    status_text = _deal_stage_label(deal, viewer_id)
    dispute_outcome = None
    if deal.status == DealStatus.COMPLETED and dispute and dispute.resolved:
        status_text = "Завершена спором"
        buyer_amount = Decimal(str(dispute.buyer_amount or "0"))
        seller_amount = Decimal(str(dispute.seller_amount or "0"))
        if buyer_amount > seller_amount:
            dispute_outcome = f"в пользу {_buyer_label(deal).lower()}"
        elif seller_amount > buyer_amount:
            dispute_outcome = "в пользу продавца"
        elif buyer_amount > 0 and buyer_amount == seller_amount:
            dispute_outcome = "с разделением"
        else:
            dispute_outcome = "без выплат"
    atm = bank_label(deal.atm_bank)
    status_line = status_text
    show_party_block = show_seller_block and not compact
    buyer_label = _buyer_label(deal)
    if compact:
        lines = [
            f"<b>Сделка {deal.hashtag}</b>",
            f"💵 Наличные: ₽{rub_amount}",
            f"🪙 USDT к оплате: {usdt_amount} USDT",
            f"💱 Курс: 1 USDT = {rate} RUB",
            f"🗓 Создано: {created}",
        ]
    else:
        if viewer_id == deal.seller_id and deal.status == DealStatus.PAID:
            buyer_name = _format_buyer_name(buyer_profile, deal.buyer_id or 0)
            buyer_last_seen = _format_last_seen(buyer_profile)
            lines = [
                f"<b>Сделка {deal.hashtag}</b>",
                f"📌 Статус: <b>{status_line}</b>",
                f"💵 Наличные: ₽{rub_amount}",
                f"🪙 USDT к оплате: {usdt_amount} USDT",
                f"💱 Курс: 1 USDT = {rate} RUB",
                f"🗓 Создано: {created}",
                f"🏧 Банкомат: {atm}",
                "",
                f"👤 {buyer_label}: {buyer_name}",
                f"⏱ Последний онлайн: {buyer_last_seen}",
            ]
            show_party_block = False
        else:
            lines = [
                f"<b>Сделка {deal.hashtag}</b>",
                f"👤 Роль: {role}",
                f"📌 Статус: <b>{status_line}</b>",
                f"💵 Наличные: ₽{rub_amount}",
                f"🪙 USDT к оплате: {usdt_amount} USDT",
                f"💱 Курс: 1 USDT = {rate} RUB",
                f"🗓 Создано: {created}",
            ]
            if deal.status in {DealStatus.PAID, DealStatus.COMPLETED}:
                lines.append(f"🏧 Банкомат: {atm}")
                if deal.buyer_id:
                    lines.append(
                        f"👤 {buyer_label}: {_format_buyer_name(buyer_profile, deal.buyer_id)}"
                    )
                else:
                    lines.append(f"👤 {buyer_label}: —")
    if deal.status == DealStatus.DISPUTE and dispute:
        opener_name = "—"
        if dispute.opened_by == deal.seller_id:
            opener_name = _format_buyer_name(profile, deal.seller_id)
            opener_role = "Продавец"
        else:
            opener_name = _format_buyer_name(buyer_profile, dispute.opened_by)
            opener_role = buyer_label
        lines.append("")
        lines.append(f"🛡️ Открыл спор: {opener_role} — {opener_name}")
        lines.append(f"Причина: {escape(dispute.reason)}")
        if dispute.comment:
            lines.append(f"Комментарий: {escape(dispute.comment)}")
    if deal.status == DealStatus.COMPLETED and dispute_outcome:
        lines.append(f"⚖️ Закрыта {dispute_outcome}")
    if deal.buyer_cash_confirmed and not (deal.status == DealStatus.COMPLETED and dispute_outcome):
        lines.append(f"✅ {buyer_label} подтвердил выдачу")
    if show_party_block:
        if viewer_id == deal.seller_id and deal.buyer_id:
            buyer_name = _format_buyer_name(buyer_profile, deal.buyer_id)
            buyer_last_seen = _format_last_seen(buyer_profile)
            lines.extend(
                [
                    "",
                    f"⏱ Последний онлайн: {buyer_last_seen}",
                ]
            )
        else:
            lines.extend(
                [
                    "",
                    "<b>👤 Продавец</b>",
                    f"🙍 Имя: {name}",
                    f"⏱ Последний онлайн: {last_seen}",
                ]
            )
    if deal.status == DealStatus.COMPLETED:
        mark = _format_review_mark(review)
        lines.append(f"⭐ Оценка сделки: {mark}")
    if deal.comment:
        lines.append("")
        lines.append(f"Комментарий: {escape(deal.comment)}")
    return "\n".join(lines)


def _format_review_mark(review: Review | None) -> str:
    if not review:
        return "—"
    return "👍" if review.rating > 0 else "👎"


def _format_last_seen(profile: UserProfile | None) -> str:
    if not profile or not getattr(profile, "last_seen_at", None):
        return "нет данных"
    last_seen = profile.last_seen_at
    now = datetime.now(timezone.utc)
    delta = now - last_seen
    seconds = int(delta.total_seconds())
    if seconds < 60:
        return "менее минуты назад"
    if seconds < 3600:
        minutes = seconds // 60
        return f"{minutes} мин назад"
    if seconds < 86400:
        hours = seconds // 3600
        return f"{hours} ч назад"
    if seconds < 2592000:
        days = seconds // 86400
        return f"{days} дн назад"
    return last_seen.astimezone(timezone.utc).strftime("%d.%m %H:%M")


def _format_buyer_name(profile: UserProfile | None, fallback_id: int) -> str:
    if profile:
        if getattr(profile, "display_name", None):
            return profile.display_name
        if profile.full_name:
            return profile.full_name
        if profile.username:
            return profile.username
    return "—"


def _deal_stage_label(deal: Deal, viewer_id: int | None) -> str:
    if deal.status == DealStatus.OPEN:
        if viewer_id == deal.seller_id:
            return "Ожидаем покупателя" if deal.is_p2p else "Ожидаем Мерчанта"
        return "Ждем оплату"
    if deal.status == DealStatus.PENDING:
        return "Ожидаем принятия"
    if deal.status == DealStatus.RESERVED:
        return "Ждем оплату"
    if deal.status == DealStatus.PAID:
        if deal.qr_stage == QrStage.READY and deal.qr_photo_id:
            return "Выдача наличных"
        if deal.qr_stage == QrStage.AWAITING_SELLER_ATTACH:
            return "Подготовка QR"
        if deal.qr_stage == QrStage.AWAITING_BUYER_READY:
            return "Ожидаем готовность"
        if deal.qr_stage == QrStage.AWAITING_SELLER_PHOTO:
            return "Прикрепление QR"
        return "Отправка QR"
    if deal.status == DealStatus.DISPUTE:
        return "Открыт спор"
    if deal.status == DealStatus.COMPLETED:
        return "Завершена"
    if deal.status == DealStatus.CANCELED:
        return "Отменена"
    if deal.status == DealStatus.EXPIRED:
        return "Истекла"
    return deal.status.value


def _buyer_label(deal: Deal) -> str:
    return "Покупатель" if deal.is_p2p else "Мерчант"


async def _send_deal_card(
    *,
    bot,
    chat_id: int,
    deal: Deal,
    viewer_id: int,
    seller_profile: UserProfile | None,
    buyer_profile: UserProfile | None,
    back_page: int | None,
    cancel_page: int | None = None,
    compact: bool = False,
    back_page_prefix: str = MY_DEALS_PAGE_PREFIX,
) -> None:
    review = None
    dispute = None
    if deal.status in {DealStatus.COMPLETED, DealStatus.DISPUTE}:
        deps = get_deps()
        if deal.status == DealStatus.COMPLETED:
            review = await deps.review_service.review_for_deal(deal.id, prefer_from=viewer_id)
            dispute = await deps.dispute_service.dispute_any_for_deal(deal.id)
        else:
            dispute = await deps.dispute_service.dispute_for_deal(deal.id)
    text = _format_deal_detail(
        deal,
        seller_profile,
        viewer_id=viewer_id,
        buyer_profile=buyer_profile,
        compact=compact,
        review=review,
        dispute=dispute,
    )
    markup = _deal_menu_markup(
        deal,
        viewer_id=viewer_id,
        buyer_profile=buyer_profile,
        back_page=back_page,
        cancel_page=cancel_page,
        back_page_prefix=back_page_prefix,
    )
    await bot.send_message(chat_id, text, reply_markup=markup)


def _deal_menu_markup(
    deal: Deal,
    *,
    viewer_id: int,
    buyer_profile: UserProfile | None,
    back_page: int | None,
    cancel_page: int | None = None,
    back_page_prefix: str = MY_DEALS_PAGE_PREFIX,
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    if deal.status == DealStatus.COMPLETED:
        builder.row(
            InlineKeyboardButton(
                text="👤 Профиль продавца",
                callback_data=f"{PROFILE_VIEW_PREFIX}{deal.seller_id}",
            )
        )
        return builder.as_markup()
    if deal.buyer_id and viewer_id in {deal.seller_id, deal.buyer_id}:
        builder.row(
            InlineKeyboardButton(
                text="📨 Написать сообщение",
                callback_data=f"{MESSAGE_DEAL_PREFIX}{deal.id}",
            )
        )
    if viewer_id == deal.buyer_id:
        builder.row(
            InlineKeyboardButton(
                text="👤 Профиль продавца",
                callback_data=f"{PROFILE_VIEW_PREFIX}{deal.seller_id}",
            )
        )
    if viewer_id == deal.seller_id and deal.buyer_id:
        builder.row(
            InlineKeyboardButton(
                text="👤 Профиль покупателя",
                callback_data=f"{PROFILE_VIEW_PREFIX}{deal.buyer_id}",
            )
        )
    if viewer_id == deal.buyer_id:
        if deal.status == DealStatus.PAID and deal.qr_stage in {QrStage.IDLE, QrStage.READY}:
            builder.row(
                InlineKeyboardButton(
                    text="📥 Запросить QR",
                    callback_data=_qr_request_info_payload(deal.id),
                )
            )
        if deal.qr_photo_id:
            builder.row(
                InlineKeyboardButton(
                    text="👁 Посмотреть QR",
                    callback_data=_qr_view_info_payload(deal.id),
                )
            )
        if deal.qr_stage == QrStage.READY and not deal.buyer_cash_confirmed:
            builder.row(
                InlineKeyboardButton(
                    text="✅ Успешно снял",
                    callback_data=_qr_buyer_done_info_payload(deal.id),
                )
            )
    if viewer_id == deal.seller_id and deal.qr_stage == QrStage.AWAITING_SELLER_ATTACH:
        builder.row(
            InlineKeyboardButton(
                text="✅ Готов отправить QR",
                callback_data=_qr_ready_info_payload(deal.id),
            )
        )
    if viewer_id == deal.seller_id and deal.qr_stage == QrStage.AWAITING_SELLER_PHOTO:
        builder.row(
            InlineKeyboardButton(
                text="📎 Прикрепить QR",
                callback_data=_qr_attach_info_payload(deal.id),
            )
        )
    if viewer_id == deal.seller_id and deal.qr_stage == QrStage.READY and not deal.seller_cash_confirmed:
        builder.row(
            InlineKeyboardButton(
                text="💸 Получил нал",
                callback_data=_qr_seller_done_info_payload(deal.id),
            )
        )
    if (
        deal.status == DealStatus.PAID
        and viewer_id in {deal.seller_id, deal.buyer_id}
        and deal.status != DealStatus.DISPUTE
        and deal.dispute_opened_by is None
    ):
        builder.row(
            InlineKeyboardButton(
                text="🛡️ Открыть спор",
                callback_data=f"{DISPUTE_OPEN_PREFIX}{deal.id}",
            )
        )
    if (
        deal.status == DealStatus.DISPUTE
        and viewer_id in {deal.seller_id, deal.buyer_id}
        and deal.dispute_opened_by
        and viewer_id != deal.dispute_opened_by
    ):
        builder.row(
            InlineKeyboardButton(
                text="🧾 Дополнить спор",
                callback_data=f"{DISPUTE_APPEND_PREFIX}{deal.id}",
            )
        )
    if viewer_id == deal.seller_id and deal.status in {DealStatus.RESERVED, DealStatus.PAID}:
        if deal.status == DealStatus.PAID and deal.qr_stage == QrStage.READY and deal.qr_photo_id:
            pass
        else:
            cancel_page_value = cancel_page if cancel_page is not None else 0
            builder.row(
                InlineKeyboardButton(
                    text="⛔️ Отменить",
                    callback_data=f"{DEAL_CANCEL_PREFIX}{cancel_page_value}:{deal.id}",
                )
            )
    if viewer_id == deal.seller_id and deal.status == DealStatus.OPEN:
        cancel_page_value = cancel_page if cancel_page is not None else 0
        builder.row(
            InlineKeyboardButton(
                text="⛔️ Отменить",
                callback_data=f"{DEAL_CANCEL_PREFIX}{cancel_page_value}:{deal.id}",
            )
        )
    if deal.status == DealStatus.OPEN and viewer_id != deal.seller_id:
        builder.row(
            InlineKeyboardButton(
                text="✅ Взять сделку",
                callback_data=f"deal_accept:{deal.id}",
            )
        )
    return builder.as_markup()


async def _cancel_deal(message: Message, deal_id: str) -> None:
    deps = get_deps()
    try:
        deal, refund_amount = await deps.deal_service.cancel_deal(deal_id, message.from_user.id)
    except Exception as exc:
        await message.answer(f"Не удалось отменить: {exc}")
        return
    if refund_amount is not None and message.from_user.id == deal.seller_id:
        await message.answer(
            f"Сделка {deal.hashtag} отменена.\n"
            f"На баланс зачислено {refund_amount} USDT (комиссия удержана)."
        )
    else:
        await message.answer(f"Сделка {deal.hashtag} отменена")


async def _complete_deal(message: Message, deal_id: str) -> None:
    deps = get_deps()
    try:
        deal, payout = await deps.deal_service.complete_deal(deal_id, message.from_user.id)
    except Exception as exc:
        await message.answer(f"Не получилось: {exc}")
        return
    await message.answer(f"Сделка {deal.hashtag} завершена")
    if payout:
        await _notify_completion(deal, deps, message.bot)
    elif deal.buyer_id:
        await message.bot.send_message(deal.buyer_id, f"Сделка {deal.hashtag} закрыта продавцом")


async def _notify_completion(deal: Deal, deps, bot) -> None:
    dispute_any = await deps.dispute_service.dispute_any_for_deal(deal.id)
    dispute_resolved = bool(dispute_any and dispute_any.resolved)
    credited = False
    if deal.buyer_id:
        credited = await deps.kb_client.credit_balance(deal.buyer_id, deal.usdt_amount)
        buyer_note = (
            f"Средства зачислены на баланс ({deal.usdt_amount} USDT)."
            if credited
            else "Не удалось обновить баланс автоматически."
        )
        buyer_builder = InlineKeyboardBuilder()
        buyer_review = None
        if not dispute_resolved:
            buyer_review = await deps.review_service.review_between(
                deal.buyer_id, deal.seller_id
            )
            if buyer_review is None:
                buyer_builder.button(
                    text="Оценить сделку",
                    callback_data=f"{REVIEW_START_PREFIX}{deal.id}",
                )
        await bot.send_message(
            deal.buyer_id,
            f"✅ Сделка {deal.hashtag} завершена.\n{buyer_note}\n"
            "Используй кнопку «Баланс», чтобы оформить вывод USDT.",
            reply_markup=buyer_builder.as_markup()
            if (not dispute_resolved and buyer_review is None)
            else None,
        )
    if deal.seller_id:
        builder = InlineKeyboardBuilder()
        review = None
        if not dispute_resolved:
            review = await deps.review_service.review_between(
                deal.seller_id, deal.buyer_id
            )
            if review is None:
                builder.button(
                    text="Оценить сделку",
                    callback_data=f"{REVIEW_START_PREFIX}{deal.id}",
                )
        await bot.send_message(
            deal.seller_id,
            f"✅ Сделка {deal.hashtag} выполнена.",
            reply_markup=builder.as_markup() if (not dispute_resolved and review is None) else None,
        )


async def _delete_callback_message(callback: CallbackQuery) -> None:
    message = callback.message
    if not message:
        return
    with suppress(TelegramBadRequest):
        await message.delete()


async def _send_sell_prompt(
    chat_id: int, bot, *, mode: str, state: FSMContext | None = None
) -> None:
    sent = await bot.send_message(
        chat_id,
        _sell_prompt_text(mode),
        reply_markup=_sell_prompt_keyboard(mode),
    )
    if state:
        await state.update_data(last_menu_message_id=sent.message_id, last_menu_chat_id=sent.chat.id)


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
    rub_text = _format_decimal(cash_amount)
    usdt_text = _format_decimal(usdt_amount)
    return (
        "<b>📄 Предпросмотр сделки</b>\n"
        f"{note}\n"
        f"💵 Наличные: ₽{rub_text}\n"
        f"💱 Курс: 1 USDT = {snapshot.usd_rate} RUB\n"
        f"⚖️ Комиссия: {snapshot.fee_percent}%\n"
        f"🪙 К оплате: {usdt_text} USDT"
    )
