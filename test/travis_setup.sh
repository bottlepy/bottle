
# This script is run by travis-ci prior to running tests.
set -e
set -x

# Coverage 4.0 doesn't support Python 3.2
if [[ $TRAVIS_PYTHON_VERSION == 3.2 ]]; then
    pip install coverage==3.7.1
else
    pip install -U coverage
fi

pip install coveralls

# Server back-ends and template engines. Not all back-ends support all python versions and we only want to test for 2.7 and 3.6 to keep things sane
if [[ $TRAVIS_PYTHON_VERSION == 2.7 ]]; then
    sudo apt-get install libev-dev
    pip install mako jinja2 waitress "cherrypy<9" cheroot paste tornado twisted diesel meinheld gunicorn eventlet
    pip install flup fapws3 rocket bjoern gevent
elif  [[ $TRAVIS_PYTHON_VERSION == 3.6 ]]; then
    sudo apt-get install libev-dev
    pip install mako jinja2 waitress "cherrypy<9" cheroot paste tornado twisted diesel meinheld gunicorn eventlet
    pip install uvloop
fi

