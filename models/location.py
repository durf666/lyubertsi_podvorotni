from sqlalchemy import Column, Integer, String, ForeignKey
from models.base import Base

class Location(Base):
    __tablename__ = 'locations'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=False)
    image = Column(String, nullable=False)
    type = Column(String, nullable=False, default='neutral')

    def __repr__(self):
        return f"<Location(id={self.id}, name={self.name}, type={self.type})>"

class LocationConnection(Base):
    __tablename__ = 'location_connections'

    id = Column(Integer, primary_key=True)
    location_id = Column(Integer, ForeignKey('locations.id'), nullable=False)
    connected_location_id = Column(Integer, ForeignKey('locations.id'), nullable=False)

    def __repr__(self):
        return f"<LocationConnection(id={self.id}, location_id={self.location_id}, connected_location_id={self.connected_location_id})>"
