import sqlite3
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import FSInputFile  # Используем FSInputFile для загрузки файлов с диска
from keyboards.location_keyboard import get_start_location_keyboard
from models.character import Character  # Импортируем класс Character
from handlers.callbacks import callback_router


API_TOKEN = ''

# Инициализация хранилища и бота
storage = MemoryStorage()  # Используем встроенное хранилище для FSM
bot = Bot(token=API_TOKEN)
dp = Dispatcher(storage=storage)  # Передаем хранилище в Dispatcher
# dp.include_router(command_router)  # Подключаем роутер для команд
dp.include_router(callback_router)

@dp.message(Command("start"))
async def send_welcome(message: types.Message):
    user_id = message.from_user.id
    user_name = message.from_user.first_name or message.from_user.username

    try:
        with sqlite3.connect('db/game.db') as conn:
            cursor = conn.cursor()

            # Проверяем, есть ли персонаж у игрока
            cursor.execute('SELECT * FROM characters WHERE user_id=?', (user_id,))
            user_data = cursor.fetchone()

            if user_data is None:
                # Создаем нового персонажа
                new_character = Character(user_id, user_name)
                # Сохраняем персонажа в базу данных
                new_character.save_to_db(cursor)
                conn.commit()
                await message.reply('Привет, новый игрок! Ты создал нового персонажа.')
            else:
                await message.reply(f'Привет, {user_name}! Ты вернулся в игру.')

            # Отправляем стартовую локацию
            cursor.execute('SELECT * FROM locations WHERE number=0')
            start_location = cursor.fetchone()
            if start_location:
                keyboard = get_start_location_keyboard()
                # Загружаем изображение с диска
                image_path = start_location[4]  # Путь к изображению
                photo = FSInputFile(image_path)  # Используем FSInputFile
                await message.reply_photo(
                    photo=photo,
                    caption=f"Вы находитесь в локации: {start_location[1]}\n\n{start_location[3]}",  # name и description
                    reply_markup=keyboard
                )
            else:
                await message.reply("Стартовая локация не найдена. Обратитесь к администратору.")
    except sqlite3.Error as e:
        await message.reply(f'Произошла ошибка при работе с базой данных: {e}')
    except FileNotFoundError:
        await message.reply("Изображение для локации не найдено.")


if __name__ == '__main__':
    # Запуск бота с помощью метода run_polling
    dp.run_polling(bot, skip_updates=True)