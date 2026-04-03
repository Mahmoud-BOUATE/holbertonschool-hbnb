from app.models.Base_Class import BaseClass

class Review(BaseClass):
    def __init__(self, rating, text, user, place):
        super().__init__()
        self.rating = rating
        self.text = text
        self.user = user
        self.place = place

        if user:
            user.reviews.append(self)
        if place:
            place.reviews.append(self)


    @property
    def text(self):
        return self._text
    @text.setter
    def text(self,value):
        self._text = self.validate_text(value)
    @property
    def rating(self):
        return self._rating
    @rating.setter
    def rating(self,value):
        self._rating = self.validate_rating(value)

    def validate_text(self, text):
        if text == "":
            raise ValueError("Review should be not empty")
        return text

    def validate_rating(self, rating):
        try:
            rating = int(rating)
            if rating > 5 or rating < 1:
                raise ValueError("Rating must be between 1 and 5")
            return rating
        except (TypeError, ValueError):
            raise ValueError("Rating must be between 1 and 5")