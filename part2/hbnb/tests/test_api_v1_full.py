import os
import sys
import unittest

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from app import create_app
from app.persistence.repository import InMemoryRepository
from app.services import facade as facade_instance


class BaseApiTest(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config["TESTING"] = True
        self.client = self.app.test_client()

        facade_instance.user_repo = InMemoryRepository()
        facade_instance.amenity_repo = InMemoryRepository()
        facade_instance.place_repo = InMemoryRepository()
        facade_instance.review_repo = InMemoryRepository()
        self.facade = facade_instance

    def create_user(self, email="jane.doe@example.com", user_id="user-1"):
        payload = {
            "first_name": "Jane",
            "last_name": "Doe",
            "email": email,
            "password": "securepass",
            "user_id": user_id,
        }
        return self.client.post("/api/v1/users/", json=payload)

    def create_amenity(self, name="WiFi"):
        payload = {"name": name}
        return self.client.post("/api/v1/amenities/", json=payload)

    def create_place(self, owner_id, amenity_ids=None, title="Cozy Cabin"):
        if amenity_ids is None:
            amenity_ids = []
        payload = {
            "title": title,
            "description": "Nice stay",
            "price": 120.0,
            "latitude": 45.0,
            "longitude": -122.0,
            "owner_id": owner_id,
            "amenities": amenity_ids,
        }
        return self.client.post("/api/v1/places/", json=payload)

    def create_review(self, user_id, place_id, rating=5, text="Great"):
        payload = {
            "text": text,
            "rating": rating,
            "user_id": user_id,
            "place_id": place_id,
        }
        return self.client.post("/api/v1/reviews/", json=payload)


class TestUserEndpoints(BaseApiTest):
    def test_create_user(self):
        response = self.create_user()
        self.assertEqual(response.status_code, 201)
        self.assertIn("id", response.get_json())

    def test_create_user_invalid_email(self):
        response = self.create_user(email="invalid-email")
        self.assertEqual(response.status_code, 400)

    def test_create_user_missing_required(self):
        response = self.client.post(
            "/api/v1/users/",
            json={
                "first_name": "Jane",
                "last_name": "Doe",
                "email": "jane.doe@example.com",
                "password": "securepass",
            },
        )
        self.assertEqual(response.status_code, 400)

    def test_create_user_short_password(self):
        response = self.client.post(
            "/api/v1/users/",
            json={
                "first_name": "Jane",
                "last_name": "Doe",
                "email": "jane.short@example.com",
                "password": "short",
                "user_id": "user-short",
            },
        )
        self.assertEqual(response.status_code, 400)

    def test_create_user_duplicate_email(self):
        response = self.create_user(email="dup@example.com", user_id="user-1")
        self.assertEqual(response.status_code, 201)
        response = self.create_user(email="dup@example.com", user_id="user-2")
        self.assertEqual(response.status_code, 400)

    def test_list_users(self):
        self.create_user()
        response = self.client.get("/api/v1/users/")
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.get_json(), list)
        self.assertEqual(len(response.get_json()), 1)

    def test_get_user_success(self):
        create_response = self.create_user()
        user_id = create_response.get_json()["id"]
        response = self.client.get(f"/api/v1/users/{user_id}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["id"], user_id)

    def test_get_user_not_found(self):
        response = self.client.get("/api/v1/users/missing")
        self.assertEqual(response.status_code, 404)

    def test_update_user(self):
        create_response = self.create_user()
        user_id = create_response.get_json()["id"]
        response = self.client.put(
            f"/api/v1/users/{user_id}",
            json={
                "first_name": "Janet",
                "last_name": "Doe",
                "email": "janet@example.com",
                "password": "securepass",
                "user_id": user_id,
            },
        )
        self.assertEqual(response.status_code, 200)
        response = self.client.get(f"/api/v1/users/{user_id}")
        self.assertEqual(response.get_json()["first_name"], "Janet")

    def test_update_user_invalid_email(self):
        create_response = self.create_user()
        user_id = create_response.get_json()["id"]
        response = self.client.put(
            f"/api/v1/users/{user_id}",
            json={
                "first_name": "Jane",
                "last_name": "Doe",
                "email": "invalid-email",
                "password": "securepass",
                "user_id": user_id,
            },
        )
        self.assertEqual(response.status_code, 400)

    def test_update_user_not_found(self):
        response = self.client.put(
            "/api/v1/users/missing",
            json={
                "first_name": "Jane",
                "last_name": "Doe",
                "email": "jane.doe@example.com",
                "password": "securepass",
                "user_id": "missing",
            },
        )
        self.assertEqual(response.status_code, 404)


class TestAmenityEndpoints(BaseApiTest):
    def test_create_amenity(self):
        response = self.create_amenity()
        self.assertEqual(response.status_code, 201)
        self.assertIn("id", response.get_json())

    def test_create_amenity_missing_name(self):
        response = self.client.post("/api/v1/amenities/", json={})
        self.assertEqual(response.status_code, 400)

    def test_create_amenity_duplicate_name(self):
        response = self.create_amenity(name="Pool")
        self.assertEqual(response.status_code, 201)
        response = self.create_amenity(name="Pool")
        self.assertEqual(response.status_code, 400)

    def test_list_amenities(self):
        self.create_amenity()
        response = self.client.get("/api/v1/amenities/")
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.get_json(), list)

    def test_get_amenity_success(self):
        create_response = self.create_amenity(name="Kitchen")
        amenity_id = create_response.get_json()["id"]
        response = self.client.get(f"/api/v1/amenities/{amenity_id}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["id"], amenity_id)

    def test_get_amenity_not_found(self):
        response = self.client.get("/api/v1/amenities/missing")
        self.assertEqual(response.status_code, 404)

    def test_update_amenity(self):
        create_response = self.create_amenity(name="Kitchen")
        amenity_id = create_response.get_json()["id"]
        response = self.client.put(
            f"/api/v1/amenities/{amenity_id}",
            json={"name": "Updated"},
        )
        self.assertEqual(response.status_code, 200)

    def test_update_amenity_not_found(self):
        response = self.client.put(
            "/api/v1/amenities/missing",
            json={"name": "Updated"},
        )
        self.assertEqual(response.status_code, 404)


class TestPlaceEndpoints(BaseApiTest):
    def test_create_place(self):
        user_response = self.create_user(user_id="owner-1")
        owner_id = user_response.get_json()["id"]
        amenity_response = self.create_amenity(name="Parking")
        amenity_id = amenity_response.get_json()["id"]

        response = self.create_place(owner_id=owner_id, amenity_ids=[amenity_id])
        self.assertEqual(response.status_code, 201)
        self.assertIn("id", response.get_json())

    def test_create_place_missing_owner(self):
        response = self.client.post(
            "/api/v1/places/",
            json={
                "title": "No Owner",
                "price": 100,
                "latitude": 45.0,
                "longitude": -122.0,
            },
        )
        self.assertEqual(response.status_code, 400)

    def test_create_place_invalid_owner(self):
        response = self.create_place(owner_id="missing-owner")
        self.assertEqual(response.status_code, 400)

    def test_create_place_invalid_amenity(self):
        user_response = self.create_user(user_id="owner-2")
        owner_id = user_response.get_json()["id"]
        response = self.create_place(owner_id=owner_id, amenity_ids=["missing-amenity"])
        self.assertEqual(response.status_code, 400)

    def test_create_place_invalid_price(self):
        user_response = self.create_user(user_id="owner-3")
        owner_id = user_response.get_json()["id"]
        response = self.client.post(
            "/api/v1/places/",
            json={
                "title": "Bad Price",
                "description": "",
                "price": -1,
                "latitude": 45.0,
                "longitude": -122.0,
                "owner_id": owner_id,
                "amenities": [],
            },
        )
        self.assertEqual(response.status_code, 400)

    def test_create_place_invalid_coordinates(self):
        user_response = self.create_user(user_id="owner-4")
        owner_id = user_response.get_json()["id"]
        response = self.client.post(
            "/api/v1/places/",
            json={
                "title": "Bad Coords",
                "description": "",
                "price": 10,
                "latitude": 100.0,
                "longitude": -200.0,
                "owner_id": owner_id,
                "amenities": [],
            },
        )
        self.assertEqual(response.status_code, 400)

    def test_create_place_duplicate_title(self):
        user_response = self.create_user(user_id="owner-5")
        owner_id = user_response.get_json()["id"]
        response = self.create_place(owner_id=owner_id, title="Same Title")
        self.assertEqual(response.status_code, 201)
        response = self.create_place(owner_id=owner_id, title="Same Title")
        self.assertEqual(response.status_code, 400)

    def test_list_places(self):
        user_response = self.create_user(user_id="owner-6")
        owner_id = user_response.get_json()["id"]
        self.create_place(owner_id=owner_id)
        response = self.client.get("/api/v1/places/")
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.get_json(), list)

    def test_get_place_success(self):
        user_response = self.create_user(user_id="owner-7")
        owner_id = user_response.get_json()["id"]
        place_response = self.create_place(owner_id=owner_id)
        place_id = place_response.get_json()["id"]

        response = self.client.get(f"/api/v1/places/{place_id}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["id"], place_id)

    def test_get_place_not_found(self):
        response = self.client.get("/api/v1/places/missing")
        self.assertEqual(response.status_code, 404)

    def test_update_place(self):
        user_response = self.create_user(user_id="owner-8")
        owner_id = user_response.get_json()["id"]
        amenity_response = self.create_amenity(name="Kitchen")
        amenity_id = amenity_response.get_json()["id"]
        place_response = self.create_place(owner_id=owner_id)
        place_id = place_response.get_json()["id"]

        response = self.client.put(
            f"/api/v1/places/{place_id}",
            json={
                "title": "Updated",
                "description": "Updated",
                "price": 150,
                "latitude": 45.0,
                "longitude": -122.0,
                "owner_id": owner_id,
                "amenities": [amenity_id],
            },
        )
        self.assertEqual(response.status_code, 200)

    def test_update_place_invalid_amenity(self):
        user_response = self.create_user(user_id="owner-9")
        owner_id = user_response.get_json()["id"]
        place_response = self.create_place(owner_id=owner_id)
        place_id = place_response.get_json()["id"]

        response = self.client.put(
            f"/api/v1/places/{place_id}",
            json={
                "title": "Updated",
                "description": "Updated",
                "price": 150,
                "latitude": 45.0,
                "longitude": -122.0,
                "owner_id": owner_id,
                "amenities": ["missing-amenity"],
            },
        )
        self.assertEqual(response.status_code, 400)

    def test_update_place_not_found(self):
        response = self.client.put(
            "/api/v1/places/missing",
            json={
                "title": "Updated",
                "description": "Updated",
                "price": 150,
                "latitude": 45.0,
                "longitude": -122.0,
                "owner_id": "missing",
                "amenities": [],
            },
        )
        self.assertEqual(response.status_code, 404)

    def test_place_reviews_empty(self):
        user_response = self.create_user(user_id="owner-10")
        owner_id = user_response.get_json()["id"]
        place_response = self.create_place(owner_id=owner_id)
        place_id = place_response.get_json()["id"]

        response = self.client.get(f"/api/v1/places/{place_id}/reviews")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), [])

    def test_place_reviews_with_data(self):
        user_response = self.create_user(user_id="owner-11")
        owner_id = user_response.get_json()["id"]
        place_response = self.create_place(owner_id=owner_id)
        place_id = place_response.get_json()["id"]

        reviewer_response = self.create_user(
            email="reviewer@example.com",
            user_id="reviewer-1",
        )
        reviewer_id = reviewer_response.get_json()["id"]

        self.create_review(user_id=reviewer_id, place_id=place_id)

        response = self.client.get(f"/api/v1/places/{place_id}/reviews")
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.get_json(), list)
        self.assertEqual(len(response.get_json()), 1)


