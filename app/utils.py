# Standard library imports
from datetime import datetime as dt

# Third party imports
import colors
from flask import Flask, current_app
from flask.helpers import get_debug_flag
from flask_babel import gettext
from flask_env import MetaFlaskEnv

# Local application imports
from app.config import DevConfig, ProdConfig


def get_config() -> MetaFlaskEnv:
    if get_debug_flag():
        return DevConfig
    return ProdConfig


def camelcase(s: str) -> str:
    assert isinstance(s, str)
    parts = iter(s.split("_"))
    return next(parts) + "".join(i.title() for i in parts)


def localize_text(key: str) -> str:
    assert isinstance(key, str) and len(key)
    return gettext(key)


def print_routes(app: Flask):
    assert isinstance(app, Flask)

    app.logger.debug("Routes:")

    endpoint_rules = []

    with app.app_context():
        for rule in app.url_map.iter_rules():
            rule_methods = []
            for method in rule.methods:
                if method in ["GET", "POST", "DELETE", "PUT"]:
                    rule_methods.append(method)
            endpoint_rules.append((rule.endpoint, rule.rule, ", ".join(rule_methods)))

    endpoint_rules.sort(key=lambda t: t[1])

    for rule in endpoint_rules:
        endpoint = colors.color(f"{rule[1]}", fg="green")
        endpoint_module = colors.color(f"{rule[0]}", fg="gray")
        endpoint_methods = colors.color(f"{rule[2]}", fg="blue")
        app.logger.debug(f"{endpoint_methods} {endpoint} {endpoint_module}")


def print_config(app: Flask, config: MetaFlaskEnv):
    assert isinstance(app, Flask)
    assert type(config) == MetaFlaskEnv

    app.logger.debug("Config:")

    with app.app_context():
        current_app.logger.info(colors.color(f"Loaded '{config.__name__}'", fg="green"))

        for attr in dir(config):
            val = getattr(config, attr)
            if not attr.startswith("__") and not callable(val):
                attr_color = colors.color(f"{attr}", fg="magenta")
                val_color = colors.color(f"{val}", fg="blue")
                current_app.logger.info(f"{attr_color}: {val_color}")


def timedelta_in_ms(a: dt, b: dt) -> int:
    if isinstance(a, dt) and isinstance(b, dt) and a > b:
        assert a > b
        return round((a - b).microseconds / 1000)
    return 0
