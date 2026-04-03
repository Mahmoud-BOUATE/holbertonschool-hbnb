from app.models.Base_Class import BaseClass
from app import db
from sqlalchemy.orm import validates

class Amenity(BaseClass):
    __tablename__ = 'amenities'
    name = db.Column(db.String, nullable=False)
    @validates('name')
    def validate_name(self, key, name):
        if name == "":
            raise ValueError("Name should be not empty")
        if len(name) > 50:
            raise ValueError("Name must be maximum 50 characters long")
        return name
