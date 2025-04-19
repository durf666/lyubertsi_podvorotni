from sqlalchemy import Column, Integer, String
from models.base import Base

class Enemy(Base):
    __tablename__ = 'enemies'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    strength = Column(Integer, nullable=False, default=10)
    agility = Column(Integer, nullable=False, default=10)
    endurance = Column(Integer, nullable=False, default=10)
    luck = Column(Integer, nullable=False, default=10)
    hp = Column(Integer, nullable=False, default=50)
    min_damage = Column(Integer, nullable=False, default=5)
    max_damage = Column(Integer, nullable=False, default=15)
    image = Column(String, nullable=True)
    description = Column(String, nullable=True)
    exp_reward = Column(Integer, nullable=False, default=5)

    def __repr__(self):
        return f"<Enemy(id={self.id}, name={self.name}, hp={self.hp}, exp_reward={self.exp_reward})>"
