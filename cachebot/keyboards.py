from __future__ import annotations

from enum import Enum

from aiogram.types import InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from cachebot.models.user import UserRole


class MenuButtons(str, Enum):
    SHOW_MENU = "📋 Меню"
    ADMIN_PANEL = "🛠 Админ панель"


class MenuAction(str, Enum):
    SELL = "menu:sell"
    OPEN_DEALS = "menu:open_deals"
    MY_DEALS = "menu:my_deals"
    PROFILE = "menu:profile"
    SETTINGS = "menu:settings"
    SETTINGS_MERCHANT = "menu:settings:merchant"
    SETTINGS_SELLER = "menu:settings:seller"
    BALANCE = "menu:balance"
    BACK = "menu:back"


def base_keyboard(is_admin: bool) -> ReplyKeyboardMarkup:
    rows = [[KeyboardButton(text=MenuButtons.SHOW_MENU.value)]]
    if is_admin:
        rows.append([KeyboardButton(text=MenuButtons.ADMIN_PANEL.value)])
    return ReplyKeyboardMarkup(
        keyboard=rows,
        resize_keyboard=True,
        input_field_placeholder="Нажми Меню",
    )


def inline_menu(role: UserRole) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    if role == UserRole.SELLER:
        builder.button(text="⚡️ Создать сделку", callback_data=MenuAction.SELL.value)
        builder.button(text="📂 Мои сделки", callback_data=MenuAction.MY_DEALS.value)
        builder.button(text="👤 Мой профиль", callback_data=MenuAction.PROFILE.value)
        builder.button(text="⚙️ Настройки", callback_data=MenuAction.SETTINGS.value)
        builder.button(text="💰 Баланс", callback_data=MenuAction.BALANCE.value)
        builder.adjust(2, 2, 1)
    else:
        builder.button(text="📋 Доступные сделки", callback_data=MenuAction.OPEN_DEALS.value)
        builder.button(text="📂 Мои сделки", callback_data=MenuAction.MY_DEALS.value)
        builder.button(text="👤 Мой профиль", callback_data=MenuAction.PROFILE.value)
        builder.button(text="⚙️ Настройки", callback_data=MenuAction.SETTINGS.value)
        builder.button(text="💰 Баланс", callback_data=MenuAction.BALANCE.value)
        builder.adjust(1, 2, 1, 1)
    return builder.as_markup()
