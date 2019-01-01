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

# Server back-ends and template engines. Not all back-ends support all python versions and we only want to test for 2.7 and 3.6 to keep things sane
case ${TRAVIS_PYTHON_VERSION} in
2.7|3.6)
    sudo apt-get update -y
    sudo apt-get install -y libev-dev
    pip install mako jinja2 waitress "cherrypy<9" cheroot paste tornado twisted meinheld gunicorn eventlet
    ;;
esac

case ${TRAVIS_PYTHON_VERSION} in
2.7)
    pip install flup fapws3 bjoern gevent diesel
    ;;
3.6)
    pip install uvloop
    ;;
esac
