import logging
import random

from aiogram import Router
from aiogram import types
from aiogram.types import CallbackQuery
from aiogram.types import FSInputFile
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from database.crud import get_connected_locations, get_random_enemy
from handlers.location import go_to_location
from keyboards.location_keyboard import get_location_keyboard, get_shop_buy_keyboard

callback_router = Router()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def return_to_location(message: types.Message, location_id):
    """Возвращает игрока в текущую локацию."""
    from sqlalchemy.orm import sessionmaker
    from sqlalchemy import create_engine
    from models.location import Location
    import os
    DATABASE_URL = os.getenv('SQLALCHEMY_DATABASE_URL')
    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        location = session.query(Location).filter_by(id=location_id).first()
        if location:
            photo = FSInputFile(location.image)
            keyboard = get_location_keyboard(location)
            await message.answer_photo(
                photo=photo,
                caption=f"Вы находитесь в локации: {location.name}\n\n{location.description}",
                reply_markup=keyboard
            )
        else:
            await message.answer("Локация не найдена.")
    except FileNotFoundError:
        await message.answer("Изображение для локации не найдено.")
    except Exception as e:
        await message.answer(f'Произошла ошибка: {e}')
    finally:
        session.close()

def calculate_damage(attacker, defender, is_defending=False):
    """Рассчитывает урон, нанесённый атакующим."""
    damage = random.randint(attacker['min_damage'], attacker['max_damage'])
    if is_defending:
        damage = max(1, damage // 2)  # Уменьшаем урон, если защищаемся
    defender['hp'] -= damage
    return damage


@callback_router.callback_query(lambda c: c.data == 'action_shop_buy')
async def handle_action_shop_buy(callback_query: CallbackQuery):
    """Открывает подменю покупки в магазине (шаурма)."""
    await callback_query.message.edit_reply_markup(reply_markup=get_shop_buy_keyboard())
    await callback_query.answer()

@callback_router.callback_query(lambda c: c.data == 'action_character_info')
async def handle_action_character_info(callback_query: CallbackQuery):
    """Показывает информацию о персонаже: здоровье, уровень, опыт и опыт до следующего уровня."""
    from sqlalchemy.orm import sessionmaker
    from sqlalchemy import create_engine
    from models.character import Character
    import os
    DATABASE_URL = os.getenv('SQLALCHEMY_DATABASE_URL')
    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        user_id = callback_query.from_user.id
        character = session.query(Character).filter_by(user_id=user_id).first()
        if character:
            max_hp = 100 + (character.endurance - 10) * 10
            text = (
                f"<b>{character.name}</b>\n"
                f"❤️ Здоровье: {character.hp}/{max_hp}\n"
                f"⭐️ Уровень: {character.level}\n"
                f"🔸 Опыт: {character.exp}\n"
                f"🔜 До след. уровня: {character.exp_to_next_level - character.exp}"
            )
            await callback_query.message.answer(text, parse_mode="HTML")
        else:
            await callback_query.message.answer("Персонаж не найден.")
    finally:
        session.close()
    await callback_query.answer()

@callback_router.callback_query(lambda c: c.data == 'action_shop_back')
async def handle_action_shop_back(callback_query: CallbackQuery):
    """Возврат к главному магазину."""
    from sqlalchemy.orm import sessionmaker
    from sqlalchemy import create_engine
    from models.character import Character
    from models.location import Location
    import os
    DATABASE_URL = os.getenv('SQLALCHEMY_DATABASE_URL')
    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        user_id = callback_query.from_user.id
        character = session.query(Character).filter_by(user_id=user_id).first()
        if character:
            location = session.query(Location).filter_by(id=character.current_location).first()
            if location:
                await callback_query.message.edit_reply_markup(reply_markup=get_location_keyboard(location))
    finally:
        session.close()
    await callback_query.answer()

@callback_router.callback_query(lambda c: c.data == 'action_buy_shawarma')
async def handle_action_buy_shawarma(callback_query: CallbackQuery):
    """Покупка шаурмы: восстановить HP до максимума и показать подменю покупки."""
    from sqlalchemy.orm import sessionmaker
    from sqlalchemy import create_engine
    from models.character import Character
    import os
    DATABASE_URL = os.getenv('SQLALCHEMY_DATABASE_URL')
    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        user_id = callback_query.from_user.id
        character = session.query(Character).filter_by(user_id=user_id).first()
        if character:
            # Вычисляем максимальное HP по формуле: 100 + (endurance - 10) * 10
            max_hp = 100 + (character.endurance - 10) * 10
            character.hp = max_hp
            session.commit()
            from aiogram.types import FSInputFile
            shawarma_img = FSInputFile("images/shawa.jpg")
            await callback_query.message.answer_photo(
                photo=shawarma_img,
                caption="Вы купили шаурму 🌯 и полностью восстановили здоровье!"
            )
            # Сразу после фото отправляем сообщение с клавиатурой покупок
            from aiogram.types import FSInputFile
            shop_img = FSInputFile("images/shop.jpg")
            await callback_query.message.answer_photo(
                photo=shop_img,
                caption="Что хотите сделать дальше?",
                reply_markup=get_shop_buy_keyboard()
            )
        else:
            await callback_query.message.answer("Персонаж не найден.")
    finally:
        session.close()
    # Безопасно обновляем клавиатуру, игнорируя ошибку 'message is not modified'
    try:
        await callback_query.message.edit_reply_markup(reply_markup=get_shop_buy_keyboard())
    except Exception as e:
        try:
            from aiogram.exceptions import TelegramBadRequest
        except ImportError:
            TelegramBadRequest = None
        if not (TelegramBadRequest and isinstance(e, TelegramBadRequest) and 'message is not modified' in str(e)):
            raise
    await callback_query.answer()

@callback_router.callback_query(lambda c: c.data == 'action_move')
async def handle_action_move(callback_query: CallbackQuery):
    """Обрабатывает действие 'Перейти в другую локацию'."""
    user_id = callback_query.from_user.id

    from sqlalchemy.orm import sessionmaker
    from sqlalchemy import create_engine
    from models.character import Character
    from models.location import Location, LocationConnection
    import os
    DATABASE_URL = os.getenv('SQLALCHEMY_DATABASE_URL')
    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        # Получаем текущую локацию игрока
        character = session.query(Character).filter_by(user_id=user_id).first()
        if character and character.current_location is not None:
            current_location_id = character.current_location
            # Получаем связанные локации через ORM
            connections = session.query(LocationConnection).filter_by(location_id=current_location_id).all()
            connected_locations = [session.query(Location).filter_by(id=conn.connected_location_id).first() for conn in connections]
            if connected_locations:
                keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
                    [types.InlineKeyboardButton(text=loc.name, callback_data=f"move_to_{loc.id}")]
                    for loc in connected_locations if loc is not None
                ])
                await callback_query.message.answer("Выберите локацию для перехода:", reply_markup=keyboard)
            else:
                await callback_query.message.answer("Нет доступных локаций для перехода.")
        else:
            await callback_query.message.answer("Текущая локация не найдена.")
    except Exception as e:
        await callback_query.message.answer(f'Произошла ошибка: {e}')
    finally:
        session.close()

