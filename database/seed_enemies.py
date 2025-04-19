# Перемещённый сид-скрипт для врагов
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.enemy import Enemy

load_dotenv()
DATABASE_URL = os.getenv('SQLALCHEMY_DATABASE_URL')
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

TEST_ENEMIES = [
    {
        "name": "Гопник",
        "strength": 8,
        "agility": 7,
        "endurance": 6,
        "luck": 3,
        "hp": 30,
        "min_damage": 3,
        "max_damage": 7,
        "image": "images/gopnik.jpg",
        "description": "Гопник в спортивках и с сигаретой за ухом. Пахнет перегаром, в руке — битая бутылка. Любит собирать дань с прохожих и устраивать разборки во дворе.",
        "exp_reward": 15
    },
    {
        "name": "Злая медсестра",
        "strength": 7,
        "agility": 8,
        "endurance": 6,
        "luck": 5,
        "hp": 28,
        "min_damage": 3,
        "max_damage": 7,
        "image": "images/nurse.jpg",
        "description": "Злая медсестра с растрёпанным халатом и огромным шприцом, наполненным мутной жидкостью. Лезет первой в драку, орёт на всех и угрожающе щёлкает пузырьком в шприце. Лучше не попадаться ей под руку во дворе!",
        "exp_reward": 18
    },
    {
        "name": "Панк с ирокезом",
        "strength": 7,
        "agility": 6,
        "endurance": 7,
        "luck": 2,
        "hp": 32,
        "min_damage": 4,
        "max_damage": 8,
        "image": "images/punk.jpg",
        "description": "Панк в кожанке, с рваными джинсами и ярким ирокезом. Вечно с магнитофоном и цепью, не прочь поспорить на кассету 'Сектор Газа'.",
        "exp_reward": 20
    }
]

def seed_enemies():
    session = Session()
    for enemy in TEST_ENEMIES:
        enemy_obj = Enemy(**enemy)
        session.add(enemy_obj)
    session.commit()
    session.close()
    print("Враги успешно добавлены!")

if __name__ == '__main__':
    seed_enemies()
