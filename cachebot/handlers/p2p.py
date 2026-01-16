from __future__ import annotations

from contextlib import suppress
from datetime import timezone
from decimal import Decimal, InvalidOperation, ROUND_UP

from aiogram import F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, InlineKeyboardButton, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

from cachebot.constants import BANK_OPTIONS, bank_label
from cachebot.deps import get_deps
from cachebot.handlers.commands import _send_profile
from cachebot.handlers.deal_flow import _deal_stage_label, _send_deal_card
from cachebot.keyboards import MenuAction
from cachebot.models.advert import Advert, AdvertSide
from cachebot.models.deal import Deal, DealStatus


router = Router(name="p2p")

P2P_MENU = "p2p:menu"
P2P_BUY = "p2p:buy"
P2P_SELL = "p2p:sell"
P2P_MY_DEALS = "p2p:mydeals"
P2P_MY_DEALS_PAGE_PREFIX = "p2p:mydeals:page:"
P2P_MY_DEALS_VIEW_PREFIX = "p2p:mydeals:view:"
P2P_PROFILE = "p2p:profile"
P2P_ADS = "p2p:ads"
P2P_AD_CREATE = "p2p:ad:create"
P2P_AD_VIEW_PREFIX = "p2p:ad:view:"
P2P_AD_TOGGLE_PREFIX = "p2p:ad:toggle:"
P2P_AD_DELETE_PREFIX = "p2p:ad:delete:"
P2P_AD_EDIT_PREFIX = "p2p:ad:edit:"
P2P_TRADING_TOGGLE = "p2p:trading:toggle"
P2P_PUBLIC_VIEW_PREFIX = "p2p:public:view:"
P2P_PUBLIC_OFFER_PREFIX = "p2p:public:offer:"
P2P_BANK_PREFIX = "p2p:bank:"
P2P_TERMS_SKIP = "p2p:terms:skip"
P2P_EDIT_CANCEL = "p2p:edit:cancel"
P2P_CREATE_CANCEL = "p2p:create:cancel"
P2P_VOLUME_MAX = "p2p:volume:max"
DEAL_INFO_PREFIX = "deal_info:"


class P2PAdCreateState(StatesGroup):
    choosing_side = State()
    waiting_volume = State()
    waiting_price = State()
    waiting_limits = State()
    choosing_banks = State()
    waiting_terms = State()


class P2PAdEditState(StatesGroup):
    waiting_value = State()
    choosing_banks = State()
    waiting_terms = State()


class P2PDealState(StatesGroup):
    waiting_amount = State()


def _format_decimal(value: Decimal) -> str:
    quantized = value.quantize(Decimal("0.001"))
    text = format(quantized, "f")
    if "." in text:
        text = text.rstrip("0").rstrip(".")
    return text or "0"


def _p2p_menu_text() -> str:
    return "💠 Здесь вы можете купить или продать криптовалюту\nРаботаем только с наличными и банкоматами"


def _ad_side_label(side: AdvertSide) -> str:
    return "Продажа" if side == AdvertSide.SELL else "Покупка"


def _ad_side_emoji(side: AdvertSide) -> str:
    return "🔸" if side == AdvertSide.SELL else "🔹"


def _ad_button_label(ad: Advert) -> str:
    price = _format_decimal(ad.price_rub)
    min_rub = _format_decimal(ad.min_rub)
    max_rub = _format_decimal(ad.max_rub)
    status_emoji = "🟩" if ad.active else "🔶"
    return (
        f"{status_emoji} {_ad_side_emoji(ad.side)} {_ad_side_label(ad.side)} · "
        f"₽{price}/USDT · ₽{min_rub}-{max_rub}"
    )


def _profile_display_name(profile) -> str:
    if not profile:
        return "—"
    if getattr(profile, "display_name", None):
        return profile.display_name
    if getattr(profile, "full_name", None):
        return profile.full_name
    if getattr(profile, "username", None):
        return profile.username
    return "—"


def _ad_public_button_label(ad: Advert, owner_name: str) -> str:
    price = _format_decimal(ad.price_rub)
    min_rub = _format_decimal(ad.min_rub)
    max_rub = _format_decimal(ad.max_rub)
    return f"{owner_name} | ₽{min_rub}-{max_rub} | ₽{price}/USDT"


async def _ad_available_usdt(deps, ad: Advert) -> Decimal:
    balance = await deps.deal_service.balance_of(ad.owner_id)
    available = min(ad.remaining_usdt, balance)
    max_possible = available * ad.price_rub
    if ad.active and (available <= 0 or ad.min_rub > max_possible):
        await deps.advert_service.update_ad(ad.id, active=False)
    return available


def _p2p_deal_button_label(deal: Deal, user_id: int, index: int) -> str:
    role_icon = "💵" if deal.seller_id == user_id else "🛒"
    short_date = deal.created_at.strftime("%d.%m %H:%M")
    status_tag = _deal_stage_label(deal, user_id)
    return f"{role_icon} #{index} · {deal.hashtag} · {short_date} · {status_tag}"


def _p2p_bank_keyboard(selected: list[str]) -> InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()
    for key, label in BANK_OPTIONS.items():
        prefix = "✅ " if key in selected else ""
        builder.button(text=f"{prefix}{label}", callback_data=f"{P2P_BANK_PREFIX}{key}")
    builder.button(text="Готово", callback_data=f"{P2P_BANK_PREFIX}done")
    builder.adjust(3, 1)
    return builder


def _p2p_menu_keyboard(active: int, total: int) -> InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()
    builder.button(text="Купить", callback_data=P2P_BUY)
    builder.button(text="Продать", callback_data=P2P_SELL)
    builder.button(text="Мои сделки", callback_data=P2P_MY_DEALS)
    builder.button(text=f"Объявления {active}/{total}", callback_data=P2P_ADS)
    builder.button(text="Мой профиль", callback_data=P2P_PROFILE)
    builder.button(text="⬅️ Назад", callback_data=MenuAction.BACK.value)
    builder.adjust(2, 2, 1, 1)
    return builder


def _ad_manage_text(trading_enabled: bool) -> str:
    if trading_enabled:
        return (
            "🔋 Здесь вы можете управлять своими объявлениями.\n\n"
            "🚀 Торги включены. Остановите торги, если вы не можете принимать сделки."
        )
    return (
        "🔋 Здесь вы можете управлять своими объявлениями.\n\n"
        "🌙 Торги приостановлены. Включите торги, когда будете готовы принимать сделки."
    )


def _ad_manage_keyboard(trading_enabled: bool) -> InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()
    builder.button(text="🚀 Создать объявление", callback_data=P2P_AD_CREATE)
    toggle_text = "🌙 Приостановить торги" if trading_enabled else "🚀 Возобновить торги"
    builder.button(text=toggle_text, callback_data=P2P_TRADING_TOGGLE)
    builder.button(text="⬅️ Назад", callback_data=MenuAction.BACK.value)
    builder.adjust(1, 1, 1)
    return builder


