"""
Standalone script to test local table creation against DATABASE_URL.

Usage:
    python init_db.py            # create all tables (safe if they exist)
    python init_db.py --drop     # drop everything first, then recreate
    python init_db.py --seed     # create tables + insert one sample row per table

This does NOT run in production — it's a dev convenience. Real deployments
should use migrations (see the Alembic/Flask-Migrate note in README setup
instructions) once the schema is stable enough that hand-dropping tables is
no longer acceptable.
"""
import argparse
import sys

from app import create_app
from app.extensions import db
from app.models import User, Place, SavedList, ListItem, Review, ReviewUpvote


def main():
    parser = argparse.ArgumentParser(description="Initialize the Loop database.")
    parser.add_argument("--drop", action="store_true", help="Drop all tables first.")
    parser.add_argument("--seed", action="store_true", help="Insert one sample row per table.")
    args = parser.parse_args()

    app = create_app()

    with app.app_context():
        print(f"Connecting to: {app.config['SQLALCHEMY_DATABASE_URI']}")

        if args.drop:
            confirm = input("This will DROP ALL TABLES. Type 'yes' to continue: ")
            if confirm.strip().lower() != "yes":
                print("Aborted.")
                sys.exit(0)
            db.drop_all()
            print("Dropped all tables.")

        db.create_all()
        print("Created tables:", ", ".join(db.metadata.tables.keys()))

        if args.seed:
            _seed()
            print("Inserted sample rows.")


def _seed():
    from app.extensions import bcrypt

    user = User(
        email="test@example.com",
        password_hash=bcrypt.generate_password_hash("password123").decode("utf-8"),
    )
    place = Place(
        google_place_id="ChIJ_test_place_id",
        name="Test Coffee Shop",
        category="cafe",
        address="123 University Ave, Gainesville, FL",
        latitude=29.6516,
        longitude=-82.3248,
    )
    db.session.add_all([user, place])
    db.session.flush()  # get generated IDs without a full commit yet

    saved_list = SavedList(user_id=user.id, title="My Coffee Crawl", is_private=True)
    db.session.add(saved_list)
    db.session.flush()

    db.session.add(ListItem(list_id=saved_list.id, place_id=place.id))
    db.session.add(Review(user_id=user.id, place_id=place.id, rating=5, comment="Great espresso."))
    db.session.commit()


if __name__ == "__main__":
    main()
