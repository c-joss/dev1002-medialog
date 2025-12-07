import os

from .config import Config
from flask import Flask, jsonify
from flask_migrate import Migrate
from flask_cors import CORS
from dotenv import load_dotenv
from flask import request, jsonify
from .models import (
    db,
    User,
    Category,
    Item,
    Tag,
    Creator,
    Review,
)
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.exceptions import BadRequest


load_dotenv()

# Helpers for handling requests
# -----------------------------

# Reads request JSON safely and returns helpful errors
def get_json_or_error():
    try:
        data = request.get_json() or {}
    except BadRequest:
        return None, ({"errors": ["Invalid JSON body"]}, 400)

    if not isinstance(data, dict):
        return None, ({"errors": ["JSON body must be an object"]}, 400)

    return data, None

# Checks required fields are present (e.g. username, title)
def require_fields(data, required_fields):
    missing = []
    for field in required_fields:
        value = data.get(field)
        if value is None:
            missing.append(field)
        elif isinstance(value, str) and not value.strip():
            missing.append(field)

    if missing:
        return (
            {
                "errors": [
                    f"Missing or empty field: {name}"
                    for name in missing
                ]
            },
            400,
        )

    return None

# Commits changes to the database and handles unexpected DB errors
def commit_session():
    try:
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        return ({"errors": ["Unexpected server error while saving data"]}, 500)

    return None

# Validates IDs are positive integers
def require_positive_int(name, raw_value):
    try:
        value = int(raw_value)
    except (TypeError, ValueError):
        return None, ({"errors": [f"{name} must be an integer"]}, 400)

    if value <= 0:
        return None, ({"errors": [f"{name} must be a positive integer"]}, 400)

    return value, None

# Validates optional rating is between 1–5
def parse_optional_rating(raw_rating):
    if raw_rating is None:
        return None, None

    try:
        rating_value = int(raw_rating)
    except (TypeError, ValueError):
        return None, ({"errors": ["Rating must be an integer between 1 and 5"]}, 400)

    if rating_value < 1 or rating_value > 5:
        return None, ({"errors": ["Rating must be between 1 and 5"]}, 400)

    return rating_value, None

# Converters to shape response JSON
# -----------------------------

# Turns a Review into a simple dictionary sent back to the client
def review_to_dict(review):
    return {
        "id": review.id,
        "rating": review.rating,
        "text": review.text,
        "user_id": review.user_id,
        "item_id": review.item_id,
    }

def user_to_dict(user):
    return {
        "id": user.id,
        "username": user.username,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "email": user.email,
    }

def item_to_dict(item):
    return {
        "id": item.id,
        "title": item.title,
        "user_id": item.user_id,
        "category_id": item.category_id,
        "image_url": item.image_url,
        "tags": [t.name for t in item.tags],
        "creators": [c.name for c in item.creators],
    }

