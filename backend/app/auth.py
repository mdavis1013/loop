"""
PBI-02 — Authentication API (bcrypt + JWT)
Owner: Maria

Endpoints:
  POST /api/auth/register  -> 201 {token, user}
  POST /api/auth/login     -> 200 {token, user}

Also exports @token_required, a reusable decorator for any future route
(Isabella's Places routes, bookmark CRUD, review endpoints, etc.) that needs
an authenticated user. It attaches the resolved User to `request.current_user`.
"""
from datetime import datetime, timezone
from functools import wraps

import jwt
from flask import Blueprint, current_app, jsonify, request
from sqlalchemy.exc import IntegrityError

from .extensions import db, bcrypt
from .models import User

auth_bp = Blueprint("auth", __name__)

MIN_PASSWORD_LENGTH = 8


def _error(message: str, status: int, code: str = "bad_request"):
    return jsonify({"error": code, "message": message}), status


def _valid_email(email: str) -> bool:
    return isinstance(email, str) and "@" in email and "." in email.split("@")[-1]


def _issue_token(user: User) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": user.id,
        "email": user.email,
        "iat": now,
        "exp": now + current_app.config["JWT_EXPIRES_IN"],
    }
    return jwt.encode(payload, current_app.config["SECRET_KEY"], algorithm="HS256")


def token_required(f):
    """
    Protects a route: requires `Authorization: Bearer <token>`.
    On success, sets request.current_user to the User row and calls the view.
    On failure, returns 401 before the view runs.

    Usage in a teammate's blueprint:

        from app.auth import token_required

        @places_bp.post("/save")
        @token_required
        def save_place():
            user = request.current_user
            ...
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return _error("Missing or malformed Authorization header.", 401, "unauthorized")

        token = auth_header.split(" ", 1)[1].strip()
        try:
            payload = jwt.decode(
                token, current_app.config["SECRET_KEY"], algorithms=["HS256"]
            )
        except jwt.ExpiredSignatureError:
            return _error("Token has expired.", 401, "token_expired")
        except jwt.InvalidTokenError:
            return _error("Invalid token.", 401, "invalid_token")

        user = db.session.get(User, payload.get("sub"))
        if user is None:
            return _error("User for this token no longer exists.", 401, "unauthorized")

        request.current_user = user
        return f(*args, **kwargs)

    return decorated


@auth_bp.post("/register")
def register():
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    if not _valid_email(email):
        return _error("A valid email is required.", 400, "invalid_email")
    if len(password) < MIN_PASSWORD_LENGTH:
        return _error(
            f"Password must be at least {MIN_PASSWORD_LENGTH} characters.",
            400,
            "weak_password",
        )

    password_hash = bcrypt.generate_password_hash(password).decode("utf-8")
    user = User(email=email, password_hash=password_hash)

    db.session.add(user)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return _error("An account with this email already exists.", 409, "email_taken")

    token = _issue_token(user)
    return jsonify({"token": token, "user": user.to_public_dict()}), 201


@auth_bp.post("/login")
def login():
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    user = User.query.filter_by(email=email).first()
    if user is None or not bcrypt.check_password_hash(user.password_hash, password):
        # Same message for "no such user" and "wrong password" — never reveal
        # which one it was, that's a user-enumeration leak.
        return _error("Invalid email or password.", 401, "invalid_credentials")

    token = _issue_token(user)
    return jsonify({"token": token, "user": user.to_public_dict()}), 200
