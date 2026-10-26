"""
Tests for PBI-02 (auth API) and PBI-01 (User model basics).

Run from the backend/ folder with the venv active:
    createdb -U loop_user loop_test      # one time
    pip install pytest                   # one time
    pytest -v

These tests use a SEPARATE database (loop_test). They drop and recreate its
tables for every test, so never point them at loop_dev.
"""
import os
from datetime import datetime, timedelta, timezone

# Must be set BEFORE the app is created so the engine binds to the test DB.
os.environ["DATABASE_URL"] = os.environ.get(
    "TEST_DATABASE_URL", "postgresql+psycopg2://loop_user@localhost:5432/loop_test"
)

import jwt
import pytest
from flask import request

from app import create_app
from app.extensions import db
from app.auth import token_required, roles_required
from app.models import User, ROLE_BUSINESS_OWNER


@pytest.fixture(scope="module")
def app():
    app = create_app()
    app.config["TESTING"] = True

    # Safety net: refuse to wipe anything that isn't clearly a test database.
    uri = str(app.config["SQLALCHEMY_DATABASE_URI"])
    assert "test" in uri, f"Refusing to run tests against non-test DB: {uri}"

    # Temporary protected route, only exists inside the tests.
    @app.get("/api/_whoami")
    @token_required
    def whoami():
        return {"email": request.current_user.email}
    
    @app.get("/api/_owner_only")
    @token_required
    @roles_required(ROLE_BUSINESS_OWNER)
    def owner_only():
        return {"ok": True}

    return app



@pytest.fixture()
def client(app):
    with app.app_context():
        db.drop_all()
        db.create_all()
        yield app.test_client()
        db.session.remove()
        db.drop_all()


EMAIL = "maria@test.com"
PASSWORD = "Pass1234!"


def register(client, email=EMAIL, password=PASSWORD):
    return client.post("/api/auth/register", json={"email": email, "password": password})


def login(client, email=EMAIL, password=PASSWORD):
    return client.post("/api/auth/login", json={"email": email, "password": password})


# ---------------------------------------------------------------- register

def test_register_success(client):
    res = register(client)
    assert res.status_code == 201
    body = res.get_json()
    assert body["token"]
    assert body["user"]["email"] == EMAIL
    assert "password_hash" not in body["user"]


def test_register_normalizes_email(client):
    res = register(client, email="  Maria@Test.COM ")
    assert res.status_code == 201
    assert res.get_json()["user"]["email"] == "maria@test.com"


def test_register_stores_bcrypt_hash_not_plaintext(client):
    register(client)
    user = User.query.filter_by(email=EMAIL).first()
    assert user.password_hash != PASSWORD
    assert user.password_hash.startswith("$2")  # bcrypt prefix


def test_register_duplicate_email_returns_409(client):
    register(client)
    res = register(client)
    assert res.status_code == 409
    assert res.get_json()["error"] == "email_taken"


@pytest.mark.parametrize("bad_email", ["", "nope", "a@b", "@test.com"])
def test_register_invalid_email_returns_400(client, bad_email):
    res = register(client, email=bad_email)
    assert res.status_code == 400
    assert res.get_json()["error"] == "invalid_email"


def test_register_weak_password_returns_400(client):
    res = register(client, password="short")
    assert res.status_code == 400
    assert res.get_json()["error"] == "weak_password"


def test_register_missing_body_returns_400(client):
    res = client.post("/api/auth/register")
    assert res.status_code == 400


# ------------------------------------------------------------------- login

def test_login_success(client):
    register(client)
    res = login(client)
    assert res.status_code == 200
    assert res.get_json()["token"]


def test_login_wrong_password_returns_401(client):
    register(client)
    res = login(client, password="wrongpass")
    assert res.status_code == 401
    assert res.get_json()["error"] == "invalid_credentials"


def test_login_unknown_email_same_error_as_wrong_password(client):
    register(client)
    wrong_pw = login(client, password="wrongpass")
    no_user = login(client, email="nobody@test.com")
    assert no_user.status_code == 401
    # Same response either way, so emails can't be enumerated.
    assert no_user.get_json() == wrong_pw.get_json()


# ---------------------------------------------------------- token_required

def test_protected_route_without_token_returns_401(client):
    res = client.get("/api/_whoami")
    assert res.status_code == 401
    assert res.get_json()["error"] == "unauthorized"


def test_protected_route_with_garbage_token_returns_401(client):
    res = client.get("/api/_whoami", headers={"Authorization": "Bearer garbage"})
    assert res.status_code == 401
    assert res.get_json()["error"] == "invalid_token"


def test_protected_route_with_wrong_scheme_returns_401(client):
    token = register(client).get_json()["token"]
    res = client.get("/api/_whoami", headers={"Authorization": f"Token {token}"})
    assert res.status_code == 401


def test_protected_route_with_valid_token_returns_200(client):
    token = register(client).get_json()["token"]
    res = client.get("/api/_whoami", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    assert res.get_json()["email"] == EMAIL


def test_protected_route_with_expired_token_returns_401(client, app):
    register(client)
    user = User.query.filter_by(email=EMAIL).first()
    past = datetime.now(timezone.utc) - timedelta(hours=1)
    expired = jwt.encode(
        {"sub": user.id, "email": user.email, "iat": past - timedelta(hours=1), "exp": past},
        app.config["SECRET_KEY"],
        algorithm="HS256",
    )
    res = client.get("/api/_whoami", headers={"Authorization": f"Bearer {expired}"})
    assert res.status_code == 401
    assert res.get_json()["error"] == "token_expired"


def test_protected_route_with_token_signed_by_wrong_key_returns_401(client):
    register(client)
    user = User.query.filter_by(email=EMAIL).first()
    forged = jwt.encode(
        {"sub": user.id, "exp": datetime.now(timezone.utc) + timedelta(hours=1)},
        "not-the-real-secret-key-0123456789abcdef",
        algorithm="HS256",
    )
    res = client.get("/api/_whoami", headers={"Authorization": f"Bearer {forged}"})
    assert res.status_code == 401
    assert res.get_json()["error"] == "invalid_token"


def test_protected_route_for_deleted_user_returns_401(client):
    token = register(client).get_json()["token"]
    user = User.query.filter_by(email=EMAIL).first()
    db.session.delete(user)
    db.session.commit()
    res = client.get("/api/_whoami", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 401

# ------------------------------------------------------------------- roles

def register_as(client, role, email=EMAIL):
    return client.post(
        "/api/auth/register", json={"email": email, "password": PASSWORD, "role": role}
    )


def test_register_defaults_to_member(client):
    assert register(client).get_json()["user"]["role"] == "member"


def test_register_as_business_owner(client):
    res = register_as(client, "business_owner")
    assert res.status_code == 201
    assert res.get_json()["user"]["role"] == "business_owner"


@pytest.mark.parametrize("bad_role", ["admin", "owner", 5])
def test_register_invalid_role_returns_400(client, bad_role):
    res = register_as(client, bad_role)
    assert res.status_code == 400
    assert res.get_json()["error"] == "invalid_role"


def test_login_returns_role(client):
    register_as(client, "business_owner")
    assert login(client).get_json()["user"]["role"] == "business_owner"


def test_role_route_without_token_returns_401(client):
    assert client.get("/api/_owner_only").status_code == 401


def test_role_route_rejects_member(client):
    token = register(client).get_json()["token"]
    res = client.get("/api/_owner_only", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 403
    assert res.get_json()["error"] == "forbidden"


def test_role_route_allows_business_owner(client):
    token = register_as(client, "business_owner").get_json()["token"]
    res = client.get("/api/_owner_only", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