def create_app():

    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    Migrate(app, db)
    CORS(app)

    # Health check route
    # -----------------------------
    @app.route("/")
    def index():
        return jsonify({"message": "Medialog API is running"}), 200
    
    # User Routes (create, list, get user, basic login)
    # ----------------------------------------------------    
    @app.post("/users")
    def create_user():
        data, error = get_json_or_error()
        if error:
            return error

        error = require_fields(
            data,
            ["username", "first_name", "last_name", "email", "password"],
        )
        if error:
            return error

        username = data["username"].strip()
        email = data["email"].strip()

        existing_username = User.query.filter_by(username=username).first()
        if existing_username:
            return {"errors": ["Username already taken"]}, 400

        existing_email = User.query.filter_by(email=email).first()
        if existing_email:
            return {"errors": ["Email already in use"]}, 400

        user = User(
            username=username,
            first_name=data["first_name"].strip(),
            last_name=data["last_name"].strip(),
            email=email,
            password=data["password"],
        )
        
        db.session.add(user)
        error = commit_session()
        if error:
            return error

        return user_to_dict(user), 201
    
    
    @app.get("/users")
    def list_users():
        users = User.query.all()
        return jsonify([user_to_dict(u) for u in users]), 200
    
    
    @app.get("/users/<int:user_id>")
    def get_user(user_id):
        user = User.query.get(user_id)
        if not user:
            return {"errors": [f"User with id {user_id} not found"]}, 404

        return user_to_dict(user), 200
    

    @app.post("/login")
    def login():
        data, error = get_json_or_error()
        if error:
            return error

        error = require_fields(data, ["email", "password"])
        if error:
            return error

        email = data["email"].strip()
        password = data["password"]

        user = User.query.filter_by(email=email).first()
        if not user or user.password != password:
            return {"errors": ["Invalid email or password"]}, 401

        return {
            "message": "Login successful",
            "user": {
                "id": user.id,
                "username": user.username,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "email": user.email,
            },
        }, 200
    
    # Item Routes (full CRUD on the main entity)
    # ----------------------------------------------------    
    @app.post("/items")
    def create_item():

        data = request.get_json() or {}

        required_fields = ["title", "user_id", "category_id"]
        missing = [field for field in required_fields if field not in data]

        if missing:
            return {"errors": [f"Missing field: {m}" for m in missing]}, 400
        
        if not data.get("title"):
            return {"errors": ["Title is required"]}, 400
        
        title = data["title"].strip()
        if not title:
            return {"errors": ["Title is required"]}, 400

        user_id, error = require_positive_int("user_id", data["user_id"])
        if error:
            return error

        category_id, error = require_positive_int("category_id", data["category_id"])
        if error:
            return error
        
        user = User.query.get(user_id)
        category = Category.query.get(category_id)

        if not user:
            return {"errors": ["User does not exist"]}, 400
        if not category:
            return {"errors": ["Category does not exist"]}, 400
        
        new_item = Item(
            title=title,
            user_id=user.id,
            category_id=category.id,
            image_url=data.get("image_url"),
        )

        db.session.add(new_item)
        error = commit_session()
        if error:
            return error

        return item_to_dict(new_item), 201
    
    
    @app.get("/items")
    def list_items():

        items = Item.query.all()

        return jsonify([item_to_dict(item) for item in items]), 200
    
    
    @app.get("/items/<int:item_id>")
    def get_item(item_id):

        item = Item.query.get(item_id)

        if not item:
            return {"errors": [f"Item with id {item_id} not found"]}, 404
        
        return item_to_dict(item), 200
    
    
    @app.patch("/items/<int:item_id>")
    def update_item(item_id):

        item = Item.query.get(item_id)

        if not item:
            return {"errors": [f"Item with id {item_id} not found"]}, 404
        
        data = request.get_json() or {}

        if not data:
            return {"errors": ["No data provided to update"]}, 400
        
        if "title" in data:
            title = (data["title"] or "").strip()
            if not title:
                return {"errors": ["Title cannot be empty"]}, 400
            item.title = title

        if "category_id" in data:
            category_id, error = require_positive_int("category_id", data["category_id"])
            if error:
                return error
            
            category = Category.query.get(category_id)
            if not category:
                return {"errors": ["Category does not exist"]}, 400
            item.category_id = category_id

        if "image_url" in data:
            item.image_url = data["image_url"]

        error = commit_session()
        if error:
            return error

        return item_to_dict(item), 200
    
    
    @app.delete("/items/<int:item_id>")
    def delete_item(item_id):

        item = Item.query.get(item_id)

        if not item:
            return {"errors": [f"Item with id {item_id} not found"]}, 404
        
        # Remove related reviews + links to tags/creators before deleting the item        
        for review in list(item.reviews):
            db.session.delete(review)

        item.tags.clear()
        item.creators.clear()
        
        db.session.delete(item)
        error = commit_session()
        if error:
            return error

        return {"message": f"Item {item_id} deleted successfully"}, 200
    
    # Review Routes (create, list, list by item)
    # ----------------------------------------------------    
    @app.post("/reviews")
    def create_review():

        data, error = get_json_or_error()
        if error:
            return error
        
        required = ["user_id", "item_id"]
        missing = [field for field in required if field not in data]
        if missing:
            return {"errors": [f"Missing field: {m}" for m in missing]}, 400

        user_id, error = require_positive_int("user_id", data["user_id"])
        if error:
            return error

        item_id, error = require_positive_int("item_id", data["item_id"])
        if error:
            return error        
        
        rating_value, error = parse_optional_rating(data.get("rating"))
        if error:
            return error
        
        user = User.query.get(user_id)
        if not user:
            return {"errors": ["User does not exist"]}, 400
        
        item = Item.query.get(item_id)
        if not item:
            return {"errors": ["Item does not exist"]}, 400
        
        review = Review(
            rating=rating_value,
            text=data.get("text"),
            user_id=user.id,
            item_id=item.id,
        )

        db.session.add(review)
        error = commit_session()
        if error:
            return error

        return review_to_dict(review), 201
    
    
    @app.get("/reviews")
    def list_reviews():

        reviews = Review.query.all()
        return jsonify([review_to_dict(r) for r in reviews]), 200
    
    
    @app.get("/items/<int:item_id>/reviews")
    def list_item_reviews(item_id):

        item = Item.query.get(item_id)
        if not item:
            return {"errors": [f"Item with id {item_id} not found"]}, 404
        
        reviews = Review.query.filter_by(item_id=item_id).all()
        return jsonify([review_to_dict(r) for r in reviews]), 200
    
    # Tag Routes (list, create, assign to item)
    # ----------------------------------------------------    
    @app.get("/tags")
    def list_tags():

        tags = Tag.query.all()

        results = []
        for tag in tags:
            results.append({
                "id": tag.id,
                "name": tag.name,
            })

        return jsonify(results), 200
    
    
    @app.post("/tags")
    def create_tag():
        data, error = get_json_or_error()
        if error:
            return error
        
        error = require_fields(data, ["name"])
        if error:
            return error

        name = data["name"].strip()
        existing = Tag.query.filter_by(name=name).first()
        if existing:
            return {"errors": ["Tag with this name already exists"]}, 400
    
        tag = Tag(name=name)
        db.session.add(tag)
        error = commit_session()
        if error:
            return error

        return {"id": tag.id, "name": tag.name}, 201
    
    
    @app.post("/items/<int:item_id>/tags")
    def set_item_tags(item_id):

        item = Item.query.get(item_id)
        if not item:
            return {"errors": [f"Item with id {item_id} not found"]},404
        
        data, error = get_json_or_error()
        if error:
            return error

        tag_ids = data.get("tag_ids")

        if not isinstance(tag_ids, list) or not tag_ids:
            return {"errors": ["tag_ids must be a non-empty list"]}, 400
        
        tags = Tag.query.filter(Tag.id.in_(tag_ids)).all()

        if len(tags) != len(tag_ids):
            return {"errors": ["One or more tag_ids do not exist"]}, 400
        
        item.tags = tags
        error = commit_session()
        if error:
            return error

        return item_to_dict(item), 200
    
    # Creator Routes (list, create, assign to item)
    # ----------------------------------------------------    
    @app.get("/creators")
    def list_creators():

        creators = Creator.query.all()

        results = []
        for creator in creators:
            results.append({
                "id": creator.id,
                "name": creator.name,
            })

        return jsonify(results), 200
    
    
    @app.post("/creators")
    def create_creator():

        data, error = get_json_or_error()
        if error:
            return error
        
        error = require_fields(data, ["name"])
        if error:
            return error

        name = data["name"].strip()
        existing = Creator.query.filter_by(name=name).first()
        if existing:
            return {"errors": ["Creator with this name already exists"]}, 400
        
        creator = Creator(name=name)
        db.session.add(creator)
        error = commit_session()
        if error:
            return error

        return {"id": creator.id, "name": creator.name}, 201
    
    
    @app.post("/items/<int:item_id>/creators")
    def set_item_creators(item_id):

        item = Item.query.get(item_id)
        if not item:
            return {"errors": [f"Item with id {item_id} not found"]}, 404
        
        data, error = get_json_or_error()
        if error:
            return error
        
        creator_ids = data.get("creator_ids")

        if not isinstance(creator_ids, list) or not creator_ids:
            return {"errors": ["creator_ids must be a non-empty list"]}, 400
        
        creators = Creator.query.filter(Creator.id.in_(creator_ids)).all()

        if len(creators) != len(creator_ids):
            return {"errors": ["One or more creator_ids do not exist"]}, 400
        
        item.creators = creators
        error = commit_session()
        if error:
            return error

        return item_to_dict(item), 200
    
    # Simple JSON error responses
    # -----------------------------   
    @app.errorhandler(404)
    def handle_not_found(error):
        return {"errors": ["Endpoint not found"]}, 404

    @app.errorhandler(500)
    def handle_server_error(error):
        return {"errors": ["Internal server error"]}, 500
 
    return app

app = create_app()