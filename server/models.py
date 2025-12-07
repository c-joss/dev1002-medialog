from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# A user in the app. Each user can add many items.
class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    password = db.Column(db.String(30), nullable=False)

    # Link to items created by the user (1-to-many)
    items = db.relationship("Item", backref="user", lazy=True)

    def __repr__(self):
        return f"<User {self.username}>"
    
# A category for grouping items (e.g. Book, Game).    
class Category(db.Model):
    __tablename__ = "categories"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)

    # One category can have many items
    items = db.relationship("Item", backref="category", lazy=True)

    def __repr__(self):
        return f"<Category {self.name}>"
    
# The main item in a user’s collection.    
class Item(db.Model):
    __tablename__ = "items"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)

    # Every item belongs to a user and a category
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey("categories.id"), nullable=False)

    image_url = db.Column(db.String(255))

    # Many-to-many link between items and tags using a join table
    tags = db.relationship(
        "Tag",
        secondary="item_tags",
        back_populates="items"
    )

    # Many-to-many link between items and creators using a join table
    creators = db.relationship(
        "Creator",
        secondary="item_creators",
        back_populates="items",
    )

    def __repr__(self):
        return f"<Item {self.title}>"
    
# A tag that can be applied to many items (e.g. RPG, Fantasy).    
class Tag(db.Model):
    __tablename__ = "tags"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)

    # Reverse many-to-many link to items
    items = db.relationship(
        "Item",
        secondary="item_tags",
        back_populates="tags"
    )

    def __repr__(self):
        return f"<Tag {self.name}>"
    
# Join table that connects items and tags.
# This avoids repeating tag lists inside the item table.   
class ItemTag(db.Model):
    __tablename__ = "item_tags"

    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey("items.id"), nullable=False)
    tag_id = db.Column(db.Integer, db.ForeignKey("tags.id"), nullable=False)

    # Prevents duplicate (item, tag) pairs
    __table_args__ = (
        db.UniqueConstraint("item_id", "tag_id", name="uix_item_tag"),
    )

# A creator (e.g. author or game studio).
class Creator(db.Model):
    __tablename__ = "creators"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)

    # Items connected to this creator
    items = db.relationship(
        "Item",
        secondary="item_creators",
        back_populates="creators",
    )

    def __repr__(self):
        return f"<Creator {self.name}>"
    
# Join table for items and creators (same idea as ItemTag).    
class ItemCreator(db.Model):
    __tablename__ = "item_creators"

    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey("items.id"), nullable=False)
    creator_id = db.Column(db.Integer, db.ForeignKey("creators.id"), nullable=False)

    # Prevents duplicate (item, creator) pairs
    __table_args__ = (
        db.UniqueConstraint("item_id", "creator_id", name="uix_item_creator"),
    )

# A review left by a user on an item (rating + short text).
class Review(db.Model):

    __tablename__ = "reviews"

    id = db.Column(db.Integer, primary_key=True)

    rating = db.Column(db.Integer, nullable=True)
    text = db.Column(db.String(255), nullable=True)

    # Who wrote the review, and which item it belongs to
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey("items.id"), nullable=False)

    user = db.relationship("User", backref="reviews")
    item = db.relationship("Item", backref="reviews")

    def __repr__(self):
        return f"<Review user={self.user_id} item={self.item_id} rating={self.rating}>"