# Перемещённый сид-скрипт для связей между локациями
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.location import Location, LocationConnection

load_dotenv()
DATABASE_URL = os.getenv('SQLALCHEMY_DATABASE_URL')
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

LOCATION_NAMES = [
    "Остановка маршрутки",
    "Подворотня",
    "Магазинчик 'У Гоги'",
    "Заброшенный завод"
]

def get_location_id_by_name(session, name):
    loc = session.query(Location).filter_by(name=name).first()
    if loc:
        return loc.id
    raise ValueError(f"Локация с именем {name} не найдена")

def seed_connections():
    session = Session()
    # Очищаем все старые связи
    session.query(LocationConnection).delete()
    session.commit()
    stop_id = get_location_id_by_name(session, "Остановка маршрутки")
    podvorotnya_id = get_location_id_by_name(session, "Подворотня")
    gogi_id = get_location_id_by_name(session, "Магазинчик 'У Гоги'")
    factory_id = get_location_id_by_name(session, "Заброшенный завод")

    # Только уникальные и не циклические связи
    connections = set()
    def add_conn(from_id, to_id):
        if from_id != to_id:
            connections.add((from_id, to_id))

    add_conn(stop_id, podvorotnya_id)
    add_conn(podvorotnya_id, factory_id)
    add_conn(podvorotnya_id, gogi_id)
    add_conn(gogi_id, podvorotnya_id)
    add_conn(factory_id, podvorotnya_id)

    for from_id, to_id in connections:
        c = LocationConnection(location_id=from_id, connected_location_id=to_id)
        session.add(c)
    session.commit()
    session.close()
    print("Связи между локациями успешно добавлены!")

if __name__ == '__main__':
    seed_connections()
