from app.models.Base_Class import BaseClass

class Amenity(BaseClass):
    def __init__(self, name):
        super().__init__()
        self.name = name
        self.places = []

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = self.validate_name(value)

    def validate_name(self, name):
        if name == "":
            raise ValueError("Name should be not empty")
        if len(name) > 50:
            raise ValueError("Name must be maximum 50 characters long")
        return name