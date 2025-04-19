from sqlalchemy import Column, Integer, String
from models.base import Base

class Character(Base):
    __tablename__ = 'characters'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, unique=True, nullable=False)
    name = Column(String, nullable=False)
    strength = Column(Integer, default=10)
    agility = Column(Integer, default=10)
    endurance = Column(Integer, default=10)
    luck = Column(Integer, default=10)
    hp = Column(Integer, default=100)
    exp = Column(Integer, default=0)
    exp_to_next_level = Column(Integer, default=100)
    level = Column(Integer, default=1)
    min_damage = Column(Integer, default=10)
    max_damage = Column(Integer, default=20)
    money = Column(Integer, default=100)
    current_location = Column(Integer, default=1)

    def __repr__(self):
        return f"<Character(id={self.id}, name={self.name}, level={self.level})>"