from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import FSInputFile  # Используем FSInputFile для загрузки файлов с диска
import os
from database.init_db import load_dotenv
from keyboards.location_keyboard import get_start_location_keyboard
from models.character import Character  # Импортируем класс Character
from handlers.callbacks import callback_router
from database.seed_locations import Location
from sqlalchemy.orm import sessionmaker
from database.seed_enemies import create_engine

load_dotenv()
API_TOKEN = os.getenv('BOT_TOKEN')

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
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        DATABASE_URL = os.getenv('SQLALCHEMY_DATABASE_URL')
        engine = create_engine(DATABASE_URL)
        Session = sessionmaker(bind=engine)
        session = Session()

        # Проверяем, есть ли персонаж у игрока
        existing_character = session.query(Character).filter_by(user_id=user_id).first()
        # Получаем id локации "Остановка маршрутки"
        stop_location = session.query(Location).filter_by(name="Остановка маршрутки").first()
        stop_location_id = stop_location.id if stop_location else 1
        if existing_character is None:
            new_character = Character(user_id=user_id, name=user_name, current_location=stop_location_id)
            session.add(new_character)
            session.commit()
            await message.reply('Привет, новый игрок! Ты создал нового персонажа.')
        else:
            existing_character.current_location = stop_location_id
            session.commit()
            await message.reply(f'Привет, {user_name}! Ты вернулся в игру.')

        # Отправляем стартовую локацию
        start_location = session.query(Location).filter_by(id=stop_location_id).first()
        if start_location:
            keyboard = get_start_location_keyboard()
            # Загружаем изображение с диска
            image_path = start_location.image  # Путь к изображению
            photo = FSInputFile(image_path)  # Используем FSInputFile
            await message.reply_photo(
                photo=photo,
                caption=f"Вы находитесь в локации: {start_location.name}\n\n{start_location.description}",  # name и description
                reply_markup=keyboard
            )
        else:
            await message.reply("Стартовая локация не найдена. Обратитесь к администратору.")
    except Exception as e:
        await message.reply(f'Произошла ошибка: {e}')


if __name__ == '__main__':
    # Запуск бота с помощью метода run_polling
    dp.run_polling(bot, skip_updates=True)