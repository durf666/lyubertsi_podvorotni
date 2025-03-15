import logging
import random
import sqlite3

from aiogram import Router
from aiogram import types
from aiogram.types import CallbackQuery
from aiogram.types import FSInputFile
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from database.crud import get_location_by_number, get_connected_locations, get_random_enemy
from handlers.location import go_to_location
from keyboards.location_keyboard import get_location_keyboard

callback_router = Router()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def return_to_location(message: types.Message, location_id):
    """Возвращает игрока в текущую локацию."""
    try:
        with sqlite3.connect('db/game.db') as conn:
            cursor = conn.cursor()

            # Получаем данные локации
            cursor.execute('SELECT * FROM locations WHERE id=?', (location_id,))
            location = get_location_by_number(cursor, location_id)
            print(location)
            if location:
                # Отправляем описание и изображение локации с клавиатурой
                photo = FSInputFile(location.image)  # image
                keyboard = get_location_keyboard(location)  # Получаем клавиатуру
                await message.answer_photo(
                    photo=photo,
                    caption=f"Вы находитесь в локации: {location.name}\n\n{location.description}",
                    reply_markup=keyboard  # Прикрепляем клавиатуру
                )
            else:
                await message.answer("Локация не найдена.")
    except sqlite3.Error as e:
        await message.answer(f'Произошла ошибка при работе с базой данных: {e}')

def calculate_damage(attacker, defender, is_defending=False):
    """Рассчитывает урон, нанесённый атакующим."""
    damage = random.randint(attacker['min_damage'], attacker['max_damage'])
    if is_defending:
        damage = max(1, damage // 2)  # Уменьшаем урон, если защищаемся
    defender['hp'] -= damage
    return damage


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
                        [types.InlineKeyboardButton(text=loc[1], callback_data=f"move_to_{loc[2]}")]
                        # loc[1] — имя локации, loc[2] — номер
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


@callback_router.callback_query(lambda c: c.data == 'action_deeper')
async def handle_action_deeper(callback_query: CallbackQuery):
    """Обрабатывает действие 'Идти глубже'."""
    user_id = callback_query.from_user.id

    try:
        with sqlite3.connect('db/game.db') as conn:
            cursor = conn.cursor()

            # Выбираем случайного противника
            enemy = get_random_enemy(cursor)
            if enemy:
                enemy_id, enemy_name, _, _, _, _, enemy_hp, _, _, enemy_image, enemy_description = enemy

                # Отправляем изображение и описание противника
                photo = FSInputFile(enemy_image)
                await callback_query.message.answer_photo(
                    photo=photo,
                    caption=f"{enemy_name}\n\n{enemy_description}"
                )

                # Предлагаем кнопки для боя или побега
                await callback_query.message.answer(
                    f"У противника {enemy_hp} HP.\nЧто будете делать?",
                    reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                        [InlineKeyboardButton(text="⚔️ В бой", callback_data=f"action_attack_{enemy_id}")],
                        [InlineKeyboardButton(text="🏃‍♂️ Сбежать", callback_data=f"action_flee_{enemy_id}")]
                    ])
                )
            else:
                await callback_query.message.answer("Противники не найдены.")
    except sqlite3.Error as e:
        await callback_query.message.answer(f'Произошла ошибка при работе с базой данных: {e}')


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

    try:
        with sqlite3.connect('db/game.db') as conn:
            cursor = conn.cursor()

            # Получаем данные игрока и противника
            cursor.execute('SELECT * FROM characters WHERE user_id=?', (user_id,))
            player = cursor.fetchone()

            cursor.execute('SELECT * FROM enemies WHERE id=?', (enemy_id,))
            enemy = cursor.fetchone()

            if player and enemy:
                # Преобразуем данные в словари для удобства
                player_data = {
                    'id': player[0],
                    'hp': player[7],
                    'min_damage': player[10],
                    'max_damage': player[11]
                }
                enemy_data = {
                    'id': enemy[0],
                    'hp': enemy[6],
                    'min_damage': enemy[7],
                    'max_damage': enemy[8]
                }

                # Игрок атакует
                player_damage = calculate_damage(player_data, enemy_data)
                await callback_query.message.answer(
                    f"Вы нанесли {player_damage} урона. У {enemy[1]} осталось {enemy_data['hp']} HP."
                )

                if enemy_data['hp'] <= 0:
                    await callback_query.message.answer(f"Вы победили {enemy[1]}!")
                    # Возвращаем игрока в локацию
                    await return_to_location(callback_query.message, player[12])  # player[8] — current_location
                    return

                # Противник атакует
                enemy_damage = calculate_damage(enemy_data, player_data)
                await callback_query.message.answer(
                    f"{enemy[1]} нанёс вам {enemy_damage} урона. У вас осталось {player_data['hp']} HP."
                )

                if player_data['hp'] <= 0:
                    await callback_query.message.answer("Вы проиграли!")
                    # Возвращаем игрока в локацию
                    await return_to_location(callback_query.message, player[12])  # player[8] — current_location
                    return

                # Обновляем HP в базе данных
                cursor.execute('UPDATE characters SET hp=? WHERE id=?', (player_data['hp'], player_data['id']))
                cursor.execute('UPDATE enemies SET hp=? WHERE id=?', (enemy_data['hp'], enemy_data['id']))
                conn.commit()

                # Продолжаем бой
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
    except sqlite3.Error as e:
        await callback_query.message.answer(f'Произошла ошибка при работе с базой данных: {e}')

@callback_router.callback_query(lambda c: c.data.startswith('action_defend_'))
async def handle_action_defend(callback_query: CallbackQuery):
    """Обрабатывает действие 'Защищаться'."""
    user_id = callback_query.from_user.id
    enemy_id = int(callback_query.data.split('_')[2])  # action_defend_1 → 1

    try:
        with sqlite3.connect('db/game.db') as conn:
            cursor = conn.cursor()

            # Получаем данные игрока и противника
            cursor.execute('SELECT * FROM characters WHERE user_id=?', (user_id,))
            player = cursor.fetchone()

            cursor.execute('SELECT * FROM enemies WHERE id=?', (enemy_id,))
            enemy = cursor.fetchone()

            if player and enemy:
                # Преобразуем данные в словари для удобства
                player_data = {
                    'id': player[0],
                    'hp': player[7],
                    'min_damage': player[10],
                    'max_damage': player[11]
                }
                enemy_data = {
                    'id': enemy[0],
                    'hp': enemy[6],
                    'min_damage': enemy[7],
                    'max_damage': enemy[8]
                }

                # Игрок защищается
                await callback_query.message.answer("Вы решили защищаться.")

                # Противник атакует
                enemy_damage = calculate_damage(enemy_data, player_data, is_defending=True)
                await callback_query.message.answer(
                    f"{enemy[1]} нанёс вам {enemy_damage} урона. У вас осталось {player_data['hp']} HP."
                )

                if player_data['hp'] <= 0:
                    await callback_query.message.answer("Вы проиграли!")
                    return

                # Обновляем HP в базе данных
                cursor.execute('UPDATE characters SET hp=? WHERE id=?', (player_data['hp'], player_data['id']))
                cursor.execute('UPDATE enemies SET hp=? WHERE id=?', (enemy_data['hp'], enemy_data['id']))
                conn.commit()

                # Продолжаем бой
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
    except sqlite3.Error as e:
        await callback_query.message.answer(f'Произошла ошибка при работе с базой данных: {e}')