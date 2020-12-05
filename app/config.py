# Standard library imports
import os
from typing import Optional

# Third party imports
from flask_env import MetaFlaskEnv


class Config(metaclass=MetaFlaskEnv):
    """Base configuration."""

    ENV: str = ""
    HOST = "0.0.0.0"
    PORT = "5050"
    GLOBAL_URL_PREFIX = "api"

    # Flask
    SECRET_KEY = "MY_VERY_SECRET_KEY"

    API_TITLE = "Library API Server"
    OPENAPI_VERSION = "3.0.2"

    # SQLAlchemy
    SQLALCHEMY_DATABASE_URI: Optional[str] = None
    SQLALCHEMY_ECHO: bool = False
    SQLALCHEMY_TRACK_MODIFICATIONS: bool = False

    # flask-babel
    BABEL_DEFAULT_LOCALE = "en"
    BABEL_DEFAULT_TIMEZONE = "UTC"
    BABEL_TRANSLATION_DIRECTORIES = os.path.abspath("translations")
    LANGUAGES = {"en": "English", "nl": "Dutch"}


class DevConfig(Config):
    ENV = "dev"

    # SQLAlchemy
    SQLALCHEMY_ECHO = True
    SQLALCHEMY_DATABASE_URI = (
        "postgresql://library-dev:library-dev@localhost:5432/library-dev"
    )


class ProdConfig(Config):
    ENV = "prod"


class TestConfig(Config):
    ENV = "test"

    # SQLAlchemy
    SQLALCHEMY_DATABASE_URI = (
        "postgresql://library-test:library-test@localhost:5432/library-test"
    )
