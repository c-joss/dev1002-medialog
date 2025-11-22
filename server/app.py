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
    
    @app.get("/items")
    def list_items():

        items = Item.query.all()

        results = []
        for item in items:
            results.append({
                "id": item.id,
                "title": item.title,
                "user_id": item.user_id,
                "category_id": item.category_id,
                "image_url": item.image_url,
            })

        return jsonify(results), 200
    
    @app.get("/items/<int:item_id>")
    def get_item(item_id):

        item = Item.query.get(item_id)

        if not item:
            return {"errors": [f"Item with id {item_id} not found"]}, 404
        
        return {
            "id": item.id,
            "title": item.title,
            "user_id": item.user_id,
            "category_id": item.category_id,
            "image_url": item.image_url,
        }, 200
    
    @app.patch("/items/<int:item_id>")
    def update_item(item_id):

        item = Item.query.get(item_id)

        if not item:
            return {"errors": [f"Item with id {item_id} not found"]}, 404
        
        data = request.get_json() or {}

        if not data:
            return {"errors": ["No data provided to update"]}, 400
        
        if "title" in data:
            if not data["title"]:
                return {"errors": ["Title cannot be empty"]}, 400
            item.title = data["title"]

        if "category_id" in data:
            category = Category.query.get(data["category_id"])
            if not category:
                return {"errors": ["Category does not exist"]}, 400
            item.category_id = data["category_id"]

        if "image_url" in data:
            item.image_url = data["image_url"]

        db.session.commit()

        return {
            "id": item.id,
            "title": item.title,
            "user_id": item.user_id,
            "category_id": item.category_id,
            "image_url": item.image_url,
        }, 200
    
    @app.delete("/items/<int:item_id>")
    def delete_item(item_id):

        item = Item.query.get(item_id)

        if not item:
            return {"errors": [f"Item with id {item_id} not found"]}, 404
        
        db.session.delete(item)
        db.session.commit()

        return {"message": f"Item {item_id} deleted successfully"}, 200



    return app

app = create_app()