def _ad_owner_card(ad: Advert, trading_enabled: bool) -> str:
    status_line = (
        "🟩 Активно. Объявление показывается в общем списке."
        if ad.active and trading_enabled
        else "🔶 Неактивно. Объявление не показывается в общем списке."
    )
    banks = " · ".join(bank_label(key) for key in ad.banks) or "—"
    terms = ad.terms or "не указаны"
    if len(terms) > 300:
        terms = f"{terms[:297]}..."
    price = _format_decimal(ad.price_rub)
    total = _format_decimal(ad.total_usdt)
    min_rub = _format_decimal(ad.min_rub)
    max_rub = _format_decimal(ad.max_rub)
    side_text = "Продажа" if ad.side == AdvertSide.SELL else "Покупка"
    return (
        f"🧾 <b>Объявление {ad.hashtag}</b>\n\n"
        f"{side_text} USDT за RUB.\n\n"
        f"Цена: ₽ {price} RUB\n\n"
        f"Общий объём: {total} USDT\n"
        f"Лимиты: ₽ {min_rub} ~ {max_rub}\n\n"
        f"Способы оплаты: {banks}\n\n"
        "Срок оплаты: 15 мин\n\n"
        f"Условия сделки: {terms}\n\n"
        f"{status_line}"
    )


def _ad_owner_keyboard(ad: Advert) -> InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()
    if ad.active:
        builder.button(text="🙈 Снять с публикации", callback_data=f"{P2P_AD_TOGGLE_PREFIX}{ad.id}:off")
    else:
        builder.button(text="💎 Опубликовать", callback_data=f"{P2P_AD_TOGGLE_PREFIX}{ad.id}:on")
    builder.button(text="Цена", callback_data=f"{P2P_AD_EDIT_PREFIX}{ad.id}:price")
    builder.button(text="Объём", callback_data=f"{P2P_AD_EDIT_PREFIX}{ad.id}:volume")
    builder.button(text="Лимиты", callback_data=f"{P2P_AD_EDIT_PREFIX}{ad.id}:limits")
    builder.button(text="Способы оплаты", callback_data=f"{P2P_AD_EDIT_PREFIX}{ad.id}:banks")
    builder.button(text="Условия сделки", callback_data=f"{P2P_AD_EDIT_PREFIX}{ad.id}:terms")
    builder.button(text="Удалить объявление", callback_data=f"{P2P_AD_DELETE_PREFIX}{ad.id}")
    builder.adjust(1, 2, 2, 1, 1, 1)
    return builder


def _ad_public_card(ad: Advert) -> str:
    banks = " · ".join(bank_label(key) for key in ad.banks) or "—"
    terms = ad.terms or "не указаны"
    if len(terms) > 300:
        terms = f"{terms[:297]}..."
    price = _format_decimal(ad.price_rub)
    volume = _format_decimal(ad.remaining_usdt)
    min_rub = _format_decimal(ad.min_rub)
    max_rub = _format_decimal(ad.max_rub)
    side_text = "Продажа" if ad.side == AdvertSide.SELL else "Покупка"
    return (
        f"🧾 <b>Объявление {ad.hashtag}</b>\n\n"
        f"{side_text} USDT за RUB.\n\n"
        f"Цена: ₽ {price} RUB\n\n"
        f"Доступный объём: {volume} USDT\n"
        f"Лимиты: ₽ {min_rub} ~ {max_rub}\n\n"
        f"Способы оплаты: {banks}\n\n"
        "Срок оплаты: 15 мин\n\n"
        f"Условия сделки: {terms}"
    )


async def _delete_callback_message(callback: CallbackQuery) -> None:
    if not callback.message:
        return
    with suppress(TelegramBadRequest):
        await callback.message.delete()


async def _show_p2p_menu(callback: CallbackQuery, *, state: FSMContext | None = None) -> None:
    deps = get_deps()
    user = callback.from_user
    if not user:
        await callback.answer()
        return
    active, total = await deps.advert_service.counts_for_user(user.id)
    with suppress(TelegramBadRequest):
        await callback.message.delete()
    if state:
        await state.update_data(back_action=None)
    await callback.message.answer(
        _p2p_menu_text(),
        reply_markup=_p2p_menu_keyboard(active, total).as_markup(),
    )


async def send_p2p_menu(bot, chat_id: int, user_id: int, *, state: FSMContext | None = None) -> None:
    deps = get_deps()
    active, total = await deps.advert_service.counts_for_user(user_id)
    sent = await bot.send_message(
        chat_id,
        _p2p_menu_text(),
        reply_markup=_p2p_menu_keyboard(active, total).as_markup(),
    )
    if state:
        await state.update_data(back_action=None)
        await state.update_data(last_menu_message_id=sent.message_id, last_menu_chat_id=sent.chat.id)


async def send_p2p_ads(bot, chat_id: int, user_id: int, *, state: FSMContext | None = None) -> None:
    deps = get_deps()
    trading_enabled = await deps.advert_service.trading_enabled(user_id)
    ads = await deps.advert_service.list_user_ads(user_id)
    for ad in ads:
        with suppress(Exception):
            await _ad_available_usdt(deps, ad)
    builder = _ad_manage_keyboard(trading_enabled)
    for ad in ads:
        builder.row(
            InlineKeyboardButton(
                text=_ad_button_label(ad),
                callback_data=f"{P2P_AD_VIEW_PREFIX}{ad.id}",
            )
        )
    # back navigation via reply keyboard
    if state:
        await state.update_data(back_action=P2P_MENU)
    sent = await bot.send_message(
        chat_id,
        _ad_manage_text(trading_enabled),
        reply_markup=builder.as_markup(),
    )
    if state:
        await state.update_data(last_menu_message_id=sent.message_id, last_menu_chat_id=sent.chat.id)


