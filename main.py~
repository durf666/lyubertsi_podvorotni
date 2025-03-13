import sqlite3

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage

from models.character import Character

API_TOKEN = '7428809191:AAFL-3P-osdw67R8Y6njmSyJYi1Jbyjy6I8'

# Инициализация хранилища и бота
storage = MemoryStorage()  # Используем встроенное хранилище для FSM
bot = Bot(token=API_TOKEN)
dp = Dispatcher(storage=storage)  # Передаем хранилище в Dispatcher


@dp.message(Command("start"))
async def send_welcome(message: types.Message):
    user_id = message.from_user.id
    user_name = message.from_user.first_name or message.from_user.username

    try:
        # Используем контекстный менеджер для работы с базой данных
        with sqlite3.connect('game.db') as conn:
            cursor = conn.cursor()
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
                # Если пользователь уже есть в базе данных, приветствуем его
                await message.reply(f'Привет, {user_name}! Ты вернулся в игру.')
    except sqlite3.Error as e:
        await message.reply(f'Произошла ошибка при работе с базой данных: {e}')


if __name__ == '__main__':
    # Запуск бота с помощью метода run_polling
    dp.run_polling(bot, skip_updates=True)
