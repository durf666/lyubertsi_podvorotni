import sqlite3

# Данные для тестовых локаций
TEST_LOCATIONS = [
    {
        "name": "Остановка маршрутки",
        "number": 0,  # Номер 0 для стартовой локации
        "description": (
            "Вы выходите из маршрутки на заброшенной остановке. Вокруг ни души, только ветер гоняет по асфальту "
            "пустые пачки сигарет и обрывки газет. Вдалеке виднеются мрачные многоэтажки, а на остановке висит "
            "разбитое расписание. Куда вы отправитесь?"
        ),
        "image": "https://example.com/bus_stop.jpg",
        "type": "neutral"
    },
    {
        "name": "Подворотня",
        "number": 1,
        "description": "Темная и мрачная подворотня. На стенах граффити, а в углу валяется пустая бутылка.",
        "image": "https://example.com/image1.jpg",
        "type": "combat"
    },
    {
        "name": "Парк",
        "number": 2,
        "description": "Тихий парк с полуразрушенными скамейками. Вдалеке слышен лай собак.",
        "image": "https://example.com/image2.jpg",
        "type": "neutral"
    },
    {
        "name": "Торговый центр",
        "number": 3,
        "description": "Заброшенный торговый центр. Внутри темно, только мигает неоновая вывеска.",
        "image": "https://example.com/image3.jpg",
        "type": "shop"
    },
    {
        "name": "Заброшенный завод",
        "number": 4,
        "description": "Огромный заброшенный завод. Внутри слышны странные звуки.",
        "image": "https://example.com/image4.jpg",
        "type": "event"
    }
]

def seed_locations():
    """Добавляет тестовые локации в базу данных."""
    try:
        # Подключаемся к базе данных
        with sqlite3.connect('game.db') as conn:
            cursor = conn.cursor()

            # Добавляем каждую локацию в таблицу
            for location in TEST_LOCATIONS:
                cursor.execute('''
                    INSERT INTO locations (name, number, description, image, type)
                    VALUES (?, ?, ?, ?, ?)
                ''', (
                    location['name'],
                    location['number'],
                    location['description'],
                    location['image'],
                    location['type']
                ))

            # Сохраняем изменения
            conn.commit()
            print("Тестовые локации успешно добавлены в базу данных!")
    except sqlite3.Error as e:
        print(f"Ошибка при добавлении локаций: {e}")

if __name__ == '__main__':
    seed_locations()