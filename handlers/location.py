import sqlite3
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import FSInputFile  # Для загрузки изображений с диска
from database.crud import get_location_by_number, get_connected_locations
from keyboards.location_keyboard import get_location_keyboard


def register_handlers(dp: Dispatcher):
    @dp.message(Command("go"))
    async def go_to_location(message: types.Message):
        """Обрабатывает команду /go <номер локации>."""
        try:
            # Получаем номер локации из сообщения
            location_number = int(message.text.split()[1])  # /go 1 → 1
        except (IndexError, ValueError):
            await message.reply("Используйте команду так: /go <номер локации>")
            return

        try:
            with sqlite3.connect('game.db') as conn:
                cursor = conn.cursor()

                # Загружаем локацию по номеру
                location = get_location_by_number(cursor, location_number)
                if location:
                    # Получаем клавиатуру для локации
                    keyboard = get_location_keyboard(location)

                    # Загружаем изображение с диска
                    photo = FSInputFile(location.image)
                    await message.reply_photo(
                        photo=photo,
                        caption=f"Вы находитесь в локации: {location.name}\n\n{location.description}",
                        reply_markup=keyboard
                    )

                    # Получаем связанные локации
                    connected_locations = get_connected_locations(cursor, location.id)
                    if connected_locations:
                        # Создаем клавиатуру для перехода
                        move_keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
                            [types.InlineKeyboardButton(text=loc[1], callback_data=f"move_to_{loc[2]}")]  # loc[1] — имя локации, loc[2] — номер
                            for loc in connected_locations
                        ])
                        await message.answer("Выберите локацию для перехода:", reply_markup=move_keyboard)
                    else:
                        await message.answer("Нет доступных локаций для перехода.")
                else:
                    await message.reply("Локация с таким номером не найдена.")
        except sqlite3.Error as e:
            await message.reply(f'Произошла ошибка при работе с базой данных: {e}')
        except FileNotFoundError:
            await message.reply("Изображение для локации не найдено.")