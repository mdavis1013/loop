"""
Tests for the reviews API: post, list, and upvote.

Run from the backend/ folder with the venv active:
    python -m pytest -v tests/test_reviews.py

Uses the SEPARATE test database (never the shared Supabase one).
"""
import os

# Must be set BEFORE the app is created so the engine binds to the test DB.
os.environ["DATABASE_URL"] = os.environ.get(
    "TEST_DATABASE_URL", "postgresql+psycopg2://loop_user@localhost:5432/loop_test"
)

import pytest

from app import create_app
from app.extensions import db
from app.models import Place, Review

PASSWORD = "Pass1234!"
PLACE = {
    "name": "Test Cafe",
    "address": "1 Main St",
    "location": {"lat": 29.65, "lng": -82.32},
}


@pytest.fixture(scope="module")
def app():
    app = create_app()
    app.config["TESTING"] = True

    # Safety net: refuse to wipe anything that isn't clearly a test database.
    uri = str(app.config["SQLALCHEMY_DATABASE_URI"])
    assert "test" in uri, f"Refusing to run tests against non-test DB: {uri}"
    return app


@pytest.fixture()
def client(app):
    with app.app_context():
        db.drop_all()
        db.create_all()
        yield app.test_client()
        db.session.remove()
        db.drop_all()


# ----------------------------------------------------------------- helpers

def signup(client, email="maria@test.com"):
    res = client.post("/api/auth/register", json={"email": email, "password": PASSWORD})
    return res.get_json()["token"]


def auth(token):
    return {"Authorization": f"Bearer {token}"}


def post_review(client, token, rating=5, comment="Great spot", gid="place-1", place=PLACE):
    body = {"rating": rating}
    if comment is not None:
        body["comment"] = comment
    if place is not None:
        body["place"] = place
    return client.post(f"/api/places/{gid}/reviews", json=body, headers=auth(token))


# ------------------------------------------------------------- post review

def test_post_review_requires_login(client):
    res = client.post("/api/places/place-1/reviews", json={"rating": 5, "place": PLACE})
    assert res.status_code == 401
    assert res.get_json()["error"] == "unauthorized"


def test_post_review_success_creates_place_and_review(client):
    res = post_review(client, signup(client))
    assert res.status_code == 201
    review = res.get_json()["review"]
    assert review["rating"] == 5
    assert review["comment"] == "Great spot"
    assert review["upvote_count"] == 0
    assert Place.query.filter_by(google_place_id="place-1").count() == 1
    assert Review.query.count() == 1


def test_post_review_does_not_expose_email(client):
    review = post_review(client, signup(client)).get_json()["review"]
    assert review["author_name"] == "maria"
    assert "@" not in str(review)


def test_post_review_comment_is_optional(client):
    res = post_review(client, signup(client), comment=None)
    assert res.status_code == 201
    assert res.get_json()["review"]["comment"] is None


def test_post_review_comment_too_long_returns_400(client):
    res = post_review(client, signup(client), comment="x" * 2001)
    assert res.status_code == 400
    assert res.get_json()["error"] == "invalid_comment"


@pytest.mark.parametrize("bad_rating", [0, 6, -1, 4.5, "5", None, True])
def test_post_review_invalid_rating_returns_400(client, bad_rating):
    res = client.post(
        "/api/places/place-1/reviews",
        json={"rating": bad_rating, "place": PLACE},
        headers=auth(signup(client)),
    )
    assert res.status_code == 400
    assert res.get_json()["error"] == "invalid_rating"


def test_post_review_new_place_without_details_returns_400(client):
    res = post_review(client, signup(client), place=None)
    assert res.status_code == 400
    assert res.get_json()["error"] == "place_required"
    assert Place.query.count() == 0


def test_post_review_new_place_with_missing_location_returns_400(client):
    res = post_review(client, signup(client), place={"name": "Test Cafe"})
    assert res.status_code == 400
    assert res.get_json()["error"] == "place_required"


def test_post_review_duplicate_returns_409(client):
    token = signup(client)
    post_review(client, token)
    res = post_review(client, token, rating=4)
    assert res.status_code == 409
    assert res.get_json()["error"] == "already_reviewed"
    assert Review.query.count() == 1


def test_second_user_reuses_existing_place_without_details(client):
    post_review(client, signup(client, "maria@test.com"))
    res = post_review(client, signup(client, "sam@test.com"), place=None)
    assert res.status_code == 201
    assert Place.query.count() == 1


# ------------------------------------------------------------ list reviews

def test_list_reviews_for_unknown_place_is_empty(client):
    res = client.get("/api/places/nope/reviews")
    assert res.status_code == 200
    body = res.get_json()
    assert body["reviews"] == []
    assert body["review_count"] == 0
    assert body["average_rating"] is None


def test_list_reviews_returns_count_and_average(client):
    post_review(client, signup(client, "maria@test.com"), rating=5)
    post_review(client, signup(client, "sam@test.com"), rating=4)
    body = client.get("/api/places/place-1/reviews").get_json()
    assert body["review_count"] == 2
    assert body["average_rating"] == 4.5
    assert len(body["reviews"]) == 2


def test_list_reviews_only_includes_that_place(client):
    token = signup(client)
    post_review(client, token, gid="place-1")
    post_review(client, token, gid="place-2")
    body = client.get("/api/places/place-1/reviews").get_json()
    assert body["review_count"] == 1


# ------------------------------------------------------------------ upvote

def test_upvote_requires_login(client):
    res = client.post("/api/reviews/some-id/upvote")
    assert res.status_code == 401


def test_upvote_unknown_review_returns_404(client):
    res = client.post("/api/reviews/does-not-exist/upvote", headers=auth(signup(client)))
    assert res.status_code == 404
    assert res.get_json()["error"] == "not_found"


def test_upvote_success_and_shows_in_list(client):
    review_id = post_review(client, signup(client, "maria@test.com")).get_json()["review"]["id"]
    voter = signup(client, "sam@test.com")

    res = client.post(f"/api/reviews/{review_id}/upvote", headers=auth(voter))
    assert res.status_code == 200
    assert res.get_json()["upvote_count"] == 1

    listed = client.get("/api/places/place-1/reviews").get_json()["reviews"][0]
    assert listed["upvote_count"] == 1


def test_upvote_twice_returns_409(client):
    review_id = post_review(client, signup(client, "maria@test.com")).get_json()["review"]["id"]
    voter = signup(client, "sam@test.com")
    client.post(f"/api/reviews/{review_id}/upvote", headers=auth(voter))

    res = client.post(f"/api/reviews/{review_id}/upvote", headers=auth(voter))
    assert res.status_code == 409
    assert res.get_json()["error"] == "already_upvoted"


def test_upvote_own_review_returns_400(client):
    author = signup(client)
    review_id = post_review(client, author).get_json()["review"]["id"]
    res = client.post(f"/api/reviews/{review_id}/upvote", headers=auth(author))
    assert res.status_code == 400
    assert res.get_json()["error"] == "own_review"