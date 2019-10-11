#!/usr/bin/env bash

# This script is run by travis-ci prior to running tests.
set -e
set -x

# Just to be sure
pip install -U pip
# pip is not able to install distribute: "ImportError: No module named _markerlib"
easy_install distribute

pip install -U coverage
pip install coveralls


if  [[ $TRAVIS_PYTHON_VERSION == 3.6 ]]; then
    sudo apt-get update -y
    sudo apt-get install -y libev-dev
    pip install mako jinja2 waitress "cherrypy<9" cheroot paste tornado twisted diesel meinheld gunicorn eventlet
    pip install uvloop
fi