async def send_p2p_list(
    bot, chat_id: int, user_id: int, *, side: str, state: FSMContext | None = None
) -> None:
    deps = get_deps()
    if side == "buy":
        ads = await deps.advert_service.list_public_ads(AdvertSide.SELL)
        title = "💠 Доступные объявления на покупку:"
        back_action = P2P_BUY
    else:
        ads = await deps.advert_service.list_public_ads(AdvertSide.BUY)
        title = "💠 Доступные объявления на продажу:"
        back_action = P2P_SELL
    builder = InlineKeyboardBuilder()
    if not ads:
        # back navigation via reply keyboard
        if state:
            await state.update_data(back_action=P2P_MENU, p2p_last_list=back_action)
        builder.button(text="⬅️ Назад", callback_data=MenuAction.BACK.value)
        sent = await bot.send_message(
            chat_id, "Пока нет доступных объявлений.", reply_markup=builder.as_markup()
        )
        if state:
            await state.update_data(last_menu_message_id=sent.message_id, last_menu_chat_id=sent.chat.id)
        return
    for ad in ads:
        available = await _ad_available_usdt(deps, ad)
        if available <= 0 or not ad.active:
            continue
        profile = await deps.user_service.profile_of(ad.owner_id)
        name = _profile_display_name(profile)
        builder.row(
            InlineKeyboardButton(
                text=_ad_public_button_label(ad, name),
                callback_data=f"{P2P_PUBLIC_VIEW_PREFIX}{ad.id}",
            )
        )
    if not builder._buttons:
        if state:
            await state.update_data(back_action=P2P_MENU, p2p_last_list=back_action)
        builder.button(text="⬅️ Назад", callback_data=MenuAction.BACK.value)
        sent = await bot.send_message(
            chat_id, "Пока нет доступных объявлений.", reply_markup=builder.as_markup()
        )
        if state:
            await state.update_data(last_menu_message_id=sent.message_id, last_menu_chat_id=sent.chat.id)
        return
    # back navigation via reply keyboard
    if state:
        await state.update_data(back_action=P2P_MENU, p2p_last_list=back_action)
    builder.row(
        InlineKeyboardButton(
            text="⬅️ Назад",
            callback_data=MenuAction.BACK.value,
        )
    )
    sent = await bot.send_message(chat_id, title, reply_markup=builder.as_markup())
    if state:
        await state.update_data(last_menu_message_id=sent.message_id, last_menu_chat_id=sent.chat.id)


