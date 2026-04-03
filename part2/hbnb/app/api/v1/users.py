from flask_restx import Namespace, Resource, fields
from app.services import facade

api = Namespace('users', description='User operations')

# Define the user model for input validation and documentation
user_model = api.model('User', {
    'user_id': fields.String(required=True, description='ID of the user'),
    'first_name': fields.String(required=True, description='First name of the user'),
    'last_name': fields.String(required=True, description='Last name of the user'),
    'email': fields.String(required=True, description='Email of the user'),
    'password': fields.String(required=True, description='Password of the user')
})

@api.route('/')
class UserList(Resource):
    @api.expect(user_model, validate=True)
    @api.response(201, 'User successfully created')
    @api.response(400, 'Email already registered')
    @api.response(400, 'Invalid input data')

    def post(self):
        """Register a new user"""
        try:
            user = facade.create_user(api.payload)
            return {
                "id": user.id,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "email": user.email,
                "password": user.password,
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
            'password':user.password
            }, 200


    @api.expect(user_model)
    @api.response(200, 'user updated successfully')
    @api.response(404, 'user not found')
    @api.response(400, 'Invalid input data')
    def put(self, user_id):
        user = facade.get_user(user_id)
        if not user:
             return {'error': 'user not found'}, 404
        updated_data = api.payload
        try:
            facade.update_user(user_id, updated_data)
        except ValueError as exc:
            return {'error': str(exc)}, 400
        return {
            "id": user.id,
            "first_name":user.first_name,
            "last_name":user.last_name,
            "email":user.email

        },200