# Обрабатывает действие 'Уйти' из магазинчика (делает то же, что и action_move)
@callback_router.callback_query(lambda c: c.data == 'action_leave')
async def handle_action_leave(callback_query: CallbackQuery):
    await handle_action_move(callback_query)

@callback_router.callback_query(lambda c: c.data.startswith('move_to_'))
async def handle_move_to_location(callback_query: CallbackQuery):
    """Обрабатывает выбор локации для перехода."""
    from sqlalchemy.orm import sessionmaker
    from sqlalchemy import create_engine
    from models.character import Character
    from models.location import Location
    import os
    user_id = callback_query.from_user.id
    location_id = int(callback_query.data.split('_')[2])  # move_to_1 → id
    DATABASE_URL = os.getenv('SQLALCHEMY_DATABASE_URL')
    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        # Загружаем выбранную локацию
        location = session.query(Location).filter_by(id=location_id).first()
        if location:
            # Обновляем текущую локацию игрока
            character = session.query(Character).filter_by(user_id=user_id).first()
            if character:
                character.current_location = location.id
                session.commit()
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
    except FileNotFoundError:
        await callback_query.message.answer("Изображение для локации не найдено.")
    except Exception as e:
        await callback_query.message.answer(f'Произошла ошибка: {e}')
    finally:
        session.close()


