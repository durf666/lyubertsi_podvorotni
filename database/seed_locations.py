# Перемещённый сид-скрипт для локаций
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.location import Location

load_dotenv()
DATABASE_URL = os.getenv('SQLALCHEMY_DATABASE_URL')
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

TEST_LOCATIONS = [
    {
        "name": "Остановка маршрутки",

        "description": (
            "Маршрутка с визгом тормозит у облезлого павильона. Вокруг — ни души, только ржавый ларёк, битое стекло под ногами и запах дешёвого пива, доносящийся из-под лавки. "
            "Пару раз мелькает подозрительная фигура в спортивках, но быстро исчезает в тени. Добро пожаловать в 90-е — здесь каждый сам за себя."
        ),
        "image": "images/bus_stop.jpg",
        "type": "neutral"
    },
    {
        "name": "Подворотня",

        "description": (
            "Узкая подворотня между домами, где даже днём темно как ночью. На стенах — свежие теги местной шпаны, под ногами — битые бутылки и окурки. "
            "Где-то в глубине слышен смех и звон монет — возможно, там играют в карты или делят добычу. Здесь лучше держать ухо востро: за каждым углом может ждать сюрприз."
        ),
        "image": "images/backstreet.jpg",
        "type": "combat"
    },
    {
        "name": "Магазинчик 'У Гоги'",

        "description": (
            "Уютный, но подозрительный магазинчик с решётками на окнах. За прилавком — сам Гога: вечно в трениках, с золотым зубом и сигаретой в уголке рта. "
            "Здесь можно купить всё — от жвачки Turbo до палёного коньяка. Гога знает все сплетни района и всегда готов поделиться "
            "информацией... за небольшую плату."
        ),
        "image": "images/gogi_shop.jpg",
        "type": "shop"
    },
    {
        "name": "Заброшенный завод",

        "description": (
            "Гигантские корпуса, проржавевшие ворота, разбитые окна. Внутри — лабиринт цехов, эхо шагов и странные тени, которые будто следят за тобой. "
            "Говорят, по ночам здесь собираются странные личности, а иногда — слышны крики. Место для настоящих искателей приключений и неприятностей."
        ),
        "image": "images/factory.jpg",
        "type": "event"
    }
]

def seed_locations():
    session = Session()
    for loc in TEST_LOCATIONS:
        location = Location(**loc)
        session.add(location)
    session.commit()
    session.close()
    print("Локации успешно добавлены!")

if __name__ == '__main__':
    seed_locations()
