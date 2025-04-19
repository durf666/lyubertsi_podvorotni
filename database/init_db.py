# Перемещённый скрипт инициализации базы данных
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from models.base import Base
from models.character import Character
from models.location import Location, LocationConnection
from models.enemy import Enemy

load_dotenv()
DATABASE_URL = os.getenv('SQLALCHEMY_DATABASE_URL')
engine = create_engine(DATABASE_URL)

print("Создаём таблицы...")
Base.metadata.create_all(engine)
print("Готово!")
