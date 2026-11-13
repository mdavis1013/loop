"""
Reviews API: post, list, and upvote reviews of a place.

Endpoints (all under /api):
  GET  /places/<google_place_id>/reviews   -> 200 {reviews, review_count, average_rating}
  POST /places/<google_place_id>/reviews   -> 201 {review}   (login required)
  POST /reviews/<review_id>/upvote         -> 200 {upvote_count} (login required)
"""
from flask import Blueprint, jsonify, request
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError

from .auth import token_required
from .extensions import db
from .models import Place, Review, ReviewUpvote

reviews_bp = Blueprint("reviews", __name__)

MAX_COMMENT_LENGTH = 2000


def _error(message: str, status: int, code: str = "bad_request"):
    return jsonify({"error": code, "message": message}), status


def _is_number(value) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _upvote_counts(review_ids: list) -> dict:
    """{review_id: count} for the given reviews, in one query."""
    if not review_ids:
        return {}
    rows = (
        db.session.query(ReviewUpvote.review_id, func.count(ReviewUpvote.id))
        .filter(ReviewUpvote.review_id.in_(review_ids))
        .group_by(ReviewUpvote.review_id)
        .all()
    )
    return dict(rows)


def _review_dict(review: Review, upvote_count: int = 0) -> dict:
    # Public shape: never expose the full email, only the part before the "@".
    return {
        "id": review.id,
        "rating": review.rating,
        "comment": review.comment,
        "author_name": review.author.email.split("@")[0],
        "upvote_count": upvote_count,
        "created_at": review.created_at.isoformat(),
    }


def _place_from_payload(google_place_id: str, info):
    """Builds a Place from the request's "place" field, or None if it's incomplete."""
    if not isinstance(info, dict):
        return None
    name = info.get("name")
    location = info.get("location")
    if not isinstance(name, str) or not name.strip() or not isinstance(location, dict):
        return None
    lat, lng = location.get("lat"), location.get("lng")
    if not _is_number(lat) or not _is_number(lng):
        return None
    return Place(
        google_place_id=google_place_id,
        name=name.strip(),
        address=info.get("address"),
        latitude=lat,
        longitude=lng,
    )


@reviews_bp.get("/places/<google_place_id>/reviews")
def list_reviews(google_place_id):
    place = Place.query.filter_by(google_place_id=google_place_id).first()
    if place is None:
        return jsonify({"reviews": [], "review_count": 0, "average_rating": None}), 200

    reviews = (
        Review.query.filter_by(place_id=place.id)
        .order_by(Review.created_at.desc())
        .all()
    )
    counts = _upvote_counts([r.id for r in reviews])
    average = round(sum(r.rating for r in reviews) / len(reviews), 1) if reviews else None
    return jsonify({
        "reviews": [_review_dict(r, counts.get(r.id, 0)) for r in reviews],
        "review_count": len(reviews),
        "average_rating": average,
    }), 200


@reviews_bp.post("/places/<google_place_id>/reviews")
@token_required
def create_review(google_place_id):
    data = request.get_json(silent=True) or {}
    rating = data.get("rating")
    comment = data.get("comment")

    if isinstance(rating, bool) or not isinstance(rating, int) or not 1 <= rating <= 5:
        return _error("Rating must be a whole number from 1 to 5.", 400, "invalid_rating")

    if comment is not None:
        if not isinstance(comment, str):
            return _error("Comment must be text.", 400, "invalid_comment")
        comment = comment.strip() or None
        if comment and len(comment) > MAX_COMMENT_LENGTH:
            return _error(
                f"Comment must be at most {MAX_COMMENT_LENGTH} characters.", 400, "invalid_comment"
            )

    place = Place.query.filter_by(google_place_id=google_place_id).first()
    if place is None:
        place = _place_from_payload(google_place_id, data.get("place"))
        if place is None:
            return _error(
                "Place details (name and location) are required the first time a place is reviewed.",
                400,
                "place_required",
            )
        db.session.add(place)
        db.session.flush()  # assigns place.id before the review needs it

    user = request.current_user
    review = Review(user_id=user.id, place_id=place.id, rating=rating, comment=comment)
    db.session.add(review)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return _error("You have already reviewed this place.", 409, "already_reviewed")

    return jsonify({"review": _review_dict(review)}), 201


@reviews_bp.post("/reviews/<review_id>/upvote")
@token_required
def upvote_review(review_id):
    review = db.session.get(Review, review_id)
    if review is None:
        return _error("Review not found.", 404, "not_found")

    user = request.current_user
    if review.user_id == user.id:
        return _error("You can't upvote your own review.", 400, "own_review")

    db.session.add(ReviewUpvote(user_id=user.id, review_id=review.id))
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return _error("You have already upvoted this review.", 409, "already_upvoted")

    count = _upvote_counts([review.id]).get(review.id, 0)
    return jsonify({"upvote_count": count}), 200