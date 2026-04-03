from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt, verify_jwt_in_request
from jwt.exceptions import PyJWTError
from app.services import facade

api = Namespace('users', description='User operations')

user_create_model = api.model('UserCreate', {
    'first_name': fields.String(required=True, description='First name of the user'),
    'last_name': fields.String(required=True, description='Last name of the user'),
    'email': fields.String(required=True, description='Email of the user'),
    'password': fields.String(required=True, description='Password of the user'),
    'is_admin': fields.Boolean(description='Admin flag')
})

user_update_model = api.model('UserUpdate', {
    'first_name': fields.String(description='First name of the user'),
    'last_name': fields.String(description='Last name of the user'),
    'email': fields.String(description='Email of the user'),
    'password': fields.String(description='Password of the user'),
    'is_admin': fields.Boolean(description='Admin flag')
})

@api.route('/')
class UserList(Resource):
    @api.expect(user_create_model, validate=True)
    @api.response(201, 'User successfully created')
    @api.response(400, 'Email already registered')
    @api.response(403, 'Admin privileges required')
    def post(self):
        """Create a new user (public registration or admin creation)"""
        # Check if user is authenticated
        is_admin = False
        try:
            verify_jwt_in_request()
            current_user = get_jwt()
            is_admin = current_user.get('is_admin', False)
        except Exception:
            # No authentication or invalid token - public registration
            pass

        email = api.payload.get('email')
        if facade.get_user_by_email(email):
            return {'error': 'Email already registered'}, 400

        # Prepare user data
        user_data = api.payload.copy()

        # If not admin, remove is_admin from payload and it will default to False
        if not is_admin:
            user_data.pop('is_admin', None)  # Remove is_admin field completely

        try:
            user = facade.create_user(user_data)
            return {
                "id": user.id,
                "Message": "User successfully created"
            }, 201
        except ValueError as e:
            return {"error": str(e)}, 400

    @api.response(200, 'List users retrieved successfully')
    def get(self):
        """Retrieve a list of all users"""
        users = facade.get_all_users()
        return [{
            'id': a.id,
            'first_name': a.first_name,
            'last_name': a.last_name,
            'email': a.email
        } for a in users], 200

@api.route('/<user_id>')
class UserResource(Resource):
    @api.response(404, 'User not found')
    def get(self, user_id):
        """Get user details by ID"""
        user = facade.get_user(user_id)
        if not user:
            return {'error': 'User not found'}, 404
        return {
            'id': user.id,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
            }, 200

    @api.expect(user_update_model, validate=True)
    @api.response(200, 'user updated successfully')
    @api.response(404, 'user not found')
    @api.response(403, 'Admin privileges required')
    @jwt_required()
    def put(self, user_id):
        """Admin: update any user's details"""
        current_user = get_jwt()
        if not current_user.get('is_admin'):
            return {'error': 'Admin privileges required'}, 403

        user = facade.get_user(user_id)
        if not user:
            return {'error': 'User not found'}, 404

        updated_data = api.payload

        email = updated_data.get('email')
        if email:
            existing_user = facade.get_user_by_email(email)
            if existing_user and existing_user.id != user_id:
                return {'error': 'Email already in use'}, 400

        try:
            user = facade.update_user(user_id, updated_data)
        except ValueError as exc:
            return {'error': str(exc)}, 400

        return {
            "id": user.id,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email
        }, 200

