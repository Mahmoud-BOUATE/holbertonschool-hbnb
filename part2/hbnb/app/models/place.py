from app.models.Base_Class import BaseClass

class Place(BaseClass):
    def __init__(self, title, description, price, amenities, latitude, longitude, owner):
        super().__init__()
        self.title = title
        self.description = description
        self.price = price
        self.latitude = latitude
        self.longitude = longitude
        self.owner = owner # Relation place/user
        self.reviews = []       # Relations place / review
        self.amenities = amenities     # Relations place / amenities

    @property
    def title(self):
        return self._title

    @title.setter
    def title(self, value):
        self._title = self.validate_title(value)

    @property
    def price(self):
        return self._price

    @price.setter
    def price(self, value):
        self._price = self.validate_price(value)

    @property
    def latitude(self):
        return self._latitude

    @latitude.setter
    def latitude(self, value):
        self._latitude = self.validate_latitude(value)

    @property
    def longitude(self):
        return self._longitude

    @longitude.setter
    def longitude(self, value):
        self._longitude = self.validate_longitude(value)


    def validate_title(self, title):
        if title == "":
            raise ValueError("Title should be not empty")
        if len(title) > 50:
            raise ValueError("Title must be maximum 50 characters long")
        return title

    def validate_price(self, price):
        try:
            price = float(price)
            if price < 0:
                raise ValueError("Price must be non-negative")
            return price
        except (TypeError, ValueError):
            raise ValueError("Price must be a valid number")

    def validate_latitude(self, latitude):
        try:
            latitude = float(latitude)
            if latitude < -90 or latitude > 90:
                raise ValueError("Latitude must be between -90 and 90")
            return latitude
        except (TypeError, ValueError):
            raise ValueError("Latitude must be a valid number between -90 and 90")

    def validate_longitude(self, longitude):
        try:
            longitude = float(longitude)
            if longitude < -180 or longitude > 180:
                raise ValueError("longitude must be between -180 and 180")
            return longitude
        except (TypeError, ValueError):
            raise ValueError("longitude must be a valid number between -180 and 180")




    def add_review(self, review):
        self.reviews.append(review)

    def add_amenity(self, amenity):
        self.amenities.append(amenity)
        amenity.places.append(self)
