import os
import sys
import unittest

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from app import create_app, db
from app.services import facade as facade_instance


class BaseApiTest(unittest.TestCase):
    def setUp(self):
        # Create app with test config
        self.app = create_app("config.TestConfig")
        self.app.config["TESTING"] = True

        with self.app.app_context():
            db.create_all()
            # Create an admin user for testing
            self.admin_user = facade_instance.create_user({
                'first_name': 'Admin',
                'last_name': 'User',
                'email': 'admin@test.com',
                'password': 'adminpass',
                'is_admin': True
            })

        self.client = self.app.test_client()

        # Get admin JWT token
        login_response = self.client.post('/api/v1/auth/login', json={
            'email': 'admin@test.com',
            'password': 'adminpass'
        })
        self.admin_token = login_response.get_json()['access_token']
        self.facade = facade_instance

    def get_admin_headers(self):
        """Return headers with admin JWT token"""
        return {'Authorization': f'Bearer {self.admin_token}'}

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def create_user(self, email="jane.doe@example.com", password="securepass"):
        payload = {
            "first_name": "Jane",
            "last_name": "Doe",
            "email": email,
            "password": password,
        }
        return self.client.post("/api/v1/users/", json=payload)

    def create_and_login_user(self, email, password="securepass"):
        create_response = self.create_user(email=email, password=password)
        self.assertEqual(create_response.status_code, 201)

        login_response = self.client.post('/api/v1/auth/login', json={
            'email': email,
            'password': password
        })
        self.assertEqual(login_response.status_code, 200)

        user_id = create_response.get_json()["id"]
        token = login_response.get_json()["access_token"]
        return user_id, token

    def get_auth_headers(self, token):
        return {'Authorization': f'Bearer {token}'}

    def create_amenity(self, name="WiFi"):
        payload = {"name": name}
        return self.client.post("/api/v1/amenities/", json=payload, headers=self.get_admin_headers())

    def create_place(self, token, amenity_ids=None, title="Cozy Cabin"):
        if amenity_ids is None:
            amenity_ids = []
        payload = {
            "title": title,
            "description": "Nice stay",
            "price": 120.0,
            "latitude": 45.0,
            "longitude": -122.0,
            "amenities": amenity_ids,
        }
        return self.client.post(
            "/api/v1/places/",
            json=payload,
            headers=self.get_auth_headers(token)
        )

    def create_review(self, token, place_id, rating=5, text="Great"):
        payload = {
            "text": text,
            "rating": rating,
            "place_id": place_id,
        }
        return self.client.post(
            "/api/v1/reviews/",
            json=payload,
            headers=self.get_auth_headers(token)
        )


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
            },
        )
        self.assertEqual(response.status_code, 201)

    def test_create_user_duplicate_email(self):
        response = self.create_user(email="dup@example.com")
        self.assertEqual(response.status_code, 201)
        response = self.create_user(email="dup@example.com")
        self.assertEqual(response.status_code, 400)

    def test_list_users(self):
        self.create_user()
        response = self.client.get("/api/v1/users/")
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.get_json(), list)
        self.assertEqual(len(response.get_json()), 2)

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
            },
            headers=self.get_admin_headers(),
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
            },
            headers=self.get_admin_headers(),
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
            },
            headers=self.get_admin_headers(),
        )
        self.assertEqual(response.status_code, 404)


class TestAmenityEndpoints(BaseApiTest):
    def test_create_amenity(self):
        response = self.create_amenity()
        self.assertEqual(response.status_code, 201)
        self.assertIn("id", response.get_json())

    def test_create_amenity_missing_name(self):
        response = self.client.post(
            "/api/v1/amenities/",
            json={},
            headers=self.get_admin_headers()
        )
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
            headers=self.get_admin_headers(),
        )
        self.assertEqual(response.status_code, 200)

    def test_update_amenity_not_found(self):
        response = self.client.put(
            "/api/v1/amenities/missing",
            json={"name": "Updated"},
            headers=self.get_admin_headers(),
        )
        self.assertEqual(response.status_code, 404)


