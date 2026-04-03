from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from app.services import facade


api = Namespace('places', description='Place operations')

# Define the models for related entities
amenity_model = api.model('PlaceAmenity', {
    'id': fields.String(description='Amenity ID'),
    'name': fields.String(description='Name of the amenity')
})

user_model = api.model('PlaceUser', {
    'id': fields.String(description='User ID'),
    'first_name': fields.String(description='First name of the owner'),
    'last_name': fields.String(description='Last name of the owner'),
    'email': fields.String(description='Email of the owner')
})
review_model = api.model('PlaceReview', {
    'id': fields.String(description='Review ID'),
    'text': fields.String(description='Text of the review'),
    'rating': fields.Integer(description='Rating of the place (1-5)'),
    'user_id': fields.String(description='ID of the user')
})
place_create_model = api.model('PlaceCreate', {
    'title': fields.String(required=True, description='Title of the place'),
    'description': fields.String(required=True, description='Description of the place'),
    'price': fields.Float(required=True, description='Price per night'),
    'latitude': fields.Float(required=True, description='Latitude of the place'),
    'longitude': fields.Float(required=True, description='Longitude of the place'),
    'amenities': fields.List(fields.String, description="List of amenities ID's to add")
})

place_update_model = api.model('PlaceUpdate', {
    'title': fields.String(description='Title of the place'),
    'description': fields.String(description='Description of the place'),
    'price': fields.Float(description='Price per night'),
    'latitude': fields.Float(description='Latitude of the place'),
    'longitude': fields.Float(description='Longitude of the place'),
    'amenities': fields.List(fields.String, description="List of amenities ID's to add")
})

@api.route('/')
class PlaceList(Resource):
    @api.expect(place_create_model, validate=True)
    @api.response(201, 'Place successfully created')
    @api.response(400, 'Invalid input data')
    @jwt_required()
    def post(self):
        """Register a new place"""
        current_user_id = get_jwt_identity()
        data = api.payload
        data['owner_id'] = current_user_id  # forcer le propriétaire sur le user connecté
        try:
            place = facade.create_place(data)
            return {
                "id": place.id,
                "title": place.title,
                "description": place.description,
                "price": place.price,
                "latitude": place.latitude,
                "longitude": place.longitude,
                "owner_id": place.owner.id
            }, 201
        except ValueError as e:
            return {"error": str(e)}, 400


    @api.response(200, 'List of places retrieved successfully')
    def get(self):
        """Retrieve a list of all places"""
        places = facade.get_all_places()
        return [{
            'id': a.id,
            'title': a.title,
            'price': a.price
            } for a in places], 200

@api.route('/<place_id>')
class PlaceResource(Resource):
    @api.response(200, 'Place details retrieved successfully')
    @api.response(404, 'Place not found')
    def get(self, place_id):
        place = facade.get_place(place_id)
        if not place:
            return {"error": "Place not found"}, 404

        return {
            "id": place.id,
            "title": place.title,
            "description": place.description,
            "price": place.price,
            "latitude": place.latitude,
            "longitude": place.longitude,
            "owner": {
                "id": place.owner.id,
                "first_name": place.owner.first_name,
                "last_name": place.owner.last_name,
                "email": place.owner.email
            },
            "amenities": [
                {"id": a.id, "name": a.name} for a in place.amenities
            ],
            "reviews": [
                {
                    "id": review.id,
                    "comment": review.text,
                    "rating": review.rating,
                    "reviewer_name": f"{review.user.first_name} {review.user.last_name}".strip()
                }
                for review in place.reviews
            ]
        }, 200

    @api.expect(place_update_model, validate=True)
    @api.response(200, 'Place updated successfully')
    @api.response(404, 'Place not found')
    @api.response(400, 'Invalid input data')
    @jwt_required()
    def put(self, place_id):
        """Update a place (owner or admin)"""
        current_user = get_jwt()
        is_admin = current_user.get('is_admin', False)
        current_user_id = get_jwt_identity()

        place = facade.get_place(place_id)
        if not place:
            return {"error": "Place not found"}, 404

        if not is_admin and place.owner.id != current_user_id:
            return {'error': 'Unauthorized action'}, 403

        try:
            updated_place = facade.update_place(place_id, api.payload)
            return {
                "id": updated_place.id,
                "title": updated_place.title,
                "description": updated_place.description,
                "price": updated_place.price,
                "latitude": updated_place.latitude,
                "longitude": updated_place.longitude
            }, 200
        except ValueError as exc:
            return {"error": str(exc)}, 400

    @api.response(200, 'Place deleted successfully')
    @api.response(404, 'Place not found')
    @jwt_required()
    def delete(self, place_id):
        """Delete a place (owner or admin)"""
        current_user = get_jwt()
        is_admin = current_user.get('is_admin', False)
        current_user_id = get_jwt_identity()

        place = facade.get_place(place_id)
        if not place:
            return {"error": "Place not found"}, 404

        if not is_admin and place.owner.id != current_user_id:
            return {'error': 'Unauthorized action'}, 403

        facade.delete_place(place_id)
        return {"message": "Place deleted successfully"}, 200

@api.route('/<place_id>/reviews')
class PlaceReviewList(Resource):
    @api.response(200, 'List of reviews for the place retrieved successfully')
    @api.response(404, 'Place not found')
    def get(self, place_id):
        """Get all reviews for a specific place"""
        place = facade.get_place(place_id)
        if not place:
            return {'error': 'Place not found'}, 404

        reviews = facade.get_reviews_by_place(place_id)
        if not reviews:
            return [], 200

        return [{
            "id": review.id,
            "comment": review.text,
            "rating": review.rating,
            "reviewer_name": f"{review.user.first_name} {review.user.last_name}".strip()
        } for review in reviews], 200









