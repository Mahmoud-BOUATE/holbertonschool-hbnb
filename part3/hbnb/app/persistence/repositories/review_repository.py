"""User repository implementation"""
from app.models.review import Review
from app.persistence.repository import SQLAlchemyRepository


class ReviewRepository(SQLAlchemyRepository):
    """Repository for Review entity with specific methods"""

    def __init__(self):
        super().__init__(Review)

