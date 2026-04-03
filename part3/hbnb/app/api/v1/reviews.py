from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from app.services import facade

api = Namespace('reviews', description='Review operations')

review_create_model = api.model('ReviewCreate', {
    'text': fields.String(required=True, description='text of the review'),
    'rating': fields.Integer(required=True, description='Rating of the place (1-5)'),
    'place_id': fields.String(required=True, description='ID of the place')
})

review_update_model = api.model('ReviewUpdate', {
    'text': fields.String(description='text of the review'),
    'rating': fields.Integer(description='Rating of the place (1-5)')
})

@api.route('/')
class ReviewList(Resource):
    @api.expect(review_create_model, validate=True)
    @api.response(201, 'Review successfully created')
    @api.response(400, 'Invalid input data')
    @jwt_required()
    def post(self):
        """Create a new review (authenticated user)"""
        current_user_id = get_jwt_identity()
        data = api.payload

        place = facade.get_place(data['place_id'])
        if not place:
            return {'error': 'Place not found'}, 404

        # Check ownership
        if place.owner.id == current_user_id:
            return {'error': 'You cannot review your own place.'}, 400

        # Check duplicate review
        if facade.user_already_reviewed_place(current_user_id, data['place_id']):
            return {'error': 'You have already reviewed this place.'}, 400

        try:
            review = facade.create_review({
                **data,
                'user_id': current_user_id
            })
            return {
                "id": review.id,
                "text": review.text,
                "rating": review.rating,
                "user_id": review.user.id,
                "place_id": review.place.id
            }, 201
        except ValueError as e:
            return {"error": str(e)}, 400

    @api.response(200, 'List of reviews retrieved successfully')
    def get(self):
        reviews = facade.get_all_reviews()
        return [{
            'id': a.id,
            'text': a.text,
            'rating': a.rating
        } for a in reviews
        ], 200

@api.route('/<review_id>')
class ReviewResource(Resource):
    @api.response(200, 'Review details retrieved successfully')
    @api.response(404, 'Review not found')
    def get(self, review_id):
        """Get review details by ID"""
        review = facade.get_review(review_id)
        if not review:
            return {"error": "Review not found"}, 404
        return {
            "id":review.id,
            "text":review.text,
            "rating":review.rating,
            "user_id":review.user.id,
            "place_id":review.place.id

        }, 200
    @api.expect(review_update_model, validate=True)
    @api.response(200, 'Review updated successfully')
    @api.response(404, 'Review not found')
    @api.response(400, 'Invalid input data')
    @jwt_required()
    def put(self, review_id):
        """Update a review (creator or admin)"""
        current_user = get_jwt()
        is_admin = current_user.get('is_admin', False)
        current_user_id = get_jwt_identity()

        review = facade.get_review(review_id)
        if not review:
            return {'error': 'Review not found'}, 404

        if not is_admin and review.user.id != current_user_id:
            return {'error': 'Unauthorized action'}, 403

        updated_data = api.payload
        try:
            facade.update_review(review_id, updated_data)
            return {"message": "Review updated successfully"}, 200
        except ValueError as exc:
            return {'error': str(exc)}, 400

    @api.response(200, 'Review deleted successfully')
    @api.response(404, 'Review not found')
    @jwt_required()
    def delete(self, review_id):
        """Delete a review (creator or admin)"""
        current_user = get_jwt()
        is_admin = current_user.get('is_admin', False)
        current_user_id = get_jwt_identity()

        review = facade.get_review(review_id)
        if not review:
            return {'error': 'Review not found'}, 404

        if not is_admin and review.user.id != current_user_id:
            return {'error': 'Unauthorized action'}, 403

        try:
            facade.delete_review(review_id)
            return {"message": "Review deleted successfully"}, 200
        except ValueError as exc:
            return {'error': str(exc)}, 400
