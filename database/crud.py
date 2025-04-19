import psycopg2
import random
import os
from dotenv import load_dotenv
from models.location import Location

load_dotenv()

def get_pg_connection():
    return psycopg2.connect(
        host=os.getenv('PG_HOST'),
        port=os.getenv('PG_PORT'),
        user=os.getenv('PG_USER'),
        password=os.getenv('PG_PASSWORD'),
        dbname=os.getenv('PG_DB')
    )

# Удалена функция get_location_by_number, так как поле number больше не используется и поиск локаций теперь делается через SQLAlchemy ORM напрямую.
# Если весь crud.py больше не используется в проекте, рекомендуется удалить этот файл полностью для чистоты кода.

def get_connected_locations(current_location_id):
    """Возвращает список локаций, связанных с текущей."""
    with get_pg_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute('''
                SELECT l.* FROM locations l
                JOIN location_connections lc ON l.id = lc.connected_location_id
                WHERE lc.location_id = %s
            ''', (current_location_id,))
            return cursor.fetchall()

def get_random_enemy():
    """Возвращает случайного противника из базы данных."""
    with get_pg_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute('SELECT * FROM enemies')
            enemies = cursor.fetchall()
            return random.choice(enemies) if enemies else None