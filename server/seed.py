from .app import app
from .models import (
    db,
    User,
    Category,
    Item,
    Tag,
    Creator,
    Review,
    ItemTag,
    ItemCreator,
)

def run_seed():
    with app.app_context():
        print("Clearing existing data...")

        ItemTag.query.delete()
        ItemCreator.query.delete()

        Review.query.delete()

        Item.query.delete()
        Category.query.delete()
        Tag.query.delete()
        Creator.query.delete()
        User.query.delete()

        print("Creating seed data...")

        jack = User(
            username="jack",
            first_name="Jack",
            last_name="Sparrow",
            email="jack@example.com",
            password="password123",
        )

        guest = User(
            username="guest",
            first_name="Guest",
            last_name="User",
            email="guest@example.com",
            password="guestpassword",
        )

        game_cat = Category(name="Game")
        book_cat = Category(name="Book")

        witcher = Item(
            title="The Witcher 3",
            user=jack,
            category=game_cat,
            image_url="https://example.com/witcher3.jpg",
        )

        wheel = Item(
            title="The Wheel of Time",
            user=jack,
            category=book_cat,
            image_url="https://example.com/wheel-of-time.jpg",
        )

        rpg = Tag(name="RPG")
        fantasy = Tag(name="Fantasy")
        classic = Tag(name="Classic")
        adventure = Tag(name="Adventure")

        cdpr = Creator(name="CD Projekt Red")
        jordan = Creator(name="Robert Jordan")

        witcher.tags = [rpg, fantasy]
        wheel.tags = [fantasy, classic, adventure]

        witcher.creators = [cdpr]
        wheel.creators = [jordan]

        review1 = Review(
            rating=5,
            text="Amazing story and visuals.",
            user=jack,
            item=witcher,
        )

        review2 = Review(
            rating=5,
            text="Epic world-building and unforgettable characters.",
            user=jack,
            item=wheel,
        )

        db.session.add_all([
            jack,
            guest,
            game_cat,
            book_cat,
            witcher,
            wheel,
            rpg,
            fantasy,
            classic,
            adventure,
            cdpr,
            jordan,
            review1,
            review2,
        ])

        db.session.commit()


if __name__ == "__main__":
    run_seed()