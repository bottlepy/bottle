#!/bin/bash

set -e
set -x

sudo apt-get install libev-dev

if [[ $TRAVIS_PYTHON_VERSION == 2.7 ]]; then
    pip install flup waitress cherrypy<9.0.0 paste fapws3 tornado twisted diesel meinheld gunicorn eventlet gevent rocket bjoern
fi

if [[ $TRAVIS_PYTHON_VERSION == 3.5 ]]; then
    pip install waitress cherrypy<9.0.0 paste tornado twisted diesel meinheld gunicorn eventlet gevent uvloop
fi