class TestPlaceEndpoints(BaseApiTest):
    def test_create_place(self):
        _, owner_token = self.create_and_login_user(email="owner-1@example.com")
        amenity_response = self.create_amenity(name="Parking")
        amenity_id = amenity_response.get_json()["id"]

        response = self.create_place(token=owner_token, amenity_ids=[amenity_id])
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
        owner_id, owner_token = self.create_and_login_user(email="owner-2@example.com")
        response = self.client.post(
            "/api/v1/places/",
            json={
                "title": "Owner spoof test",
                "description": "desc",
                "price": 100,
                "latitude": 45.0,
                "longitude": -122.0,
                "owner_id": "missing-owner",
                "amenities": [],
            },
            headers=self.get_auth_headers(owner_token)
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.get_json()["owner_id"], owner_id)

    def test_create_place_invalid_amenity(self):
        _, owner_token = self.create_and_login_user(email="owner-3@example.com")
        response = self.create_place(token=owner_token, amenity_ids=["missing-amenity"])
        self.assertEqual(response.status_code, 400)

    def test_create_place_invalid_price(self):
        _, owner_token = self.create_and_login_user(email="owner-4@example.com")
        response = self.client.post(
            "/api/v1/places/",
            json={
                "title": "Bad Price",
                "description": "",
                "price": -1,
                "latitude": 45.0,
                "longitude": -122.0,
                "amenities": [],
            },
            headers=self.get_auth_headers(owner_token)
        )
        self.assertEqual(response.status_code, 400)

    def test_create_place_invalid_coordinates(self):
        _, owner_token = self.create_and_login_user(email="owner-5@example.com")
        response = self.client.post(
            "/api/v1/places/",
            json={
                "title": "Bad Coords",
                "description": "",
                "price": 10,
                "latitude": 100.0,
                "longitude": -200.0,
                "amenities": [],
            },
            headers=self.get_auth_headers(owner_token)
        )
        self.assertEqual(response.status_code, 400)

    def test_create_place_duplicate_title(self):
        _, owner_token = self.create_and_login_user(email="owner-6@example.com")
        response = self.create_place(token=owner_token, title="Same Title")
        self.assertEqual(response.status_code, 201)
        response = self.create_place(token=owner_token, title="Same Title")
        self.assertEqual(response.status_code, 400)

    def test_list_places(self):
        _, owner_token = self.create_and_login_user(email="owner-7@example.com")
        self.create_place(token=owner_token)
        response = self.client.get("/api/v1/places/")
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.get_json(), list)

    def test_get_place_success(self):
        _, owner_token = self.create_and_login_user(email="owner-8@example.com")
        place_response = self.create_place(token=owner_token)
        place_id = place_response.get_json()["id"]

        response = self.client.get(f"/api/v1/places/{place_id}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["id"], place_id)

    def test_get_place_not_found(self):
        response = self.client.get("/api/v1/places/missing")
        self.assertEqual(response.status_code, 404)

    def test_update_place(self):
        _, owner_token = self.create_and_login_user(email="owner-9@example.com")
        amenity_response = self.create_amenity(name="Kitchen")
        amenity_id = amenity_response.get_json()["id"]
        place_response = self.create_place(token=owner_token)
        place_id = place_response.get_json()["id"]

        response = self.client.put(
            f"/api/v1/places/{place_id}",
            json={
                "title": "Updated",
                "description": "Updated",
                "price": 150,
                "latitude": 45.0,
                "longitude": -122.0,
                "amenities": [amenity_id],
            },
            headers=self.get_auth_headers(owner_token)
        )
        self.assertEqual(response.status_code, 200)

    def test_update_place_invalid_amenity(self):
        _, owner_token = self.create_and_login_user(email="owner-10@example.com")
        place_response = self.create_place(token=owner_token)
        place_id = place_response.get_json()["id"]

        response = self.client.put(
            f"/api/v1/places/{place_id}",
            json={
                "title": "Updated",
                "description": "Updated",
                "price": 150,
                "latitude": 45.0,
                "longitude": -122.0,
                "amenities": ["missing-amenity"],
            },
            headers=self.get_auth_headers(owner_token)
        )
        self.assertEqual(response.status_code, 400)

    def test_update_place_not_found(self):
        _, owner_token = self.create_and_login_user(email="owner-11@example.com")
        response = self.client.put(
            "/api/v1/places/missing",
            json={
                "title": "Updated",
                "description": "Updated",
                "price": 150,
                "latitude": 45.0,
                "longitude": -122.0,
                "amenities": [],
            },
            headers=self.get_auth_headers(owner_token)
        )
        self.assertEqual(response.status_code, 404)

    def test_place_reviews_empty(self):
        _, owner_token = self.create_and_login_user(email="owner-12@example.com")
        place_response = self.create_place(token=owner_token)
        place_id = place_response.get_json()["id"]

        response = self.client.get(f"/api/v1/places/{place_id}/reviews")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), [])

    def test_place_reviews_with_data(self):
        _, owner_token = self.create_and_login_user(email="owner-13@example.com")
        place_response = self.create_place(token=owner_token)
        place_id = place_response.get_json()["id"]

        _, reviewer_token = self.create_and_login_user(email="reviewer@example.com")

        self.create_review(token=reviewer_token, place_id=place_id)

        response = self.client.get(f"/api/v1/places/{place_id}/reviews")
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.get_json(), list)
        self.assertEqual(len(response.get_json()), 1)


