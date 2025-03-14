from aiogram import types

from aiogram.types import CallbackQuery
from aiogram.types import FSInputFile
import sqlite3

from database.crud import get_location_by_number, get_connected_locations
from keyboards.location_keyboard import get_location_keyboard
from models.location import Location
from aiogram import Router
from aiogram.types import CallbackQuery
import logging


callback_router = Router()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@callback_router.callback_query(lambda c: c.data == 'action_move')
async def handle_action_move(callback_query: CallbackQuery):
    """Обрабатывает действие 'Перейти в другую локацию'."""
    user_id = callback_query.from_user.id

    try:
        with sqlite3.connect('db/game.db') as conn:
            cursor = conn.cursor()

            # Получаем текущую локацию игрока
            cursor.execute('SELECT current_location FROM characters WHERE user_id=?', (user_id,))
            current_location = cursor.fetchone()

            if current_location:
                current_location_id = current_location[0]

                # Получаем связанные локации
                connected_locations = get_connected_locations(cursor, current_location_id)
                if connected_locations:
                    # Создаем клавиатуру с кнопками для выбора локаций
                    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
                        [types.InlineKeyboardButton(text=loc[1], callback_data=f"move_to_{loc[2]}")]  # loc[1] — имя локации, loc[2] — номер
                        for loc in connected_locations
                    ])
                    await callback_query.message.answer("Выберите локацию для перехода:", reply_markup=keyboard)
                else:
                    await callback_query.message.answer("Нет доступных локаций для перехода.")
            else:
                await callback_query.message.answer("Текущая локация не найдена.")
    except sqlite3.Error as e:
        await callback_query.message.answer(f'Произошла ошибка при работе с базой данных: {e}')
    @callback_router.callback_query(lambda c: c.data.startswith('move_to_'))
    async def handle_move_to_location(callback_query: CallbackQuery):
        """Обрабатывает выбор локации для перехода."""
        user_id = callback_query.from_user.id
        location_number = int(callback_query.data.split('_')[2])  # move_to_1 → 1

        try:
            with sqlite3.connect('db/game.db') as conn:
                cursor = conn.cursor()

                # Загружаем выбранную локацию
                location = get_location_by_number(cursor, location_number)
                if location:
                    # Обновляем текущую локацию игрока (если нужно)
                    cursor.execute('UPDATE characters SET current_location=? WHERE user_id=?',
                                   (location.number, user_id))
                    conn.commit()

                    # Отправляем описание и изображение новой локации
                    keyboard = get_location_keyboard(location)
                    photo = FSInputFile(location.image)
                    await callback_query.message.answer_photo(
                        photo=photo,
                        caption=f"Вы перешли в локацию: {location.name}\n\n{location.description}",
                        reply_markup=keyboard
                    )
                else:
                    await callback_query.message.answer("Локация не найдена.")
        except sqlite3.Error as e:
            await callback_query.message.answer(f'Произошла ошибка при работе с базой данных: {e}')
        except FileNotFoundError:
            await callback_query.message.answer("Изображение для локации не найдено.")