@callback_router.callback_query(lambda c: c.data == 'action_deeper')
async def handle_action_deeper(callback_query: CallbackQuery):
    """Обрабатывает действие 'Идти глубже'."""
    user_id = callback_query.from_user.id

    from sqlalchemy.orm import sessionmaker
    from sqlalchemy import create_engine
    from models.enemy import Enemy
    import os
    DATABASE_URL = os.getenv('SQLALCHEMY_DATABASE_URL')
    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
    session = Session()
    import random
    try:
        # Выбираем случайного противника
        enemies = session.query(Enemy).all()
        if enemies:
            enemy = random.choice(enemies)
            photo = FSInputFile(enemy.image)
            await callback_query.message.answer_photo(
                photo=photo,
                caption=f"{enemy.name}\n\n{enemy.description}"
            )
            await callback_query.message.answer(
                f"У противника {enemy.hp} HP.\nЧто будете делать?",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="⚔️ В бой", callback_data=f"action_attack_{enemy.id}")],
                    [InlineKeyboardButton(text="🏃‍♂️ Сбежать", callback_data=f"action_flee_{enemy.id}")]
                ])
            )
        else:
            await callback_query.message.answer("Противники не найдены.")
    except FileNotFoundError:
        await callback_query.message.answer("Изображение для противника не найдено.")
    except Exception as e:
        await callback_query.message.answer(f'Произошла ошибка: {e}')
    finally:
        session.close()


@callback_router.callback_query(lambda c: c.data.startswith('action_flee_'))
async def handle_action_flee(callback_query: CallbackQuery):
    """Обрабатывает действие 'Сбежать'."""
    user_id = callback_query.from_user.id
    enemy_id = int(callback_query.data.split('_')[2])  # action_flee_1 → 1

    # Шанс побега 50/50
    if random.random() < 0.5:
        await callback_query.message.answer("Вам удалось сбежать!")
        # Возвращаем игрока в текущую локацию
        await go_to_location(callback_query.message)  # Вызываем функцию для возврата в локацию
    else:
        await callback_query.message.answer("Вам не удалось сбежать! Приготовьтесь к бою.")
        # Продолжаем бой
        await handle_action_attack(callback_query)


# @callback_router.callback_query(lambda c: c.data.startswith('action_attack_'))
# async def handle_action_attack(callback_query: CallbackQuery):
#     """Обрабатывает действие 'В бой'."""
#     user_id = callback_query.from_user.id
#     enemy_id = int(callback_query.data.split('_')[2])  # action_attack_1 → 1
#
#     try:
#         with sqlite3.connect('db/game.db') as conn:
#             cursor = conn.cursor()
#
#             # Получаем данные игрока и противника
#             cursor.execute('SELECT * FROM characters WHERE user_id=?', (user_id,))
#             player = cursor.fetchone()
#
#             cursor.execute('SELECT * FROM enemies WHERE id=?', (enemy_id,))
#             enemy = cursor.fetchone()
#
#             if player and enemy:
#                 player_damage = random.randint(player[10], player[11])  # min_damage и max_damage игрока
#                 enemy_hp = enemy[6] - player_damage
#
#                 if enemy_hp <= 0:
#                     await callback_query.message.answer(
#                         f"Вы нанесли {player_damage} урона и победили {enemy[1]}!"
#                     )
#                 else:
#                     cursor.execute('UPDATE enemies SET hp=? WHERE id=?', (enemy_hp, enemy_id))
#                     conn.commit()
#                     await callback_query.message.answer(
#                         f"Вы нанесли {player_damage} урона. У {enemy[1]} осталось {enemy_hp} HP."
#                     )
#             else:
#                 await callback_query.message.answer("Игрок или противник не найдены.")
#     except sqlite3.Error as e:
#         await callback_query.message.answer(f'Произошла ошибка при работе с базой данных: {e}')


