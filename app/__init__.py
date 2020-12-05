# Third party imports
from flask import Flask
from flask_env import MetaFlaskEnv

# Local application imports
from app.api import register_apis
from app.config import Config
from app.extensions import babel
from app.utils import get_config, print_config, print_routes


def configure_app(app: Flask, config: MetaFlaskEnv = None):
    assert isinstance(app, Flask)

    if config is not None:
        assert type(config) == MetaFlaskEnv
        assert issubclass(config, Config)

    if config is None:
        config = get_config()

    app.config.from_object(config)

    return config


def configure_db(app: Flask):
    # Local application imports
    from app.extensions import db, migrate

    db.init_app(app)
    migrate.init_app(app, db)


def handle_error(error):
    # Local application imports
    from app.api.error import APIError
    from app.api.response import APIResponse

    assert isinstance(error, APIError)
    return APIResponse().create_error_response(error)


def setup_error_handlers(app):
    # Local application imports
    from app.api.error import BadRequestError, NotFoundError, ValidationError

    app.register_error_handler(BadRequestError, handle_error)
    app.register_error_handler(NotFoundError, handle_error)
    app.register_error_handler(ValidationError, handle_error)


def create_app(config: MetaFlaskEnv = None):
    if config is not None:
        assert type(config) == MetaFlaskEnv
        assert issubclass(config, Config)

    app = Flask(__name__)
    config = configure_app(app, config)
    configure_db(app)

    register_apis(app)

    # Internationalization
    babel.init_app(app)

    # Error handling
    setup_error_handlers(app)

    # Print debug info
    if app.debug is True:
        print_config(app, config)
        print_routes(app)

    return app
