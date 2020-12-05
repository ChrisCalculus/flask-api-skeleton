#!/usr/bin/env bash

# https://pythonhosted.org/Flask-Babel/#translating-applications
pybabel extract -F babel.cfg -k localize_text -o messages.pot . --no-default-keywords