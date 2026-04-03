from app.models.Base_Class import BaseClass
from app import db
from sqlalchemy.orm import validates

class Review(BaseClass):
    __tablename__ = 'reviews'
    rating = db.Column(db.Integer, nullable=False)
    text = db.Column(db.String(100), nullable=False)

    user_id = db.Column(db.String, db.ForeignKey("users.id"), nullable=False)
    place_id = db.Column(db.String, db.ForeignKey("places.id"), nullable=False)

    @validates('text')
    def validate_text(self, key, text):
        if text == "":
            raise ValueError("Review should be not empty")
        return text



    @validates('rating')
    def validate_rating(self, key, rating):
        try:
            rating = int(rating)
            if rating > 5 or rating < 1:
                raise ValueError("Rating must be between 1 and 5")
            return rating
        except (TypeError, ValueError):
            raise ValueError("Rating must be between 1 and 5")

