#!/usr/bin/env bash
set -e
set -x

# Test utilities
pip install -U pip pytest coverage

# Test dependencies (template engines)
pip install mako jinja2

for name in waitress "cherrypy<9" cheroot paste tornado twisted diesel meinheld\
            gunicorn eventlet flup bjoern gevent aiohttp-wsgi uvloop; do
    pip install $name || echo "Failed to install $name with $(python -V 2>&1)" 1>&2
done
