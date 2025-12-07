from server.app import app
from server.models import db

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        print("Database tables created.")
