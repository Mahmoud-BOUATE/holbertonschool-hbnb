HBnB API (Part 2)
=================

Overview
--------
This project exposes a simple REST API for managing users, amenities, places,
and reviews. It uses Flask-RESTX and an in-memory repository (no database).

Project structure
-----------------
- app/ contains the application code.
- app/api/v1/ contains the versioned REST endpoints.
- app/models/ contains the business entities and validation.
- app/services/ implements the Facade layer.
- app/persistence/ contains the in-memory repository.
- run.py starts the Flask application.
- config.py defines basic config settings.

Main features
-------------
- User management with validation (email format, password length >= 8).
- Amenity management with unique name constraint.
- Place management linked to an owner and amenities.
- Review management linked to a user and a place.
- CRUD endpoints for users, amenities, places, and reviews.

API endpoints (v1)
------------------
Base path: /api/v1

Users
- POST /users/ create a user
- GET /users/ list users
- GET /users/<user_id> get user details
- PUT /users/<user_id> update user

Amenities
- POST /amenities/ create an amenity
- GET /amenities/ list amenities
- GET /amenities/<amenity_id> get amenity details
- PUT /amenities/<amenity_id> update amenity

Places
- POST /places/ create a place (requires valid owner_id and amenity ids)
- GET /places/ list places
- GET /places/<place_id> get place details (owner, amenities, reviews)
- PUT /places/<place_id> update a place (can add amenities)
- GET /places/<place_id>/reviews list reviews for a place

Reviews
- POST /reviews/ create a review (requires valid user_id and place_id)
- GET /reviews/ list reviews
- GET /reviews/<review_id> get review details
- PUT /reviews/<review_id> update a review
- DELETE /reviews/<review_id> delete a review

Detailed operations
-------------------
All endpoints accept and return JSON. Validation happens in the models and
Facade layer. Errors return status 400 or 404 with a JSON body like
{"error": "message"}.

Users
~~~~~
Create user
- POST /users/
- Required fields: user_id, first_name, last_name, email, password
- Validations: email format, password length >= 8
- Success: 201 with user payload

Get user
- GET /users/<user_id>
- Success: 200 with user payload
- Not found: 404

Update user
- PUT /users/<user_id>
- Updatable fields: first_name, last_name, email, password
- Validations: same as create
- Success: 200 with updated payload

List users
- GET /users/
- Success: 200 list of users

Amenities
~~~~~~~~~
Create amenity
- POST /amenities/
- Required fields: name
- Validations: unique name
- Success: 201 with amenity payload

Get amenity
- GET /amenities/<amenity_id>
- Success: 200 with amenity payload
- Not found: 404

Update amenity
- PUT /amenities/<amenity_id>
- Updatable fields: name
- Validations: name cannot conflict with an existing amenity
- Success: 200 with confirmation

List amenities
- GET /amenities/
- Success: 200 list of amenities

Places
~~~~~~
Create place
- POST /places/
- Required fields: title, price, latitude, longitude, owner_id
- Optional fields: description, amenities (list of amenity ids)
- Validations: owner exists, amenities exist, price >= 0,
  latitude in [-90, 90], longitude in [-180, 180], unique title
- Success: 201 with place payload

Get place
- GET /places/<place_id>
- Success: 200 with owner, amenities, and reviews embedded
- Not found: 404

Update place
- PUT /places/<place_id>
- Updatable fields: title, description, price, latitude, longitude, amenities
- Behavior: amenities are added (not replaced)
- Validations: amenities exist, coordinate ranges, price >= 0
- Success: 200 with confirmation

List places
- GET /places/
- Success: 200 list of places (id, title, latitude, longitude)

Place reviews
- GET /places/<place_id>/reviews
- Success: 200 list (empty list if no reviews)

Reviews
~~~~~~~
Create review
- POST /reviews/
- Required fields: text, rating, user_id, place_id
- Validations: rating between 1 and 5, user exists, place exists
- Success: 201 with review payload

Get review
- GET /reviews/<review_id>
- Success: 200 with review payload
- Not found: 404

Update review
- PUT /reviews/<review_id>
- Updatable fields: text, rating
- Validations: rating between 1 and 5
- Success: 200 with confirmation

Delete review
- DELETE /reviews/<review_id>
- Success: 200 with confirmation
- Not found: 404

Install
-------
pip install -r requirements.txt

Run
---
python run.py

Tests
-----
python -m unittest discover -s tests -p "test_api_v1_full.py"
