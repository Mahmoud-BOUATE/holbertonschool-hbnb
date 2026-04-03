from app.models.Base_Class import BaseClass
from email_validator import validate_email, EmailNotValidError

class User(BaseClass):
	def __init__(self, email, first_name, last_name, password, user_id, is_admin=False):
		super().__init__()
		self.email = email
		self.first_name = first_name
		self.last_name = last_name
		self.password = password
		self.is_admin = is_admin
		self.user_id = user_id
		self.places = []
		self.reviews = []

	@property
	def first_name(self):
		return self._first_name
	@first_name.setter
	def first_name(self, value):
		self._first_name = self.validate_first_name(value)
	@property
	def last_name(self):
		return self._last_name
	@last_name.setter
	def last_name(self, value):
		self._last_name = self.validate_last_name(value)
	@property
	def email(self):
		return self._email
	@email.setter
	def email(self, value):
		self._email = self.validate_email(value)
	@property
	def password(self):
		return self.__password
	@password.setter
	def password(self, value):
		self.__password = self.validate_password(value)

	def validate_first_name(self, first_name):
		try:
			if first_name == "":
				raise ValueError("First_name should be not empty")
			return first_name
		except ValueError:
			raise ValueError("First_name must be not empty")

	def validate_last_name(self, last_name):
		try:
			if last_name == "":
				raise ValueError("Last_name should be not empty")
			return last_name
		except ValueError:
			raise ValueError("Last_name must be not empty")

	def validate_email(self, email):
		if email == "":
			raise ValueError("Email should be not empty")
		try:
			validate_email(email, check_deliverability=False)
		except EmailNotValidError:
			raise ValueError("Invalid email format")
		return email

	def validate_password(self, password):
		if password == "":
			raise ValueError("Password should be not empty")
		if len(password) < 8:
			raise ValueError("Password must be at least 8 characters long")
		return password



