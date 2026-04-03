from app.models.Base_Class import BaseClass
from app import db
from sqlalchemy.orm import validates

place_amenity = db.Table(
    'place_amenity',
    db.Column('place_id', db.String, db.ForeignKey('places.id'), primary_key=True),
    db.Column('amenity_id', db.String, db.ForeignKey('amenities.id'), primary_key=True)
)

class Place(BaseClass):
    __tablename__ = 'places'

    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String, nullable=False)
    price = db.Column(db.Float, nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)

    user_id = db.Column(db.String, db.ForeignKey('users.id'), nullable=False)
    reviews = db.relationship('Review', backref='place', lazy=True)
    amenities = db.relationship(
        'Amenity',
        secondary=place_amenity,
        backref=db.backref('places', lazy=True),
        lazy='subquery'
    )

    @validates('title')
    def validate_title(self, key, title):
        if title == "":
            raise ValueError("Title should be not empty")
        if len(title) > 50:
            raise ValueError("Title must be maximum 50 characters long")
        return title

    @validates('price')
    def validate_price(self, key, price):
        try:
            price = float(price)
            if price < 0:
                raise ValueError("Price must be non-negative")
            return price
        except (TypeError, ValueError):
            raise ValueError("Price must be a valid number")


    @validates('latitude')
    def validate_latitude(self, key, latitude):
        try:
            latitude = float(latitude)
            if latitude < -90 or latitude > 90:
                raise ValueError("Latitude must be between -90 and 90")
            return latitude
        except (TypeError, ValueError):
            raise ValueError("Latitude must be a valid number between -90 and 90")



    @validates('longitude')
    def validate_longitude(self, key, longitude):
        try:
            longitude = float(longitude)
            if longitude < -180 or longitude > 180:
                raise ValueError("longitude must be between -180 and 180")
            return longitude
        except (TypeError, ValueError):
            raise ValueError("longitude must be a valid number between -180 and 180")

