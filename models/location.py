class Location:
    def __init__(self, id, name, number, description, image, type='neutral'):
        self.id = id
        self.name = name
        self.number = number
        self.description = description
        self.image = image
        self.type = type  # Тип локации

    @classmethod
    def load_from_db(cls, cursor, location_id):
        """Загружает локацию из базы данных по её ID."""
        cursor.execute('SELECT * FROM locations WHERE id=?', (location_id,))
        data = cursor.fetchone()
        if data:
            return cls(data[0], data[1], data[2], data[3], data[4], data[5])
        return None

    @classmethod
    def load_by_number(cls, cursor, location_number):
        """Загружает локацию из базы данных по её номеру."""
        cursor.execute('SELECT * FROM locations WHERE number=?', (location_number,))
        data = cursor.fetchone()
        if data:
            return cls(data[0], data[1], data[2], data[3], data[4], data[5])
        return None