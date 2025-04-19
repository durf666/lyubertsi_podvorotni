from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_location_keyboard(location):

    if location.type == 'combat':
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="⚔️ Поискать приключений", callback_data="action_deeper")],
            [InlineKeyboardButton(text="🚶‍♂️ Перейти в другую локацию", callback_data="action_move")],
            [InlineKeyboardButton(text="ℹ️ Персонаж", callback_data="action_character_info")]
        ])
    elif location.type == 'shop':
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🛒 Купить", callback_data="action_shop_buy")],
            [InlineKeyboardButton(text="💰 Продать", callback_data="action_shop_sell")],
            [InlineKeyboardButton(text="🚶‍♂️ Уйти", callback_data="action_move")]
        ])
    else:
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔍 Исследовать", callback_data="action_explore")],
            [InlineKeyboardButton(text="🚶‍♂️ Перейти в другую локацию", callback_data="action_move")],
            [InlineKeyboardButton(text="ℹ️ Персонаж", callback_data="action_character_info")]
        ])


def get_start_location_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔍 Осмотреться", callback_data="action_explore")],
        [InlineKeyboardButton(text="🚶‍♂️ Перейти в другую локацию", callback_data="action_move")],
        [InlineKeyboardButton(text="ℹ️ Персонаж", callback_data="action_character_info")]
    ])


def get_shop_buy_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🌯 Купить шаурму", callback_data="action_buy_shawarma")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="action_shop_back")]
    ])

