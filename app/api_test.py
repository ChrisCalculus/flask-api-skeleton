# Third party imports
import pytest

# Local application imports
from app import Config, configure_app, create_app, handle_error
from app.api.error import APIError


def test_handle_error(monkeypatch):
    error = APIError()
    monkeypatch.setattr(
        "app.api.response.APIResponse.create_error_response", lambda *x: None
    )
    response = handle_error(error)
    assert response is None

    with pytest.raises(AssertionError):
        error = "a"
        handle_error(error)


class DummyConfig(Config):
    pass


class DummyDebugConfig(Config):
    DEBUG = True


def test_configure_app(monkeypatch, app):
    monkeypatch.setattr("app.get_config", lambda *x: None)
    monkeypatch.setattr("flask.config.Config.from_object", lambda *x: None)

    # Without config
    result = configure_app(app)
    assert result is None

    # With config
    config = DummyConfig
    result = configure_app(app, config)
    assert result == DummyConfig


def test_create_app(monkeypatch, app):
    debug_calls = []

    monkeypatch.setattr("app.Flask", lambda *x: app)
    monkeypatch.setattr("app.configure_app", lambda *x: DummyConfig)
    monkeypatch.setattr("app.configure_db", lambda *x: None)
    monkeypatch.setattr("app.register_apis", lambda *x: None)
    monkeypatch.setattr("flask_babel.Babel.init_app", lambda *x: None)
    monkeypatch.setattr("app.setup_error_handlers", lambda *x: None)
    monkeypatch.setattr("app.print_config", lambda *x: debug_calls.append(1))
    monkeypatch.setattr("app.print_routes", lambda *x: debug_calls.append(1))

    # Without config
    result = create_app()
    assert result == app

    # With config
    config = DummyConfig
    result = create_app(config)
    assert result == app

    with pytest.raises(AssertionError):
        create_app({})


def test_create_debug_app(monkeypatch, app):
    debug_calls = []

    monkeypatch.setattr("app.Flask", lambda *x: app)
    monkeypatch.setattr("app.configure_app", lambda *x: None)
    monkeypatch.setattr("app.configure_db", lambda *x: None)
    monkeypatch.setattr("app.register_apis", lambda *x: None)
    monkeypatch.setattr("flask_babel.Babel.init_app", lambda *x: None)
    monkeypatch.setattr("app.setup_error_handlers", lambda *x: None)
    monkeypatch.setattr("app.print_config", lambda *x: debug_calls.append(1))
    monkeypatch.setattr("app.print_routes", lambda *x: debug_calls.append(1))

    app.debug = True

    result = create_app()
    assert result == app
    assert len(debug_calls) == 2
