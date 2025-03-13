class Character:
    def __init__(self, user_id, name):
        self.user_id = user_id
        self.name = name
        self.strength = 10
        self.agility = 10
        self.endurance = 10
        self.luck = 10
        self.hp = 100
        self.exp = 0
        self.exp_to_next_level = 100
        self.min_damage = 10
        self.max_damage = 20
        self.equipment = []
        self.skills = []

    def save_to_db(self, cursor):
        """Сохраняет данные персонажа в базу данных."""
        cursor.execute('''
            INSERT INTO characters (
                user_id, name, strength, agility, endurance, luck, hp, exp, exp_to_next_level, min_damage, max_damage
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            self.user_id,
            self.name,
            self.strength,
            self.agility,
            self.endurance,
            self.luck,
            self.hp,
            self.exp,
            self.exp_to_next_level,
            self.min_damage,
            self.max_damage
        ))