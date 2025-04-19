from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import FSInputFile  # Для загрузки изображений с диска
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from models.location import Location, LocationConnection
from keyboards.location_keyboard import get_location_keyboard


async def go_to_location(message: types.Message):
    """Обрабатывает команду /go <id локации>."""
    try:
        # Получаем id локации из сообщения
        location_id = int(message.text.split()[1])  # /go 1 → id
    except (IndexError, ValueError):
        await message.reply("Используйте команду так: /go <id локации>")
        return

    try:
        DATABASE_URL = os.getenv('SQLALCHEMY_DATABASE_URL')
        engine = create_engine(DATABASE_URL)
        Session = sessionmaker(bind=engine)
        session = Session()

        # Получаем локацию по номеру
        location = session.query(Location).filter_by(id=location_id).first()
        if location:
            keyboard = get_location_keyboard(location)
            photo = FSInputFile(location.image)
            await message.reply_photo(
                photo=photo,
                caption=f"Вы находитесь в локации: {location.name}\n\n{location.description}",
                reply_markup=keyboard
            )

            # Получаем связанные локации через ORM
            connections = session.query(LocationConnection).filter_by(location_id=location.id).all()
            if connections:
                connected_locations = [session.query(Location).filter_by(id=conn.connected_location_id).first() for conn in connections]
                move_keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
                    [types.InlineKeyboardButton(text=loc.name, callback_data=f"move_to_{loc.id}")]
                    for loc in connected_locations if loc is not None
                ])
                await message.answer("Выберите локацию для перехода:", reply_markup=move_keyboard)
            else:
                await message.answer("Нет доступных локаций для перехода.")
        else:
            await message.reply("Локация с таким id не найдена.")
        session.close()
    except FileNotFoundError:
        await message.reply("Изображение для локации не найдено.")
    except Exception as e:
        await message.reply(f'Произошла ошибка: {e}')


def register_handlers(dp: Dispatcher):
    dp.message(Command("go"))(go_to_location)