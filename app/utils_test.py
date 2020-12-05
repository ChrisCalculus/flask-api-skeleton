# Standard library imports
import logging
import os

# Third party imports
import colors
import pytest
from flask import Flask
from flask_env import MetaFlaskEnv

# Local application imports
from app.config import DevConfig, ProdConfig
from app.utils import (
    camelcase,
    get_config,
    localize_text,
    print_config,
    print_routes,
    timedelta_in_ms,
)


def test_get_config():
    # Test debug
    os.environ["FLASK_DEBUG"] = "1"
    assert get_config() == DevConfig

    # Test production
    os.environ["FLASK_DEBUG"] = "0"
    assert get_config() == ProdConfig

    del os.environ["FLASK_DEBUG"]
    assert get_config() == ProdConfig


def test_camelcase():
    lowercase_str = "lowercase"
    assert camelcase(lowercase_str) == "lowercase"

    duckcase_str = "duck_case"
    assert camelcase(duckcase_str) == "duckCase"

    number_str = "1"
    assert camelcase(number_str) == "1"

    # Test no-string input
    with pytest.raises(AssertionError):
        camelcase(1)

    # Test None input
    with pytest.raises(AssertionError):
        camelcase(None)


def test_localize_text(monkeypatch):
    translation = "translation"
    monkeypatch.setattr("flask_babel.gettext", lambda: translation)

    assert localize_text(translation) == translation

    # Test no-string input
    with pytest.raises(AssertionError):
        localize_text(1)

    # Test None input
    with pytest.raises(AssertionError):
        localize_text(None)


def test_print_routes(caplog):
    app = Flask(__name__)

    def test_route_1():
        return "OK", 200

    assert test_route_1() == ("OK", 200)

    def test_route_2():
        return "OK", 200

    assert test_route_2() == ("OK", 200)

    app.add_url_rule("/1", "test_route_1", view_func=test_route_1)
    app.add_url_rule("/2", "test_route_2", view_func=test_route_2)

    with caplog.at_level(logging.DEBUG):
        print_routes(app)

    get = f"{colors.color('GET', fg='blue')}"

    expected_output = [
        "Routes:",
        f"{get} {colors.color('/1', fg='green')} {colors.color('test_route_1', fg='gray')}",
        f"{get} {colors.color('/2', fg='green')} {colors.color('test_route_2', fg='gray')}",
        f"{get} {colors.color('/static/<path:filename>', fg='green')} {colors.color('static', fg='gray')}",
    ]

    for record in caplog.records:
        assert record.message in expected_output


def test_print_config(caplog):
    app = Flask(__name__)

    class SomeConfig(metaclass=MetaFlaskEnv):
        A = 1
        B = "2"

    expected_output = [
        colors.color(f"Loaded '{SomeConfig.__name__}'", fg="green"),
        f"{colors.color('A', fg='magenta')}: {colors.color('1', fg='blue')}",
        f"{colors.color('B', fg='magenta')}: {colors.color('2', fg='blue')}",
    ]

    with caplog.at_level(logging.INFO):
        print_config(app, SomeConfig)

    for record in caplog.records:
        assert record.message in expected_output

    # Test invalid config
    class OtherConfig(object):
        A = 2

    with pytest.raises(AssertionError):
        print_config(app, OtherConfig)


def test_timedelta_in_ms():
    # Standard library imports
    from datetime import datetime as dt
    from datetime import timedelta as td

    now = dt.now()
    five_minutes = td(minutes=5)
    five_minutes_ago = now - five_minutes
    five_minutes_in_ms = round(five_minutes.microseconds / 1000)

    timedelta = timedelta_in_ms(now, five_minutes_ago)

    assert timedelta == five_minutes_in_ms

    assert timedelta_in_ms(five_minutes_ago, now) == 0

    assert timedelta_in_ms("a", "b") == 0

    assert timedelta_in_ms(now, 1) == 0

    assert timedelta_in_ms(now, now) == 0
