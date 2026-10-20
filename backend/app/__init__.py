"""
Loop backend application factory.

Owned by: Maria (Database + Auth)
Do not add Google Places / Mapbox proxy routes here — those belong to
Isabella's blueprint (app/places.py, registered separately). This factory
only wires up the pieces this PBI owns: db, bcrypt, and the auth blueprint.
"""
import os
from flask import Flask, jsonify
from flask_cors import CORS

from .config import get_config
from .extensions import db, bcrypt
from .auth import auth_bp


def create_app(config_name: str | None = None) -> Flask:
    app = Flask(__name__)
    app.config.from_object(get_config(config_name))

    # --- Extensions ---
    db.init_app(app)
    bcrypt.init_app(app)
    CORS(
        app,
        resources={r"/api/*": {"origins": app.config["CORS_ORIGINS"]}},
        supports_credentials=True,
    )

    # --- Blueprints ---
    app.register_blueprint(auth_bp, url_prefix="/api/auth")

    # Teammates register their own blueprints in main.py / run.py, e.g.:
    #   from app.places import places_bp
    #   app.register_blueprint(places_bp, url_prefix="/api/places")

    @app.get("/api/health")
    def health():
        return jsonify({"status": "ok"}), 200

    @app.errorhandler(404)
    def not_found(_e):
        return jsonify({"error": "not_found", "message": "Resource not found."}), 404

    @app.errorhandler(500)
    def server_error(_e):
        return jsonify({"error": "server_error", "message": "Something went wrong."}), 500

    return app
