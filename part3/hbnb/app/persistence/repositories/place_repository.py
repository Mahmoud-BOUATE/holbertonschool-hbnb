"""User repository implementation"""
from app.models.place import Place
from app.persistence.repository import SQLAlchemyRepository


class PlaceRepository(SQLAlchemyRepository):
    """Repository for Place entity with specific methods"""

    def __init__(self):
        super().__init__(Place)