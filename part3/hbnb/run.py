from app import create_app, db
from app.services import facade

app = create_app()


def create_admin():
    admin = facade.get_user_by_email("admin@hbnb.com")

    if not admin:
        admin_data = {
            "email": "admin@hbnb.com",
            "first_name": "Admin",
            "last_name": "HBnB",
            "password": "admin/12345",
            "is_admin": True,
        }

        facade.create_user(admin_data)
        print("Admin user created")

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        create_admin()
    app.run(debug=True)
