from app.models.Base_Class import BaseClass
from email_validator import validate_email, EmailNotValidError
from app import db, bcrypt
from sqlalchemy.orm import validates

class User(BaseClass):
    __tablename__ = 'users'

    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    password = db.Column(db.String(128), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

    places = db.relationship('Place', backref='owner', lazy=True)
    reviews = db.relationship('Review', backref='user', lazy=True)

    @validates('first_name')
    def validate_first_name(self, key, first_name):
        if first_name == "":
            raise ValueError("First_name must be not empty")
        return first_name

    @validates('last_name')
    def validate_last_name(self, key, last_name):
        if last_name == "":
            raise ValueError("Last_name must be not empty")
        return last_name

    @validates('email')
    def validate_email(self, key, email):
        if email == "":
            raise ValueError("Email must be not empty")
        try:
            validate_email(email, check_deliverability=False)
        except EmailNotValidError:
            raise ValueError("Invalid email format")
        return email

    def hash_password(self, password):
        """Hashes the password before storing it."""
        self.password = bcrypt.generate_password_hash(password).decode('utf-8')

    def verify_password(self, password):
        """Verifies if the provided password matches the hashed password."""
        return bcrypt.check_password_hash(self.password, password)