@callback_router.callback_query(lambda c: c.data.startswith('action_attack_'))
async def handle_action_attack(callback_query: CallbackQuery):
    """Обрабатывает действие 'Атаковать'."""
    user_id = callback_query.from_user.id
    enemy_id = int(callback_query.data.split('_')[2])  # action_attack_1 → 1

    from sqlalchemy.orm import sessionmaker
    from sqlalchemy import create_engine
    from models.character import Character
    from models.enemy import Enemy
    import os
    DATABASE_URL = os.getenv('SQLALCHEMY_DATABASE_URL')
    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        player = session.query(Character).filter_by(user_id=user_id).first()
        enemy = session.query(Enemy).filter_by(id=enemy_id).first()
        if player and enemy:
            player_data = {
                'id': player.id,
                'hp': player.hp,
                'min_damage': player.min_damage,
                'max_damage': player.max_damage
            }
            enemy_data = {
                'id': enemy.id,
                'hp': enemy.hp,
                'min_damage': enemy.min_damage,
                'max_damage': enemy.max_damage
            }
            # Игрок атакует
            player_damage = calculate_damage(player_data, enemy_data)
            await callback_query.message.answer(
                f"Вы нанесли {player_damage} урона. У {enemy.name} осталось {enemy_data['hp']} HP."
            )
            if enemy_data['hp'] <= 0:
                gold_reward = getattr(enemy, 'gold', 0)
                exp_reward = getattr(enemy, 'exp_reward', 0)
                player.gold = getattr(player, 'gold', 0) + gold_reward
                player.exp = getattr(player, 'exp', 0) + exp_reward
                level_up_messages = []
                # Level up logic
                while player.exp >= player.exp_to_next_level:
                    player.exp -= player.exp_to_next_level
                    player.level += 1
                    # Increase exp required for next level (e.g., +50%)
                    player.exp_to_next_level = int(player.exp_to_next_level * 1.5)
                    # Restore HP to max (optional)
                    player.hp = 100 + (player.endurance - 10) * 10
                    level_up_messages.append(f"\n🎉 Поздравляем! Ваш уровень повышен до {player.level}! HP восстановлено.")
                session.delete(enemy)
                session.commit()
                await callback_query.message.answer(
                    f"Вы победили {enemy.name}!\n\n🏅 Награда: +{gold_reward} gold, +{exp_reward} XP." + ''.join(level_up_messages)
                )
                await return_to_location(callback_query.message, player.current_location)
                return
            # Противник атакует
            enemy_damage = calculate_damage(enemy_data, player_data)
            await callback_query.message.answer(
                f"{enemy.name} нанёс вам {enemy_damage} урона. У вас осталось {player_data['hp']} HP."
            )
            if player_data['hp'] <= 0:
                await callback_query.message.answer("Вы проиграли!")
                await return_to_location(callback_query.message, player.current_location)
                return
            # Обновляем HP в базе
            player.hp = player_data['hp']
            enemy.hp = enemy_data['hp']
            session.commit()
            await callback_query.message.answer(
                "Бой продолжается! Что будете делать?",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="⚔️ Атаковать", callback_data=f"action_attack_{enemy_id}")],
                    [InlineKeyboardButton(text="🛡️ Защищаться", callback_data=f"action_defend_{enemy_id}")],
                    [InlineKeyboardButton(text="🏃‍♂️ Сбежать", callback_data=f"action_flee_{enemy_id}")]
                ])
            )
        else:
            await callback_query.message.answer("Игрок или противник не найдены.")
    except Exception as e:
        await callback_query.message.answer(f'Произошла ошибка: {e}')
    finally:
        session.close()

@callback_router.callback_query(lambda c: c.data.startswith('action_defend_'))
async def handle_action_defend(callback_query: CallbackQuery):
    """Обрабатывает действие 'Защищаться'."""
    user_id = callback_query.from_user.id
    enemy_id = int(callback_query.data.split('_')[2])  # action_defend_1 → 1

    from sqlalchemy.orm import sessionmaker
    from sqlalchemy import create_engine
    from models.character import Character
    from models.enemy import Enemy
    import os
    DATABASE_URL = os.getenv('SQLALCHEMY_DATABASE_URL')
    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        player = session.query(Character).filter_by(user_id=user_id).first()
        enemy = session.query(Enemy).filter_by(id=enemy_id).first()
        if player and enemy:
            player_data = {
                'id': player.id,
                'hp': player.hp,
                'min_damage': player.min_damage,
                'max_damage': player.max_damage
            }
            enemy_data = {
                'id': enemy.id,
                'hp': enemy.hp,
                'min_damage': enemy.min_damage,
                'max_damage': enemy.max_damage
            }
            await callback_query.message.answer("Вы решили защищаться.")
            enemy_damage = calculate_damage(enemy_data, player_data, is_defending=True)
            await callback_query.message.answer(
                f"{enemy.name} нанёс вам {enemy_damage} урона. У вас осталось {player_data['hp']} HP."
            )
            if player_data['hp'] <= 0:
                await callback_query.message.answer("Вы проиграли!")
                return
            player.hp = player_data['hp']
            enemy.hp = enemy_data['hp']
            session.commit()
            await callback_query.message.answer(
                "Бой продолжается! Что будете делать?",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="⚔️ Атаковать", callback_data=f"action_attack_{enemy_id}")],
                    [InlineKeyboardButton(text="🛡️ Защищаться", callback_data=f"action_defend_{enemy_id}")],
                    [InlineKeyboardButton(text="🏃‍♂️ Сбежать", callback_data=f"action_flee_{enemy_id}")]
                ])
            )
        else:
            await callback_query.message.answer("Игрок или противник не найдены.")
    except Exception as e:
        await callback_query.message.answer(f'Произошла ошибка: {e}')
    finally:
        session.close()