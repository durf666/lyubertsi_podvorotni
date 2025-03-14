from sqlite3 import Connection
from models.location import Location

def get_location_by_number(cursor, location_number):
    cursor.execute('SELECT * FROM locations WHERE number=?', (location_number,))
    data = cursor.fetchone()
    if data:
        return Location(data[0], data[1], data[2], data[3], data[4], data[5])
    return None

def get_connected_locations(cursor, current_location_id):
    """Возвращает список локаций, связанных с текущей."""
    cursor.execute('''
        SELECT l.* FROM locations l
        JOIN location_connections lc ON l.id = lc.connected_location_id
        WHERE lc.location_id = ?
    ''', (current_location_id,))
    return cursor.fetchall()