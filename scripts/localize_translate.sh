#!/usr/bin/env bash

# https://pythonhosted.org/Flask-Babel/#translating-applications
pybabel init -i messages.pot -d translations -l en
pybabel init -i messages.pot -d translations -l nl
