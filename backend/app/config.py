"""
Central config. Reads everything from environment variables (.env) so no
secrets ever live in source. See .env.example for the full key list.
"""
import os
from datetime import timedelta

from dotenv import load_dotenv

load_dotenv()  # loads .env in local dev; in prod, real env vars win


class BaseConfig:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-change-me")
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", "postgresql+psycopg2://localhost/loop_dev"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    JWT_EXPIRES_IN = timedelta(hours=int(os.environ.get("JWT_EXPIRES_HOURS", 24)))

    CORS_ORIGINS = os.environ.get("CORS_ORIGINS", "http://localhost:5173").split(",")


class DevelopmentConfig(BaseConfig):
    DEBUG = True


class TestingConfig(BaseConfig):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "TEST_DATABASE_URL", "postgresql+psycopg2://localhost/loop_test"
    )


class ProductionConfig(BaseConfig):
    DEBUG = False


_CONFIGS = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
}


def get_config(name: str | None = None):
    name = name or os.environ.get("FLASK_ENV", "development")
    return _CONFIGS.get(name, DevelopmentConfig)
