from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False, unique=True)

    items = db.relationship("Item", backref="user", lazy=True)

    def __repr__(self):
        return f"<User {self.username}>"
    
class Category(db.Model):
    __tablename__ = "categories"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)

    items = db.relationship("Item", backref="category", lazy=True)

    def __repr__(self):
        return f"<Category {self.name}>"