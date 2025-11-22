import os

from flask import Flask, jsonify
from flask_migrate import Migrate
from flask_cors import CORS
from dotenv import load_dotenv
from flask import request
from .models import db, User, Category, Item

load_dotenv()


def create_app():

    app = Flask(__name__)

    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        database_url = "postgresql+psycopg2://localhost/medialog_dev"

    app.config["SQLALCHEMY_DATABASE_URI"] = database_url
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)
    Migrate(app, db)
    CORS(app)

    @app.route("/")
    def index():
        return jsonify({"message": "Medialog API is running"}), 200
    
    @app.post("/items")
    def create_item():

        data = request.get_json()

        required_fields = ["title", "user_id", "category_id"]
        missing = [field for field in required_fields if field not in data]

        if missing:
            return {"errors": [f"Missing field: {m}" for m in missing]}, 400
        
        user = User.query.get(data["user_id"])
        category = Category.query.get(data["category_id"])

        if not user:
            return {"errors": ["User does not exist"]}, 400
        if not category:
            return {"errors": ["Category does not exist"]}, 400
        
        new_item = Item(
            title=data["title"],
            user_id=data["user_id"],
            category_id=data["category_id"],
            image_url=data.get("image_url")
        )

        db.session.add(new_item)
        db.session.commit()

        return {
            "id": new_item.id,
            "title": new_item.title,
            "user_id": new_item.user_id,
            "category_id": new_item.category_id,
            "image_url": new_item.image_url,
        }, 201


    return app

app = create_app()