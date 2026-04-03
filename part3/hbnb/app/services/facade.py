from app import db
from app.persistence.repository import SQLAlchemyRepository
from app.persistence.repositories.user_repository import UserRepository
from app.persistence.repositories.place_repository import PlaceRepository
from app.persistence.repositories.review_repository import ReviewRepository
from app.persistence.repositories.amenity_repository import AmenityRepository


from app.models.user import User
from app.models.amenity import Amenity
from app.models.place import Place
from app.models.review import Review


class HBnBFacade:
    def __init__(self):
        self.user_repository = UserRepository()  # Switched to SQLAlchemyRepository
        self.place_repository = PlaceRepository() # Switched to SQLAlchemyRepository
        self.review_repository = ReviewRepository() # Switched to SQLAlchemyRepository
        self.amenity_repository = AmenityRepository() # Switched to SQLAlchemyRepository
        '''Gestion USER'''
    def create_user(self, user_data):
        # vérifier doublon
        for user in self.user_repository.get_all():
            if user.email == user_data["email"]:
                raise ValueError("Email already registered")
            #if user.user_id == user_data["user_id"]:
                #raise ValueError("User_id already registered")
        # Créer user
        user = User(
            first_name=user_data["first_name"],
            last_name=user_data["last_name"],
            email=user_data["email"],
            password=user_data["password"],
            is_admin=user_data.get("is_admin", False)
        )
        # Hacher le mot de passe avant stockage
        user.hash_password(user_data["password"])
        self.user_repository.add(user)
        return user

    def get_user(self, user_id):
        return self.user_repository.get(user_id)

    def get_all_users(self):
        return self.user_repository.get_all()

    def get_user_by_email(self, email):
        return self.user_repository.get_user_by_email(email)

    def update_user(self, user_id, user_data):
        user = self.user_repository.get(user_id)
        if not user:
            return None

        #update simple fields
        data = {}
        if "first_name" in user_data:
            data["first_name"] = user_data["first_name"]
        if "last_name" in user_data:
            data["last_name"] = user_data["last_name"]
        if "email" in user_data:
            data["email"] = user_data["email"]
        if "password" in user_data:
            user.hash_password(user_data["password"])

        self.user_repository.update(user.id, data)
        return user
    '''Gestion amenity'''
    def create_amenity(self, amenity_data):
        # Vérifier doublon
        for amenity in self.amenity_repository.get_all():
            if amenity.name == amenity_data["name"]:
                raise ValueError("Amenity already registered")

        # Créer amenities
        amenity = Amenity(
            name=amenity_data["name"]
        )
        self.amenity_repository.add(amenity)
        return amenity


    def get_amenity(self, amenity_id):
        return self.amenity_repository.get(amenity_id)

    def get_all_amenities(self):
        return self.amenity_repository.get_all()

    def update_amenity(self, amenity_id, amenity_data):
        amenity = self.amenity_repository.get(amenity_id)
        if not amenity:
            return None
        # Update simple fields
        data = {}
        if "name" in amenity_data:
            data["name"] = amenity_data["name"]
        self.amenity_repository.update(amenity.id, data)
        return amenity

    '''Gestion place'''
    def create_place(self, place_data):
    # Vérifier doublon
        for place in self.place_repository.get_all():
            if place.title == place_data["title"]:
                raise ValueError("Place already registered")

    # Vérifier owner
        owner = self.user_repository.get(place_data["owner_id"])
        if not owner:
            raise ValueError("Owner not found")

    # Vérifier amenities
        amenities = []
        for amenity_id in place_data.get("amenities", []):
            amenity = self.amenity_repository.get(amenity_id)
            if not amenity:
                raise ValueError(f"Amenity {amenity_id} not found")
            amenities.append(amenity)

    # Créer le Place
        place = Place(
            title=place_data["title"],
            description=place_data.get("description"),
            price=place_data["price"],
            latitude=place_data["latitude"],
            longitude=place_data["longitude"],
            user_id=place_data["owner_id"]
        )

        self.place_repository.add(place)

        # Add amenities via relationship
        for amenity in amenities:
            place.amenities.append(amenity)
        db.session.commit()

        return place

    def get_place(self, place_id):
        return self.place_repository.get(place_id)

    def get_all_places(self):
        return self.place_repository.get_all()

    def update_place(self, place_id, place_data):
        place = self.place_repository.get(place_id)
        if not place:
            return None

        # Update simple fields
        data = {}
        if "title" in place_data:
            data["title"] = place_data["title"]
        if "description" in place_data:
            data["description"] = place_data["description"]
        if "price" in place_data:
            data["price"] = place_data["price"]
        if "latitude" in place_data:
            data["latitude"] = place_data["latitude"]
        if "longitude" in place_data:
            data["longitude"] = place_data["longitude"]

        # Update amenities (ajout sans remplacer)
        if "amenities" in place_data:
            for amenity_id in place_data.get("amenities", []):
                amenity = self.amenity_repository.get(amenity_id)
                if not amenity:
                    raise ValueError(f"Amenity {amenity_id} not found")
                if amenity not in place.amenities:
                    place.amenities.append(amenity)

        self.place_repository.update(place.id, data)
        return place

    def delete_place(self, place_id):
        place = self.place_repository.get(place_id)
        if not place:
            return None

        # Delete associated reviews first
        for review in list(place.reviews):
            self.review_repository.delete(review.id)

        # Delete the place (amenities are removed via many-to-many cleanup)
        return self.place_repository.delete(place_id)


    '''Gestion Review'''
    def create_review(self, review_data):

        # Vérifier user
        user = self.user_repository.get(review_data["user_id"])
        if not user:
            raise ValueError("Owner not found")
        # Vérifier place
        place = self.place_repository.get(review_data["place_id"])
        if not place:
            raise ValueError("Place not found")

        review = Review(
            rating=review_data["rating"],
            text=review_data["text"],
            user_id=review_data["user_id"],
            place_id=review_data["place_id"]
        )
        self.review_repository.add(review)
        return review



    def get_review(self, review_id):
        return self.review_repository.get(review_id)

    def get_all_reviews(self):
        return self.review_repository.get_all()

    def get_reviews_by_place(self, place_id):
        return [
        review for review in self.review_repository.get_all()
        if review.place.id == place_id
        ]

    def update_review(self, review_id, review_data):
        review = self.review_repository.get(review_id)
        if not review:
            return None
        #update simple fields
        data = {}
        if "rating" in review_data:
            data["rating"] = review_data["rating"]
        if "text" in review_data:
            data["text"] = review_data["text"]

        self.review_repository.update(review.id, data)
        return review

    def delete_review(self, review_id):
        review = self.review_repository.get(review_id)
        if not review:
            return None
        # SQLAlchemy backrefs handle automatic removal from user.reviews and place.reviews
        return self.review_repository.delete(review_id)

    def user_already_reviewed_place(self, user_id, place_id):
        """Check if a user has already reviewed a specific place"""
        for review in self.review_repository.get_all():
            if review.user.id == user_id and review.place.id == place_id:
                return True
        return False