async def send_p2p_my_deals(
    bot, chat_id: int, user_id: int, *, page: int, state: FSMContext | None = None
) -> None:
    deps = get_deps()
    deals = await deps.deal_service.list_user_deals(user_id)
    if not deals:
        builder = InlineKeyboardBuilder()
        # back navigation via reply keyboard
        if state:
            await state.update_data(back_action=P2P_MENU)
        builder.button(text="⬅️ Назад", callback_data=MenuAction.BACK.value)
        sent = await bot.send_message(chat_id, "У тебя пока нет сделок", reply_markup=builder.as_markup())
        if state:
            await state.update_data(last_menu_message_id=sent.message_id, last_menu_chat_id=sent.chat.id)
        return
    total_pages = max(1, (len(deals) + 7 - 1) // 7)
    page = max(0, min(page, total_pages - 1))
    start = page * 7
    chunk = deals[start : start + 7]
    total = len(deals)
    success = sum(1 for item in deals if item.status == DealStatus.COMPLETED)
    failed = sum(1 for item in deals if item.status in {DealStatus.CANCELED, DealStatus.EXPIRED})
    text = (
        "<b>📂 Мои сделки</b>\n"
        f"Всего: {total}\n"
        f"Успешных: {success}\n"
        f"Отменённых/истёкших: {failed}\n"
        f"Страница {page + 1}/{total_pages}\n\n"
        "Выбери сделку кнопками ниже."
    )
    builder = InlineKeyboardBuilder()
    for index, deal in enumerate(chunk, start=start + 1):
        builder.row(
            InlineKeyboardButton(
                text=_p2p_deal_button_label(deal, user_id, index),
                callback_data=f"{P2P_MY_DEALS_VIEW_PREFIX}{page}:{deal.id}",
            )
        )
    if total_pages > 1:
        nav_buttons = []
        if page > 0:
            nav_buttons.append(
                InlineKeyboardButton(
                    text=f"Стр. {page}",
                    callback_data=f"{P2P_MY_DEALS_PAGE_PREFIX}{page - 1}",
                )
            )
        if page < total_pages - 1:
            nav_buttons.append(
                InlineKeyboardButton(
                    text=f"Стр. {page + 2} ➡️",
                    callback_data=f"{P2P_MY_DEALS_PAGE_PREFIX}{page + 1}",
                )
            )
        if nav_buttons:
            builder.row(*nav_buttons)
    # back navigation via reply keyboard
    if state:
        await state.update_data(back_action=P2P_MENU)
    builder.row(
        InlineKeyboardButton(
            text="⬅️ Назад",
            callback_data=MenuAction.BACK.value,
        )
    )
    sent = await bot.send_message(chat_id, text, reply_markup=builder.as_markup())
    if state:
        await state.update_data(last_menu_message_id=sent.message_id, last_menu_chat_id=sent.chat.id)


@router.callback_query(F.data == MenuAction.P2P.value)
async def p2p_menu(callback: CallbackQuery, state: FSMContext) -> None:
    await _show_p2p_menu(callback, state=state)
    await callback.answer()


@router.callback_query(F.data == P2P_MENU)
async def p2p_menu_back(callback: CallbackQuery, state: FSMContext) -> None:
    await _show_p2p_menu(callback, state=state)
    await callback.answer()


@router.callback_query(F.data == P2P_PROFILE)
async def p2p_profile(callback: CallbackQuery, state: FSMContext) -> None:
    deps = get_deps()
    user = callback.from_user
    if not user:
        await callback.answer()
        return
    await state.update_data(back_action=P2P_MENU)
    await _delete_callback_message(callback)
    await _send_profile(user, callback.message.chat.id, callback.bot, state=state)
    await callback.answer()


@router.callback_query(F.data == P2P_ADS)
async def p2p_ads_menu(callback: CallbackQuery, state: FSMContext) -> None:
    deps = get_deps()
    user = callback.from_user
    if not user:
        await callback.answer()
        return
    await state.update_data(back_action=P2P_MENU)
    trading_enabled = await deps.advert_service.trading_enabled(user.id)
    ads = await deps.advert_service.list_user_ads(user.id)
    builder = _ad_manage_keyboard(trading_enabled)
    for ad in ads:
        builder.row(
            InlineKeyboardButton(
                text=_ad_button_label(ad),
                callback_data=f"{P2P_AD_VIEW_PREFIX}{ad.id}",
            )
        )
    # back navigation via reply keyboard
    await _delete_callback_message(callback)
    await callback.message.answer(
        _ad_manage_text(trading_enabled),
        reply_markup=builder.as_markup(),
    )
    await callback.answer()


async def _render_p2p_deals(
    callback: CallbackQuery, *, page: int, state: FSMContext | None = None
) -> None:
    deps = get_deps()
    user = callback.from_user
    if not user:
        return
    deals = await deps.deal_service.list_user_deals(user.id)
    if not deals:
        builder = InlineKeyboardBuilder()
        # back navigation via reply keyboard
        if state:
            await state.update_data(back_action=P2P_MENU)
        await _delete_callback_message(callback)
        builder.button(text="⬅️ Назад", callback_data=MenuAction.BACK.value)
        sent = await callback.message.answer("У тебя пока нет сделок", reply_markup=builder.as_markup())
        if state:
            await state.update_data(last_menu_message_id=sent.message_id, last_menu_chat_id=sent.chat.id)
        return
    total_pages = max(1, (len(deals) + 7 - 1) // 7)
    page = max(0, min(page, total_pages - 1))
    start = page * 7
    chunk = deals[start : start + 7]
    total = len(deals)
    success = sum(1 for item in deals if item.status == DealStatus.COMPLETED)
    failed = sum(1 for item in deals if item.status in {DealStatus.CANCELED, DealStatus.EXPIRED})
    text = (
        "<b>📂 Мои сделки</b>\n"
        f"Всего: {total}\n"
        f"Успешных: {success}\n"
        f"Отменённых/истёкших: {failed}\n"
        f"Страница {page + 1}/{total_pages}\n\n"
        "Выбери сделку кнопками ниже."
    )
    builder = InlineKeyboardBuilder()
    for index, deal in enumerate(chunk, start=start + 1):
        builder.row(
            InlineKeyboardButton(
                text=_p2p_deal_button_label(deal, user.id, index),
                callback_data=f"{P2P_MY_DEALS_VIEW_PREFIX}{page}:{deal.id}",
            )
        )
    if total_pages > 1:
        nav_buttons = []
        if page > 0:
            nav_buttons.append(
                InlineKeyboardButton(
                    text=f"Стр. {page}",
                    callback_data=f"{P2P_MY_DEALS_PAGE_PREFIX}{page - 1}",
                )
            )
        if page < total_pages - 1:
            nav_buttons.append(
                InlineKeyboardButton(
                    text=f"Стр. {page + 2} ➡️",
                    callback_data=f"{P2P_MY_DEALS_PAGE_PREFIX}{page + 1}",
                )
            )
        if nav_buttons:
            builder.row(*nav_buttons)
    # back navigation via reply keyboard
    if state:
        await state.update_data(back_action=P2P_MENU)
    builder.row(
        InlineKeyboardButton(
            text="⬅️ Назад",
            callback_data=MenuAction.BACK.value,
        )
    )
    await _delete_callback_message(callback)
    sent = await callback.message.answer(text, reply_markup=builder.as_markup())
    if state:
        await state.update_data(last_menu_message_id=sent.message_id, last_menu_chat_id=sent.chat.id)


@router.callback_query(F.data == P2P_MY_DEALS)
async def p2p_my_deals(callback: CallbackQuery, state: FSMContext) -> None:
    await _render_p2p_deals(callback, page=0, state=state)
    await callback.answer()


@router.callback_query(F.data.startswith(P2P_MY_DEALS_PAGE_PREFIX))
async def p2p_my_deals_page(callback: CallbackQuery, state: FSMContext) -> None:
    payload = callback.data[len(P2P_MY_DEALS_PAGE_PREFIX) :]
    if not payload.isdigit():
        await callback.answer()
        return
    await _render_p2p_deals(callback, page=int(payload), state=state)
    await callback.answer()


@router.callback_query(F.data.startswith(P2P_MY_DEALS_VIEW_PREFIX))
async def p2p_my_deal_view(callback: CallbackQuery, state: FSMContext) -> None:
    deps = get_deps()
    user = callback.from_user
    if not user:
        await callback.answer()
        return
    payload = callback.data[len(P2P_MY_DEALS_VIEW_PREFIX) :]
    try:
        page_str, deal_id = payload.split(":", 1)
        page = int(page_str)
    except ValueError:
        await callback.answer()
        return
    deal = await deps.deal_service.get_deal(deal_id)
    if not deal or user.id not in {deal.seller_id, deal.buyer_id}:
        await callback.answer("Сделка недоступна", show_alert=True)
        return
    buyer_profile = await deps.user_service.profile_of(deal.buyer_id) if deal.buyer_id else None
    seller_profile = await deps.user_service.profile_of(deal.seller_id)
    await _delete_callback_message(callback)
    await state.update_data(back_action=f"{P2P_MY_DEALS_PAGE_PREFIX}{page}")
    await _send_deal_card(
        bot=callback.bot,
        chat_id=callback.message.chat.id,
        deal=deal,
        viewer_id=user.id,
        seller_profile=seller_profile,
        buyer_profile=buyer_profile,
        back_page=page,
        cancel_page=page,
        back_page_prefix=P2P_MY_DEALS_PAGE_PREFIX,
    )
    await callback.answer()


@router.callback_query(F.data == P2P_TRADING_TOGGLE)
async def p2p_trading_toggle(callback: CallbackQuery, state: FSMContext) -> None:
    deps = get_deps()
    user = callback.from_user
    if not user:
        await callback.answer()
        return
    enabled = await deps.advert_service.trading_enabled(user.id)
    await deps.advert_service.set_trading(user.id, not enabled)
    await p2p_ads_menu(callback, state)


@router.callback_query(F.data == P2P_AD_CREATE)
async def p2p_ad_create_start(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await state.set_state(P2PAdCreateState.choosing_side)
    await state.update_data(back_action=P2P_ADS)
    builder = InlineKeyboardBuilder()
    builder.button(text="Купить", callback_data="p2p:create:buy")
    builder.button(text="Продать", callback_data="p2p:create:sell")
    builder.button(text="Отменить", callback_data=P2P_CREATE_CANCEL)
    builder.adjust(2)
    await callback.message.answer(
        "Хотели бы купить или продать USDT",
        reply_markup=builder.as_markup(),
    )
    await callback.answer()


@router.callback_query(F.data == P2P_CREATE_CANCEL, P2PAdCreateState.choosing_side)
async def p2p_ad_create_cancel(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    with suppress(TelegramBadRequest):
        await callback.message.delete()
    await callback.answer()


@router.callback_query(
    F.data.in_({"p2p:create:buy", "p2p:create:sell"}), P2PAdCreateState.choosing_side
)
async def p2p_ad_create_side(callback: CallbackQuery, state: FSMContext) -> None:
    side = AdvertSide.BUY if callback.data.endswith("buy") else AdvertSide.SELL
    await state.update_data(side=side)
    await state.set_state(P2PAdCreateState.waiting_volume)
    deps = get_deps()
    balance = await deps.deal_service.balance_of(callback.from_user.id)
    builder = InlineKeyboardBuilder()
    builder.button(text="Макс объём", callback_data=P2P_VOLUME_MAX)
    await callback.message.answer(
        f"Укажи доступный объём в USDT\nТвой баланс: {_format_decimal(balance)} USDT",
        reply_markup=builder.as_markup(),
    )
    await callback.answer()


@router.message(P2PAdCreateState.waiting_volume)
async def p2p_ad_create_volume(message: Message, state: FSMContext) -> None:
    deps = get_deps()
    balance = await deps.deal_service.balance_of(message.from_user.id)
    try:
        volume = Decimal(message.text.replace(",", "."))
    except Exception:
        await message.answer("Введи число USDT, например: 10.5")
        return
    if volume <= Decimal("0"):
        await message.answer("Объём должен быть больше нуля")
        return
    if volume > balance:
        await message.answer(
            f"Недостаточно баланса. Доступно: {_format_decimal(balance)} USDT"
        )
        return
    await state.update_data(volume=volume)
    await state.set_state(P2PAdCreateState.waiting_price)
    await message.answer("Укажи цену за 1 USDT в RUB")


@router.callback_query(F.data == P2P_VOLUME_MAX, P2PAdCreateState.waiting_volume)
async def p2p_ad_create_volume_max(callback: CallbackQuery, state: FSMContext) -> None:
    deps = get_deps()
    balance = await deps.deal_service.balance_of(callback.from_user.id)
    if balance <= Decimal("0"):
        await callback.answer("Баланс пуст", show_alert=True)
        return
    await state.update_data(volume=balance)
    await state.set_state(P2PAdCreateState.waiting_price)
    await callback.message.answer("Укажи цену за 1 USDT в RUB")
    await callback.answer()


@router.message(P2PAdCreateState.waiting_price)
async def p2p_ad_create_price(message: Message, state: FSMContext) -> None:
    try:
        price = Decimal(message.text.replace(",", "."))
    except Exception:
        await message.answer("Введи цену, например: 74.5")
        return
    if price <= Decimal("0"):
        await message.answer("Цена должна быть больше нуля")
        return
    await state.update_data(price=price)
    await state.set_state(P2PAdCreateState.waiting_limits)
    await message.answer("Укажи лимиты в RUB через дефис, например: 1000-10000")


@router.message(P2PAdCreateState.waiting_limits)
async def p2p_ad_create_limits(message: Message, state: FSMContext) -> None:
    raw = message.text.replace(",", ".").replace("–", "-").replace("—", "-").strip()
    if "-" not in raw:
        await message.answer("Формат лимитов: минимум-максимум (например: 1000-10000)")
        return
    parts = [part.strip() for part in raw.split("-", 1)]
    if len(parts) != 2 or not parts[0] or not parts[1]:
        await message.answer("Формат лимитов: минимум-максимум (например: 1000-10000)")
        return
    try:
        min_rub = Decimal(parts[0])
        max_rub = Decimal(parts[1])
    except Exception:
        await message.answer("Введи числа, например: 1000-10000")
        return
    if min_rub <= Decimal("0") or max_rub <= Decimal("0") or min_rub > max_rub:
        await message.answer("Некорректные лимиты")
        return
    data = await state.get_data()
    volume = data.get("volume")
    price = data.get("price")
    if volume is not None and price is not None:
        max_possible = Decimal(str(volume)) * Decimal(str(price))
        if max_possible > 0 and (max_rub > max_possible or min_rub > max_possible):
            await message.answer(
                "Не хватает объёма для такого лимита. "
                "Введи лимит меньше или равный доступному объёму."
            )
            return
    await state.update_data(min_rub=min_rub, max_rub=max_rub, banks=[])
    await state.set_state(P2PAdCreateState.choosing_banks)
    await message.answer(
        "Выбери банки для сделки",
        reply_markup=_p2p_bank_keyboard([]).as_markup(),
    )


@router.callback_query(F.data.startswith(P2P_BANK_PREFIX), P2PAdCreateState.choosing_banks)
async def p2p_ad_create_banks(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    banks = set(data.get("banks") or [])
    action = callback.data[len(P2P_BANK_PREFIX) :]
    if action == "done":
        if not banks:
            await callback.answer("Отметь хотя бы один банк", show_alert=True)
            return
        await state.update_data(banks=list(banks))
        await state.set_state(P2PAdCreateState.waiting_terms)
        skip_builder = InlineKeyboardBuilder()
        skip_builder.button(text="Пропустить", callback_data=P2P_TERMS_SKIP)
        await callback.message.answer(
            "Отправь условия сделки или нажми «Пропустить».",
            reply_markup=skip_builder.as_markup(),
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
            reply_markup=_p2p_bank_keyboard(list(banks)).as_markup()
        )
    await callback.answer()


@router.callback_query(F.data == P2P_TERMS_SKIP, P2PAdCreateState.waiting_terms)
async def p2p_ad_terms_skip(callback: CallbackQuery, state: FSMContext) -> None:
    await _create_ad_from_state(callback, state, terms=None)
    await callback.answer()


@router.message(P2PAdCreateState.waiting_terms)
async def p2p_ad_terms(message: Message, state: FSMContext) -> None:
    terms = message.text.strip()
    await _create_ad_from_state(message, state, terms=terms)


async def _create_ad_from_state(message_or_cb, state: FSMContext, *, terms: str | None) -> None:
    data = await state.get_data()
    deps = get_deps()
    user = message_or_cb.from_user
    if not user:
        return
    balance = await deps.deal_service.balance_of(user.id)
    volume = Decimal(str(data.get("volume") or "0"))
    price = Decimal(str(data.get("price") or "0"))
    min_rub = Decimal(str(data.get("min_rub") or "0"))
    max_rub = Decimal(str(data.get("max_rub") or "0"))
    if volume > balance:
        if hasattr(message_or_cb, "answer"):
            await message_or_cb.answer(
                f"Недостаточно баланса. Доступно: {_format_decimal(balance)} USDT"
            )
        return
    max_possible = volume * price
    if max_possible > 0 and (min_rub > max_possible or max_rub > max_possible):
        if hasattr(message_or_cb, "answer"):
            await message_or_cb.answer(
                "Не хватает объёма для такого лимита. "
                "Введи лимит меньше или равный доступному объёму."
            )
        return
    try:
        ad = await deps.advert_service.create_ad(
            owner_id=user.id,
            side=data["side"],
            total_usdt=volume,
            price_rub=price,
            min_rub=min_rub,
            max_rub=max_rub,
            banks=data["banks"],
            terms=terms,
        )
    except Exception as exc:
        if hasattr(message_or_cb, "answer"):
            await message_or_cb.answer(f"Не удалось создать объявление: {exc}")
        return
    await state.clear()
    trading_enabled = await deps.advert_service.trading_enabled(user.id)
    text = _ad_owner_card(ad, trading_enabled)
    markup = _ad_owner_keyboard(ad).as_markup()
    if isinstance(message_or_cb, CallbackQuery) and message_or_cb.message:
        with suppress(TelegramBadRequest):
            await message_or_cb.message.delete()
        return
    if hasattr(message_or_cb, "answer"):
        await message_or_cb.answer(text, reply_markup=markup)


@router.callback_query(F.data.startswith(P2P_AD_VIEW_PREFIX))
async def p2p_ad_view(callback: CallbackQuery, state: FSMContext) -> None:
    deps = get_deps()
    advert_id = callback.data[len(P2P_AD_VIEW_PREFIX) :]
    ad = await deps.advert_service.get_ad(advert_id)
    if not ad:
        await callback.answer("Объявление не найдено", show_alert=True)
        return
    trading_enabled = await deps.advert_service.trading_enabled(ad.owner_id)
    with suppress(Exception):
        await _ad_available_usdt(deps, ad)
    await state.update_data(back_action=P2P_ADS)
    await _delete_callback_message(callback)
    await callback.message.answer(
        _ad_owner_card(ad, trading_enabled),
        reply_markup=_ad_owner_keyboard(ad).as_markup(),
    )
    await callback.answer()


@router.callback_query(F.data.startswith(P2P_AD_TOGGLE_PREFIX))
async def p2p_ad_toggle(callback: CallbackQuery, state: FSMContext) -> None:
    deps = get_deps()
    payload = callback.data[len(P2P_AD_TOGGLE_PREFIX) :]
    if ":" not in payload:
        await callback.answer()
        return
    advert_id, mode = payload.split(":", 1)
    active = mode == "on"
    if active:
        ad_check = await deps.advert_service.get_ad(advert_id)
        if ad_check:
            available = await _ad_available_usdt(deps, ad_check)
            if available <= 0 or ad_check.min_rub > available * ad_check.price_rub:
                await callback.answer("Недостаточно баланса для публикации", show_alert=True)
                return
    try:
        ad = await deps.advert_service.toggle_active(advert_id, active)
    except Exception as exc:
        await callback.answer(str(exc), show_alert=True)
        return
    trading_enabled = await deps.advert_service.trading_enabled(ad.owner_id)
    await state.update_data(back_action=P2P_ADS)
    await _delete_callback_message(callback)
    await callback.message.answer(
        _ad_owner_card(ad, trading_enabled),
        reply_markup=_ad_owner_keyboard(ad).as_markup(),
    )
    await callback.answer()


@router.callback_query(F.data.startswith(P2P_AD_DELETE_PREFIX))
async def p2p_ad_delete(callback: CallbackQuery, state: FSMContext) -> None:
    deps = get_deps()
    advert_id = callback.data[len(P2P_AD_DELETE_PREFIX) :]
    await deps.advert_service.delete_ad(advert_id)
    await p2p_ads_menu(callback, state)


@router.callback_query(F.data.startswith(P2P_AD_EDIT_PREFIX))
async def p2p_ad_edit_start(callback: CallbackQuery, state: FSMContext) -> None:
    deps = get_deps()
    payload = callback.data[len(P2P_AD_EDIT_PREFIX) :]
    if ":" not in payload:
        await callback.answer()
        return
    advert_id, field = payload.split(":", 1)
    ad = await deps.advert_service.get_ad(advert_id)
    if not ad:
        await callback.answer("Объявление не найдено", show_alert=True)
        return
    await state.clear()
    await state.update_data(ad_id=advert_id, field=field)
    await state.update_data(back_action=P2P_ADS)
    if field == "banks":
        await state.set_state(P2PAdEditState.choosing_banks)
        await callback.message.answer(
            "Выбери банки для сделки",
            reply_markup=_p2p_bank_keyboard(ad.banks).as_markup(),
        )
        await callback.answer()
        return
    if field == "terms":
        await state.set_state(P2PAdEditState.waiting_terms)
        skip_builder = InlineKeyboardBuilder()
        skip_builder.button(text="Пропустить", callback_data=P2P_TERMS_SKIP)
        await callback.message.answer(
            "Отправь условия сделки или нажми «Пропустить».",
            reply_markup=skip_builder.as_markup(),
        )
        await callback.answer()
        return
    await state.set_state(P2PAdEditState.waiting_value)
    prompt = "Укажи новую цену за 1 USDT" if field == "price" else "Укажи новый объём в USDT"
    if field == "limits":
        prompt = "Укажи новые лимиты в RUB через дефис (например: 1000-10000)"
    cancel_builder = InlineKeyboardBuilder()
    cancel_builder.button(text="Отменить", callback_data=P2P_EDIT_CANCEL)
    await callback.message.answer(prompt, reply_markup=cancel_builder.as_markup())
    await callback.answer()


@router.callback_query(F.data.startswith(P2P_BANK_PREFIX), P2PAdEditState.choosing_banks)
async def p2p_ad_edit_banks(callback: CallbackQuery, state: FSMContext) -> None:
    deps = get_deps()
    data = await state.get_data()
    advert_id = data.get("ad_id")
    ad = await deps.advert_service.get_ad(advert_id)
    if not ad:
        await callback.answer("Объявление не найдено", show_alert=True)
        return
    banks = set(ad.banks)
    action = callback.data[len(P2P_BANK_PREFIX) :]
    if action == "done":
        if not banks:
            await callback.answer("Отметь хотя бы один банк", show_alert=True)
            return
        ad = await deps.advert_service.update_ad(advert_id, banks=list(banks))
        await state.clear()
        trading_enabled = await deps.advert_service.trading_enabled(ad.owner_id)
        await callback.message.answer(
            _ad_owner_card(ad, trading_enabled),
            reply_markup=_ad_owner_keyboard(ad).as_markup(),
        )
        await callback.answer()
        return
    if action in BANK_OPTIONS:
        if action in banks:
            banks.remove(action)
        else:
            banks.add(action)
        await deps.advert_service.update_ad(advert_id, banks=list(banks))
        await callback.message.edit_reply_markup(
            reply_markup=_p2p_bank_keyboard(list(banks)).as_markup()
        )
    await callback.answer()


@router.callback_query(F.data == P2P_TERMS_SKIP, P2PAdEditState.waiting_terms)
async def p2p_ad_edit_terms_skip(callback: CallbackQuery, state: FSMContext) -> None:
    await _save_ad_terms(callback, state, terms=None, send_card=False)
    with suppress(TelegramBadRequest):
        await callback.message.delete()
    await callback.answer()


@router.message(P2PAdEditState.waiting_terms)
async def p2p_ad_edit_terms(message: Message, state: FSMContext) -> None:
    await _save_ad_terms(message, state, terms=message.text.strip())


async def _save_ad_terms(
    message_or_cb,
    state: FSMContext,
    *,
    terms: str | None,
    send_card: bool = True,
) -> None:
    deps = get_deps()
    data = await state.get_data()
    advert_id = data.get("ad_id")
    try:
        ad = await deps.advert_service.update_ad(advert_id, terms=terms)
    except Exception as exc:
        if hasattr(message_or_cb, "answer"):
            await message_or_cb.answer(f"Не удалось сохранить: {exc}")
        return
    await state.clear()
    if not send_card:
        return
    trading_enabled = await deps.advert_service.trading_enabled(ad.owner_id)
    text = _ad_owner_card(ad, trading_enabled)
    markup = _ad_owner_keyboard(ad).as_markup()
    if isinstance(message_or_cb, CallbackQuery) and message_or_cb.message:
        await message_or_cb.message.answer(text, reply_markup=markup)
    elif hasattr(message_or_cb, "answer"):
        await message_or_cb.answer(text, reply_markup=markup)


@router.message(P2PAdEditState.waiting_value)
async def p2p_ad_edit_value(message: Message, state: FSMContext) -> None:
    deps = get_deps()
    data = await state.get_data()
    advert_id = data.get("ad_id")
    field = data.get("field")
    ad = await deps.advert_service.get_ad(advert_id)
    if not ad:
        await message.answer("Объявление не найдено")
        await state.clear()
        return
    raw = message.text.replace(",", ".").replace("–", "-").replace("—", "-").strip()
    if field == "limits" or ("-" in raw and field not in {"price", "volume"}):
        if "-" not in raw:
            await message.answer("Формат лимитов: минимум-максимум (например: 1000-10000)")
            return
        parts = [part.strip() for part in raw.split("-", 1)]
        if len(parts) != 2 or not parts[0] or not parts[1]:
            await message.answer("Формат лимитов: минимум-максимум (например: 1000-10000)")
            return
        try:
            min_rub = Decimal(parts[0])
            max_rub = Decimal(parts[1])
        except Exception:
            await message.answer("Введи числа, например: 1000-10000")
            return
        if min_rub <= 0 or max_rub <= 0 or min_rub > max_rub:
            await message.answer("Некорректные лимиты")
            return
        balance = await deps.deal_service.balance_of(ad.owner_id)
        available = min(ad.total_usdt, balance)
        max_possible = available * ad.price_rub
        if max_possible > 0 and (max_rub > max_possible or min_rub > max_possible):
            await message.answer(
                "Не хватает объёма для такого лимита. "
                "Введи лимит меньше или равный доступному объёму."
            )
            return
        ad = await deps.advert_service.update_ad(advert_id, min_rub=min_rub, max_rub=max_rub)
    else:
        try:
            value = Decimal(raw)
        except Exception:
            await message.answer("Введи корректное число")
            return
        if value <= 0:
            await message.answer("Значение должно быть больше нуля")
            return
        if field == "price":
            balance = await deps.deal_service.balance_of(ad.owner_id)
            available = min(ad.total_usdt, balance)
            max_possible = available * value
            if max_possible > 0 and (ad.min_rub > max_possible or ad.max_rub > max_possible):
                await message.answer(
                    "Не хватает объёма для такого лимита. "
                    "Введи лимит меньше или равный доступному объёму."
                )
                return
            ad = await deps.advert_service.update_ad(advert_id, price_rub=value)
        elif field == "volume":
            balance = await deps.deal_service.balance_of(ad.owner_id)
            if value > balance:
                await message.answer(
                    f"Недостаточно баланса. Доступно: {_format_decimal(balance)} USDT"
                )
                return
            max_possible = value * ad.price_rub
            if max_possible > 0 and (ad.min_rub > max_possible or ad.max_rub > max_possible):
                await message.answer(
                    "Не хватает объёма для такого лимита. "
                    "Введи лимит меньше или равный доступному объёму."
                )
                return
            ad = await deps.advert_service.update_ad(
                advert_id,
                total_usdt=value,
                remaining_usdt=value,
            )
        else:
            await message.answer("Неизвестное поле")
            return
    await state.clear()
    trading_enabled = await deps.advert_service.trading_enabled(ad.owner_id)
    await message.answer(
        _ad_owner_card(ad, trading_enabled),
        reply_markup=_ad_owner_keyboard(ad).as_markup(),
    )


@router.callback_query(F.data == P2P_EDIT_CANCEL, P2PAdEditState.waiting_value)
async def p2p_ad_edit_cancel(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    with suppress(TelegramBadRequest):
        await callback.message.delete()
    await callback.answer()


@router.callback_query(F.data == P2P_BUY)
async def p2p_buy_list(callback: CallbackQuery, state: FSMContext) -> None:
    deps = get_deps()
    user = callback.from_user
    if not user:
        await callback.answer()
        return
    ads = await deps.advert_service.list_public_ads(AdvertSide.SELL)
    builder = InlineKeyboardBuilder()
    if not ads:
        # back navigation via reply keyboard
        await state.update_data(back_action=P2P_MENU, p2p_last_list=P2P_BUY)
        await _delete_callback_message(callback)
        await callback.message.answer("Пока нет доступных объявлений.", reply_markup=builder.as_markup())
        await callback.answer()
        return
    for ad in ads:
        available = await _ad_available_usdt(deps, ad)
        if available <= 0 or not ad.active:
            continue
        profile = await deps.user_service.profile_of(ad.owner_id)
        name = _profile_display_name(profile)
        builder.row(
            InlineKeyboardButton(
                text=_ad_public_button_label(ad, name),
                callback_data=f"{P2P_PUBLIC_VIEW_PREFIX}{ad.id}",
            )
        )
    if not builder._buttons:
        await state.update_data(back_action=P2P_MENU, p2p_last_list=P2P_BUY)
        await _delete_callback_message(callback)
        await callback.message.answer("Пока нет доступных объявлений.", reply_markup=builder.as_markup())
        await callback.answer()
        return
    # back navigation via reply keyboard
    await state.update_data(back_action=P2P_MENU, p2p_last_list=P2P_BUY)
    await _delete_callback_message(callback)
    await callback.message.answer(
        "💠 Доступные объявления на покупку:",
        reply_markup=builder.as_markup(),
    )
    await callback.answer()


@router.callback_query(F.data == P2P_SELL)
async def p2p_sell_list(callback: CallbackQuery, state: FSMContext) -> None:
    deps = get_deps()
    user = callback.from_user
    if not user:
        await callback.answer()
        return
    ads = await deps.advert_service.list_public_ads(AdvertSide.BUY)
    builder = InlineKeyboardBuilder()
    if not ads:
        # back navigation via reply keyboard
        await state.update_data(back_action=P2P_MENU, p2p_last_list=P2P_SELL)
        await _delete_callback_message(callback)
        await callback.message.answer("Пока нет доступных объявлений.", reply_markup=builder.as_markup())
        await callback.answer()
        return
    for ad in ads:
        available = await _ad_available_usdt(deps, ad)
        if available <= 0 or not ad.active:
            continue
        profile = await deps.user_service.profile_of(ad.owner_id)
        name = _profile_display_name(profile)
        builder.row(
            InlineKeyboardButton(
                text=_ad_public_button_label(ad, name),
                callback_data=f"{P2P_PUBLIC_VIEW_PREFIX}{ad.id}",
            )
        )
    if not builder._buttons:
        await state.update_data(back_action=P2P_MENU, p2p_last_list=P2P_SELL)
        await _delete_callback_message(callback)
        await callback.message.answer("Пока нет доступных объявлений.", reply_markup=builder.as_markup())
        await callback.answer()
        return
    # back navigation via reply keyboard
    await state.update_data(back_action=P2P_MENU, p2p_last_list=P2P_SELL)
    await _delete_callback_message(callback)
    await callback.message.answer(
        "💠 Доступные объявления на продажу:",
        reply_markup=builder.as_markup(),
    )
    await callback.answer()


@router.callback_query(F.data.startswith(P2P_PUBLIC_VIEW_PREFIX))
async def p2p_public_view(callback: CallbackQuery, state: FSMContext) -> None:
    deps = get_deps()
    advert_id = callback.data[len(P2P_PUBLIC_VIEW_PREFIX) :]
    ad = await deps.advert_service.get_ad(advert_id)
    if not ad or not ad.active:
        await callback.answer("Объявление не найдено", show_alert=True)
        return
    if not await deps.advert_service.trading_enabled(ad.owner_id):
        await callback.answer("Объявление недоступно", show_alert=True)
        return
    available = await _ad_available_usdt(deps, ad)
    if available <= 0 or not ad.active:
        await callback.answer("Объявление недоступно", show_alert=True)
        return
    builder = InlineKeyboardBuilder()
    action_text = "Купить" if ad.side == AdvertSide.SELL else "Продать"
    builder.button(text=action_text, callback_data=f"{P2P_PUBLIC_OFFER_PREFIX}{ad.id}")
    # back navigation via reply keyboard
    builder.adjust(1)
    data = await state.get_data()
    back_action = data.get("p2p_last_list") or P2P_MENU
    await state.update_data(back_action=back_action)
    await _delete_callback_message(callback)
    await callback.message.answer(_ad_public_card(ad), reply_markup=builder.as_markup())
    await callback.answer()


@router.callback_query(F.data.startswith(P2P_PUBLIC_OFFER_PREFIX))
async def p2p_offer_start(callback: CallbackQuery, state: FSMContext) -> None:
    advert_id = callback.data[len(P2P_PUBLIC_OFFER_PREFIX) :]
    deps = get_deps()
    ad = await deps.advert_service.get_ad(advert_id)
    if not ad:
        await callback.answer("Объявление недоступно", show_alert=True)
        return
    if callback.from_user and callback.from_user.id == ad.owner_id:
        await callback.answer("Нельзя создать сделку по своему объявлению", show_alert=True)
        return
    data = await state.get_data()
    back_action = data.get("p2p_last_list") or P2P_MENU
    await state.clear()
    await state.update_data(advert_id=advert_id, back_action=back_action)
    await state.set_state(P2PDealState.waiting_amount)
    await callback.message.answer("Укажи сумму в RUB для сделки")
    await callback.answer()


@router.message(P2PDealState.waiting_amount)
async def p2p_offer_amount(message: Message, state: FSMContext) -> None:
    deps = get_deps()
    data = await state.get_data()
    advert_id = data.get("advert_id")
    ad = await deps.advert_service.get_ad(advert_id)
    if not ad or not ad.active:
        await message.answer("Объявление недоступно")
        await state.clear()
        return
    try:
        rub_amount = Decimal(message.text.replace(",", "."))
    except InvalidOperation:
        await message.answer("Введи сумму в RUB, например: 5000")
        return
    if rub_amount < ad.min_rub or rub_amount > ad.max_rub:
        await message.answer("Сумма должна быть в пределах лимитов объявления")
        return
    base_usdt = rub_amount / ad.price_rub
    seller_id = ad.owner_id if ad.side == AdvertSide.SELL else message.from_user.id
    seller_balance = await deps.deal_service.balance_of(seller_id)
    available = min(ad.remaining_usdt, seller_balance)
    if base_usdt > available:
        await message.answer("В объявлении недостаточно объёма")
        return
    user = message.from_user
    if not user:
        return
    if ad.side == AdvertSide.SELL:
        seller_id = ad.owner_id
        buyer_id = user.id
    else:
        seller_id = user.id
        buyer_id = ad.owner_id
    try:
        deal = await deps.deal_service.create_p2p_deal(
            seller_id=seller_id,
            buyer_id=buyer_id,
            usd_amount=rub_amount,
            rate=ad.price_rub,
            advert_id=ad.id,
            comment=ad.terms,
        )
        await deps.advert_service.reduce_volume(ad.id, base_usdt)
    except Exception as exc:
        await message.answer(f"Не удалось создать сделку: {exc}")
        await state.clear()
        return
    try:
        invoice = await deps.crypto_pay.create_invoice(
            amount=deal.usdt_amount,
            currency="USDT",
            description=f"Сделка {deal.hashtag} на {deal.usd_amount} RUB",
            payload=deal.id,
        )
        await deps.deal_service.attach_invoice(deal.id, invoice.invoice_id, invoice.pay_url)
    except Exception as exc:
        with suppress(Exception):
            await deps.deal_service.cancel_deal(deal.id, seller_id)
        with suppress(Exception):
            await deps.advert_service.restore_volume(ad.id, base_usdt)
        await message.answer(f"Не удалось создать счет: {exc}")
        await state.clear()
        return
    await state.clear()
    info_builder = InlineKeyboardBuilder()
    info_builder.button(text="К сделке", callback_data=f"{DEAL_INFO_PREFIX}{deal.id}")
    await message.answer(
        f"✅ Сделка {deal.hashtag} создана.\nОжидаем оплату продавца.",
        reply_markup=info_builder.as_markup(),
    )
    if buyer_id != message.from_user.id:
        await message.bot.send_message(
            buyer_id,
            f"✅ Сделка {deal.hashtag} создана.\nОжидаем оплату продавца.",
            reply_markup=info_builder.as_markup(),
        )
    amount = Decimal(str(invoice.amount)).quantize(Decimal("0.01"), rounding=ROUND_UP)
    pay_builder = InlineKeyboardBuilder()
    pay_builder.button(text="💸 Оплатить", url=invoice.pay_url)
    pay_builder.adjust(1)
    await message.bot.send_message(
        deal.seller_id,
        f"✅ Сделка {deal.hashtag} закреплена за тобой.\n"
        f"Оплати {format(amount, 'f')} USDT\n"
        "После оплаты начнется отсчет времени для открытия спора.",
        reply_markup=pay_builder.as_markup(),
    )
