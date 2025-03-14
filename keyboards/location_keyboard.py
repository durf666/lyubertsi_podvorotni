from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_location_keyboard(location):
    if location.type == 'combat':
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="⚔️ Атаковать", callback_data="action_attack")],
            [InlineKeyboardButton(text="🛡️ Защищаться", callback_data="action_defend")],
            [InlineKeyboardButton(text="🏃‍♂️ Убежать", callback_data="action_flee")]
        ])
    elif location.type == 'shop':
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🛒 Купить", callback_data="action_buy")],
            [InlineKeyboardButton(text="💰 Продать", callback_data="action_sell")],
            [InlineKeyboardButton(text="🚶‍♂️ Уйти", callback_data="action_leave")]
        ])
    else:
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔍 Исследовать", callback_data="action_explore")],
            [InlineKeyboardButton(text="🚶‍♂️ Перейти в другую локацию", callback_data="action_move")]
        ])


def get_start_location_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔍 Осмотреться", callback_data="action_explore")],
        [InlineKeyboardButton(text="🚶‍♂️ Перейти в другую локацию", callback_data="action_move")]
    ])
