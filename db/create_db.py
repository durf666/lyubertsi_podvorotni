import sqlite3

def create_tables():
    # Подключаемся к базе данных (или создаем её, если она не существует)
    conn = sqlite3.connect('game.db')
    cursor = conn.cursor()

    try:
        # Создаем таблицу для персонажей
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS characters (
                id INTEGER PRIMARY KEY,
                user_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                strength INTEGER NOT NULL,
                agility INTEGER NOT NULL,
                endurance INTEGER NOT NULL,
                luck INTEGER NOT NULL,
                hp INTEGER NOT NULL,
                exp INTEGER NOT NULL,
                exp_to_next_level INTEGER NOT NULL,
                min_damage INTEGER NOT NULL,
                max_damage INTEGER NOT NULL
            );
        ''')

        # Создаем таблицу для снаряжения
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS equipment (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                type TEXT NOT NULL,
                strength INTEGER NOT NULL,
                agility INTEGER NOT NULL,
                endurance INTEGER NOT NULL,
                luck INTEGER NOT NULL
            );
        ''')

        # Создаем таблицу для навыков
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS skills (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                type TEXT NOT NULL,
                strength INTEGER NOT NULL,
                agility INTEGER NOT NULL,
                endurance INTEGER NOT NULL,
                luck INTEGER NOT NULL
            );
        ''')

        # Создаем таблицу для локаций
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS locations (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                number INTEGER NOT NULL,
                description TEXT NOT NULL,
                image TEXT NOT NULL,
                type TEXT NOT NULL DEFAULT 'neutral'
            );
        ''')

        # Сохраняем изменения
        conn.commit()
        print("Таблицы успешно созданы!")
    except sqlite3.Error as e:
        print(f"Ошибка при создании таблиц: {e}")
    finally:
        # Закрываем соединение с базой данных
        conn.close()

# Вызываем функцию для создания таблиц
create_tables()