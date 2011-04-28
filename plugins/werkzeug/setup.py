#!/usr/bin/env python

"""
This plugin adds support for :class:`werkzeug.Response`, all kinds of
:exc:`werkzeug.HTTPException` and provides a thread-local instance of
:class:`werkzeug.Request`. It basically turns Bottle into Flask.

The plugin instance doubles as a werkzeug module object, so you don't need to
import werkzeug in your application.

For werkzeug library documentation, see: http://werkzeug.pocoo.org/

Example::

    import bottle
    from bottle.ext.werkzeug import WerkzeugPlugin

    app = bottle.Bottle()
    werkzeug = app.install(WerkzeugPlugin())
    wrequest = werkzueg.request # For the lazy.

    @app.route('/hello/:name')
    def say_hello(name):
        greet = {'en':'Hello', 'de':'Hallo', 'fr':'Bonjour'}
        language = wrequest.accept_language.best_match(greet.keys())
        if language:
            return werkzeug.Response('%s %s!' % (greet[language], name))
        else:
            raise werkzeug.exceptions.NotAcceptable()

"""

import sys
import os
import re
from distutils.core import setup

try:
    from distutils.command.build_py import build_py_2to3 as build_py
except ImportError:
    from distutils.command.build_py import build_py

setup(
    name = 'bottle-werkzeug',
    version = '0.1',
    url = 'http://bottlepy.org/docs/dev/plugin/werkzeug/',
    description = 'Werkzeug integration for Bottle',
    long_description = __doc__,
    author = 'Marcel Hellkamp',
    author_email = 'marc@gsites.de',
    license = 'MIT',
    platforms = 'any',
    py_modules = [
        'bottle_werkzeug'
    ],
    requires = [
        'bottle (>=0.9)',
        'werkzeug'
    ],
    classifiers = [
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    cmdclass = {'build_py': build_py}
)
