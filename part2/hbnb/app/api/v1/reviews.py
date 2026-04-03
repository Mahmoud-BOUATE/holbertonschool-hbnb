from flask_restx import Namespace, Resource, fields
from app.services import facade

api = Namespace('reviews', description='Review operations')

# Define the review model for input validation and documentation
review_model = api.model('Review', {
    'text': fields.String(required=True, description='text of the review'),
    'rating': fields.Integer(required=True, description='Rating of the place (1-5)'),
    'user_id': fields.String(required=True, description='ID of the user'),
    'place_id': fields.String(required=True, description='ID of the place')
})

@api.route('/')
class ReviewList(Resource):
    @api.expect(review_model, validate=True)
    @api.response(201, 'Review successfully created')
    @api.response(400, 'Invalid input data')
    def post(self):
        """Register a new review"""
        # Placeholder for the logic to register a new review
        try:
            review = facade.create_review(api.payload)
            return {
                "id":review.id,
                "text": review.text,
                "rating": review.rating,
                "user_id":review.user.id,
                "place_id":review.place.id

            }, 201
        except ValueError as e:
            return {"error": str(e)},400

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
    @api.expect(review_model)
    @api.response(200, 'Review updated successfully')
    @api.response(404, 'Review not found')
    @api.response(400, 'Invalid input data')
    def put(self, review_id):
        """Update a review's information"""
        review = facade.get_review(review_id)
        if not review:
            return {'error': 'Review not found'}, 404
        updated_data = api.payload
        try:
            facade.update_review(review_id, updated_data)
        except ValueError as exc:
            return {'error': str(exc)}, 400
        return {"message": "Review updated successfully"}, 200

    @api.response(200, 'Review deleted successfully')
    @api.response(404, 'Review not found')
    def delete(self, review_id):
        """Delete a review"""
        review = facade.get_review(review_id)
        if not review:
            return {'error': 'Review not found'}, 404

        try:
            facade.delete_review(review_id)
        except ValueError as exc:
            return {'error': str(exc)}, 400
        return {"message": "Review deleted successfully"}, 200