class TestReviewEndpoints(BaseApiTest):
    def test_create_review(self):
        _, owner_token = self.create_and_login_user(email="owner-14@example.com")
        place_response = self.create_place(token=owner_token)
        place_id = place_response.get_json()["id"]

        _, reviewer_token = self.create_and_login_user(email="reviewer2@example.com")

        response = self.create_review(token=reviewer_token, place_id=place_id)
        self.assertEqual(response.status_code, 201)
        self.assertIn("id", response.get_json())

    def test_create_review_missing_text(self):
        _, owner_token = self.create_and_login_user(email="owner-15@example.com")
        place_response = self.create_place(token=owner_token)
        place_id = place_response.get_json()["id"]

        _, reviewer_token = self.create_and_login_user(email="reviewer3@example.com")

        response = self.client.post(
            "/api/v1/reviews/",
            json={
                "rating": 5,
                "place_id": place_id,
            },
            headers=self.get_auth_headers(reviewer_token)
        )
        self.assertEqual(response.status_code, 400)

    def test_create_review_invalid_rating(self):
        _, owner_token = self.create_and_login_user(email="owner-16@example.com")
        place_response = self.create_place(token=owner_token)
        place_id = place_response.get_json()["id"]

        _, reviewer_token = self.create_and_login_user(email="reviewer4@example.com")

        response = self.create_review(token=reviewer_token, place_id=place_id, rating=10)
        self.assertEqual(response.status_code, 400)

    def test_create_review_invalid_user(self):
        _, owner_token = self.create_and_login_user(email="owner-17@example.com")
        place_response = self.create_place(token=owner_token)
        place_id = place_response.get_json()["id"]

        response = self.create_review(token=owner_token, place_id=place_id)
        self.assertEqual(response.status_code, 400)

    def test_create_review_invalid_place(self):
        _, reviewer_token = self.create_and_login_user(email="reviewer5@example.com")
        response = self.create_review(token=reviewer_token, place_id="missing")
        self.assertEqual(response.status_code, 404)

    def test_list_reviews(self):
        _, owner_token = self.create_and_login_user(email="owner-18@example.com")
        place_response = self.create_place(token=owner_token)
        place_id = place_response.get_json()["id"]

        _, reviewer_token = self.create_and_login_user(email="reviewer6@example.com")

        self.create_review(token=reviewer_token, place_id=place_id)

        response = self.client.get("/api/v1/reviews/")
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.get_json(), list)

    def test_get_review_success(self):
        _, owner_token = self.create_and_login_user(email="owner-19@example.com")
        place_response = self.create_place(token=owner_token)
        place_id = place_response.get_json()["id"]

        _, reviewer_token = self.create_and_login_user(email="reviewer7@example.com")

        review_response = self.create_review(token=reviewer_token, place_id=place_id)
        review_id = review_response.get_json()["id"]

        response = self.client.get(f"/api/v1/reviews/{review_id}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["id"], review_id)

    def test_get_review_not_found(self):
        response = self.client.get("/api/v1/reviews/missing")
        self.assertEqual(response.status_code, 404)

    def test_update_review(self):
        _, owner_token = self.create_and_login_user(email="owner-20@example.com")
        place_response = self.create_place(token=owner_token)
        place_id = place_response.get_json()["id"]

        _, reviewer_token = self.create_and_login_user(email="reviewer8@example.com")

        review_response = self.create_review(token=reviewer_token, place_id=place_id)
        review_id = review_response.get_json()["id"]

        response = self.client.put(
            f"/api/v1/reviews/{review_id}",
            json={
                "text": "Updated",
                "rating": 4,
            },
            headers=self.get_auth_headers(reviewer_token)
        )
        self.assertEqual(response.status_code, 200)

    def test_update_review_invalid_rating(self):
        _, owner_token = self.create_and_login_user(email="owner-21@example.com")
        place_response = self.create_place(token=owner_token)
        place_id = place_response.get_json()["id"]

        _, reviewer_token = self.create_and_login_user(email="reviewer9@example.com")

        review_response = self.create_review(token=reviewer_token, place_id=place_id)
        review_id = review_response.get_json()["id"]

        response = self.client.put(
            f"/api/v1/reviews/{review_id}",
            json={
                "text": "Updated",
                "rating": 10,
            },
            headers=self.get_auth_headers(reviewer_token)
        )
        self.assertEqual(response.status_code, 400)

    def test_update_review_not_found(self):
        response = self.client.put(
            "/api/v1/reviews/missing",
            json={
                "text": "Updated",
                "rating": 4,
            },
            headers=self.get_admin_headers()
        )
        self.assertEqual(response.status_code, 404)

    def test_delete_review(self):
        _, owner_token = self.create_and_login_user(email="owner-22@example.com")
        place_response = self.create_place(token=owner_token)
        place_id = place_response.get_json()["id"]

        _, reviewer_token = self.create_and_login_user(email="reviewer10@example.com")

        review_response = self.create_review(token=reviewer_token, place_id=place_id)
        review_id = review_response.get_json()["id"]

        response = self.client.delete(
            f"/api/v1/reviews/{review_id}",
            headers=self.get_auth_headers(reviewer_token)
        )
        self.assertEqual(response.status_code, 200)

    def test_delete_review_not_found(self):
        response = self.client.delete(
            "/api/v1/reviews/missing",
            headers=self.get_admin_headers()
        )
        self.assertEqual(response.status_code, 404)


if __name__ == "__main__":
    unittest.main()
