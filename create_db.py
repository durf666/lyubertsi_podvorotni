import sqlite3

# Создаем соединение с базой данных
conn = sqlite3.connect('game.db')

# Создаем курсор
cursor = conn.cursor()

# Создаем таблицу для хранения персонажей
cursor.execute('''
CREATE TABLE characters (
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

# Создаем таблицу для хранения снаряжения
cursor.execute('''
    CREATE TABLE equipment (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        type TEXT NOT NULL,
        strength INTEGER NOT NULL,
        agility INTEGER NOT NULL,
        endurance INTEGER NOT NULL,
        luck INTEGER NOT NULL
    );
''')

# Создаем таблицу для хранения навыков
cursor.execute('''
    CREATE TABLE skills (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        type TEXT NOT NULL,
        strength INTEGER NOT NULL,
        agility INTEGER NOT NULL,
        endurance INTEGER NOT NULL,
        luck INTEGER NOT NULL
    );
''')



# Закрываем соединение с базой данных
conn.close()