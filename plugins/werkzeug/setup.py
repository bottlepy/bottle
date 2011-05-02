#!/usr/bin/env python

import sys
import os
from distutils.core import setup

try:
    from distutils.command.build_py import build_py_2to3 as build_py
except ImportError:
    from distutils.command.build_py import build_py

# This ugly hack executes the first few lines of the module file to look up some
# common variables. We cannot just import the module because it depends on other
# modules that might not be installed yet.
filename = os.path.join(os.path.dirname(__file__), 'bottle_werkzeug.py')
source = open(filename).read().split('### CUT HERE')[0]
exec(source)

setup(
    name = 'bottle-werkzeug',
    version = __version__,
    url = 'http://bottlepy.org/docs/dev/plugin/werkzeug/',
    description = 'Werkzeug integration for Bottle.',
    long_description = __doc__,
    author = 'Marcel Hellkamp',
    author_email = 'marc@gsites.de',
    license = __license__,
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