class TestReviewEndpoints(BaseApiTest):
    def test_create_review(self):
        user_response = self.create_user(user_id="owner-12")
        owner_id = user_response.get_json()["id"]
        place_response = self.create_place(owner_id=owner_id)
        place_id = place_response.get_json()["id"]

        reviewer_response = self.create_user(
            email="reviewer2@example.com",
            user_id="reviewer-2",
        )
        reviewer_id = reviewer_response.get_json()["id"]

        response = self.create_review(user_id=reviewer_id, place_id=place_id)
        self.assertEqual(response.status_code, 201)
        self.assertIn("id", response.get_json())

    def test_create_review_missing_text(self):
        user_response = self.create_user(user_id="owner-13")
        owner_id = user_response.get_json()["id"]
        place_response = self.create_place(owner_id=owner_id)
        place_id = place_response.get_json()["id"]

        reviewer_response = self.create_user(
            email="reviewer3@example.com",
            user_id="reviewer-3",
        )
        reviewer_id = reviewer_response.get_json()["id"]

        response = self.client.post(
            "/api/v1/reviews/",
            json={
                "rating": 5,
                "user_id": reviewer_id,
                "place_id": place_id,
            },
        )
        self.assertEqual(response.status_code, 400)

    def test_create_review_invalid_rating(self):
        user_response = self.create_user(user_id="owner-14")
        owner_id = user_response.get_json()["id"]
        place_response = self.create_place(owner_id=owner_id)
        place_id = place_response.get_json()["id"]

        reviewer_response = self.create_user(
            email="reviewer4@example.com",
            user_id="reviewer-4",
        )
        reviewer_id = reviewer_response.get_json()["id"]

        response = self.create_review(user_id=reviewer_id, place_id=place_id, rating=10)
        self.assertEqual(response.status_code, 400)

    def test_create_review_invalid_user(self):
        response = self.create_review(user_id="missing", place_id="missing")
        self.assertEqual(response.status_code, 400)

    def test_create_review_invalid_place(self):
        reviewer_response = self.create_user(
            email="reviewer5@example.com",
            user_id="reviewer-5",
        )
        reviewer_id = reviewer_response.get_json()["id"]
        response = self.create_review(user_id=reviewer_id, place_id="missing")
        self.assertEqual(response.status_code, 400)

    def test_list_reviews(self):
        user_response = self.create_user(user_id="owner-15")
        owner_id = user_response.get_json()["id"]
        place_response = self.create_place(owner_id=owner_id)
        place_id = place_response.get_json()["id"]

        reviewer_response = self.create_user(
            email="reviewer6@example.com",
            user_id="reviewer-6",
        )
        reviewer_id = reviewer_response.get_json()["id"]

        self.create_review(user_id=reviewer_id, place_id=place_id)

        response = self.client.get("/api/v1/reviews/")
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.get_json(), list)

    def test_get_review_success(self):
        user_response = self.create_user(user_id="owner-16")
        owner_id = user_response.get_json()["id"]
        place_response = self.create_place(owner_id=owner_id)
        place_id = place_response.get_json()["id"]

        reviewer_response = self.create_user(
            email="reviewer7@example.com",
            user_id="reviewer-7",
        )
        reviewer_id = reviewer_response.get_json()["id"]

        review_response = self.create_review(user_id=reviewer_id, place_id=place_id)
        review_id = review_response.get_json()["id"]

        response = self.client.get(f"/api/v1/reviews/{review_id}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["id"], review_id)

    def test_get_review_not_found(self):
        response = self.client.get("/api/v1/reviews/missing")
        self.assertEqual(response.status_code, 404)

    def test_update_review(self):
        user_response = self.create_user(user_id="owner-17")
        owner_id = user_response.get_json()["id"]
        place_response = self.create_place(owner_id=owner_id)
        place_id = place_response.get_json()["id"]

        reviewer_response = self.create_user(
            email="reviewer8@example.com",
            user_id="reviewer-8",
        )
        reviewer_id = reviewer_response.get_json()["id"]

        review_response = self.create_review(user_id=reviewer_id, place_id=place_id)
        review_id = review_response.get_json()["id"]

        response = self.client.put(
            f"/api/v1/reviews/{review_id}",
            json={
                "text": "Updated",
                "rating": 4,
                "user_id": reviewer_id,
                "place_id": place_id,
            },
        )
        self.assertEqual(response.status_code, 200)

    def test_update_review_invalid_rating(self):
        user_response = self.create_user(user_id="owner-18")
        owner_id = user_response.get_json()["id"]
        place_response = self.create_place(owner_id=owner_id)
        place_id = place_response.get_json()["id"]

        reviewer_response = self.create_user(
            email="reviewer9@example.com",
            user_id="reviewer-9",
        )
        reviewer_id = reviewer_response.get_json()["id"]

        review_response = self.create_review(user_id=reviewer_id, place_id=place_id)
        review_id = review_response.get_json()["id"]

        response = self.client.put(
            f"/api/v1/reviews/{review_id}",
            json={
                "text": "Updated",
                "rating": 10,
                "user_id": reviewer_id,
                "place_id": place_id,
            },
        )
        self.assertEqual(response.status_code, 400)

    def test_update_review_not_found(self):
        response = self.client.put(
            "/api/v1/reviews/missing",
            json={
                "text": "Updated",
                "rating": 4,
                "user_id": "missing",
                "place_id": "missing",
            },
        )
        self.assertEqual(response.status_code, 404)

    def test_delete_review(self):
        user_response = self.create_user(user_id="owner-19")
        owner_id = user_response.get_json()["id"]
        place_response = self.create_place(owner_id=owner_id)
        place_id = place_response.get_json()["id"]

        reviewer_response = self.create_user(
            email="reviewer10@example.com",
            user_id="reviewer-10",
        )
        reviewer_id = reviewer_response.get_json()["id"]

        review_response = self.create_review(user_id=reviewer_id, place_id=place_id)
        review_id = review_response.get_json()["id"]

        response = self.client.delete(f"/api/v1/reviews/{review_id}")
        self.assertEqual(response.status_code, 200)

    def test_delete_review_not_found(self):
        response = self.client.delete("/api/v1/reviews/missing")
        self.assertEqual(response.status_code, 404)


if __name__ == "__main__":
    unittest.main()
