"""
PBI-01 — Database models (Flask-SQLAlchemy / PostgreSQL)
Owner: Maria

Five tables: User, Place, SavedList, ListItem, Review.
Relationships use cascade deletes where a child row is meaningless without
its parent (e.g. a SavedList's items disappear if the list is deleted), but
NOT for Place, which is shared reference data other rows point to.
"""
import uuid
from datetime import datetime, timezone

from .extensions import db


def _uuid() -> str:
    return str(uuid.uuid4())


def _now() -> datetime:
    return datetime.now(timezone.utc)


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.String(36), primary_key=True, default=_uuid)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=_now, nullable=False)

    saved_lists = db.relationship(
        "SavedList", back_populates="owner", cascade="all, delete-orphan"
    )
    reviews = db.relationship(
        "Review", back_populates="author", cascade="all, delete-orphan"
    )

    def to_public_dict(self) -> dict:
        """Never include password_hash — this is what auth responses send."""
        return {
            "id": self.id,
            "email": self.email,
            "created_at": self.created_at.isoformat(),
        }

    def __repr__(self) -> str:
        return f"<User {self.email}>"


class Place(db.Model):
    """
    Shared reference data. One row per real-world place, deduped on
    google_place_id so Isabella's Places proxy can upsert freely without
    creating duplicates every time a user views/saves/reviews a place.
    """
    __tablename__ = "places"

    id = db.Column(db.String(36), primary_key=True, default=_uuid)
    google_place_id = db.Column(db.String(255), unique=True, nullable=False, index=True)
    name = db.Column(db.String(255), nullable=False)
    category = db.Column(db.String(100), nullable=True)
    address = db.Column(db.String(500), nullable=True)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=_now, nullable=False)

    list_items = db.relationship(
        "ListItem", back_populates="place", cascade="all, delete-orphan"
    )
    reviews = db.relationship(
        "Review", back_populates="place", cascade="all, delete-orphan"
    )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "google_place_id": self.google_place_id,
            "name": self.name,
            "category": self.category,
            "address": self.address,
            "latitude": self.latitude,
            "longitude": self.longitude,
        }

    def __repr__(self) -> str:
        return f"<Place {self.name}>"


class SavedList(db.Model):
    """A user-created collection, e.g. 'Coffee crawl'. Public or private."""
    __tablename__ = "saved_lists"

    id = db.Column(db.String(36), primary_key=True, default=_uuid)
    user_id = db.Column(
        db.String(36), db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    title = db.Column(db.String(255), nullable=False)
    is_private = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=_now, nullable=False)

    owner = db.relationship("User", back_populates="saved_lists")
    items = db.relationship(
        "ListItem", back_populates="saved_list", cascade="all, delete-orphan"
    )

    def to_dict(self, include_items: bool = False) -> dict:
        data = {
            "id": self.id,
            "user_id": self.user_id,
            "title": self.title,
            "is_private": self.is_private,
            "created_at": self.created_at.isoformat(),
            "item_count": len(self.items),
        }
        if include_items:
            data["items"] = [item.to_dict() for item in self.items]
        return data

    def __repr__(self) -> str:
        return f"<SavedList {self.title}>"


class ListItem(db.Model):
    """A single place saved into a SavedList. One place can appear in many lists."""
    __tablename__ = "list_items"
    __table_args__ = (
        db.UniqueConstraint("list_id", "place_id", name="uq_list_place"),
    )

    id = db.Column(db.String(36), primary_key=True, default=_uuid)
    list_id = db.Column(
        db.String(36), db.ForeignKey("saved_lists.id", ondelete="CASCADE"), nullable=False, index=True
    )
    place_id = db.Column(
        db.String(36), db.ForeignKey("places.id", ondelete="CASCADE"), nullable=False, index=True
    )
    added_at = db.Column(db.DateTime(timezone=True), default=_now, nullable=False)

    saved_list = db.relationship("SavedList", back_populates="items")
    place = db.relationship("Place", back_populates="list_items")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "list_id": self.list_id,
            "added_at": self.added_at.isoformat(),
            "place": self.place.to_dict(),
        }

    def __repr__(self) -> str:
        return f"<ListItem list={self.list_id} place={self.place_id}>"


class Review(db.Model):
    """One review per (user, place) — enforced by the unique constraint below."""
    __tablename__ = "reviews"
    __table_args__ = (
        db.UniqueConstraint("user_id", "place_id", name="uq_user_place_review"),
        db.CheckConstraint("rating >= 1 AND rating <= 5", name="ck_rating_range"),
    )

    id = db.Column(db.String(36), primary_key=True, default=_uuid)
    user_id = db.Column(
        db.String(36), db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    place_id = db.Column(
        db.String(36), db.ForeignKey("places.id", ondelete="CASCADE"), nullable=False, index=True
    )
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime(timezone=True), default=_now, nullable=False)

    author = db.relationship("User", back_populates="reviews")
    place = db.relationship("Place", back_populates="reviews")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "place_id": self.place_id,
            "rating": self.rating,
            "comment": self.comment,
            "created_at": self.created_at.isoformat(),
            "author_email": self.author.email if self.author else None,
        }

    def __repr__(self) -> str:
        return f"<Review user={self.user_id} place={self.place_id} rating={self.rating}>"


class ReviewUpvote(db.Model):
    """
    NOT in the original 5-table spec — added because your deliverables list
    'upvoting endpoints' and an upvote has to be persisted *somewhere* to be
    idempotent (so one user can't upvote the same review 100 times). If your
    team decides upvotes should just be a counter column on Review instead,
    delete this model and add `upvote_count = db.Column(db.Integer, default=0)`
    to Review — but you lose per-user idempotency and the ability to "unvote."
    """
    __tablename__ = "review_upvotes"
    __table_args__ = (
        db.UniqueConstraint("user_id", "review_id", name="uq_user_review_upvote"),
    )

    id = db.Column(db.String(36), primary_key=True, default=_uuid)
    user_id = db.Column(
        db.String(36), db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    review_id = db.Column(
        db.String(36), db.ForeignKey("reviews.id", ondelete="CASCADE"), nullable=False, index=True
    )
    created_at = db.Column(db.DateTime(timezone=True), default=_now, nullable=False)

    def __repr__(self) -> str:
        return f"<ReviewUpvote user={self.user_id} review={self.review_id}>"
