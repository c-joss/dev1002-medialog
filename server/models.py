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
    
class Item(db.Model):
    __tablename__ = "items"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey("categories.id"), nullable=False)

    image_url = db.Column(db.String(255))

    tags = db.relationship(
        "Tag",
        secondary="item_tags",
        back_populates="items"
    )

    creators = db.relationship(
        "Creator",
        secondary="item_creators",
        back_populates="items",
    )

    def __repr__(self):
        return f"<Item {self.title}>"
    
class Tag(db.Model):
    __tablename__ = "tags"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)

    items = db.relationship(
        "Item",
        secondary="item_tags",
        back_populates="tags"
    )

    def __repr__(self):
        return f"<Tag {self.name}>"
    
class ItemTag(db.Model):
    __tablename__ = "item_tags"

    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey("items.id"), nullable=False)
    tag_id = db.Column(db.Integer, db.ForeignKey("tags.id"), nullable=False)

    __table_args__ = (
        db.UniqueConstraint("item_id", "tag_id", name="uix_item_tag"),
    )

class Creator(db.Model):
    __tablename__ = "creators"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)

    items = db.relationship(
        "Item",
        secondary="item_creators",
        back_populates="creators",
    )

    def __repr__(self):
        return f"<Creator {self.name}>"
    
class ItemCreator(db.Model):
    __tablename__ = "item_creators"

    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey("items.id"), nullable=False)
    creator_id = db.Column(db.Integer, db.ForeignKey("creators.id"), nullable=False)

    __table_args__ = (
        db.UniqueConstraint("item_id", "creator_id", name="uix_item_creator"),
    )