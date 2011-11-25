#!/usr/bin/env python

import sys
import os
from distutils.core import setup

if sys.version_info < (2,5):
    raise NotImplementedError("Sorry, you need at least Python 2.5 or Python 3.x to use bottle.")

import bottle

setup(name='bottle',
      version=bottle.__version__,
      description='Fast and simple WSGI-framework for small web-applications.',
      long_description=bottle.__doc__,
      author=bottle.__author__,
      author_email='marc@gsites.de',
      url='http://bottlepy.org/',
      py_modules=['bottle'],
      scripts=['bottle.py'],
      license='MIT',
      platforms = 'any',
      classifiers=['Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content :: CGI Tools/Libraries',
        'Topic :: Internet :: WWW/HTTP :: HTTP Servers',
        'Topic :: Internet :: WWW/HTTP :: WSGI',
        'Topic :: Internet :: WWW/HTTP :: WSGI :: Application',
        'Topic :: Internet :: WWW/HTTP :: WSGI :: Middleware',
        'Topic :: Internet :: WWW/HTTP :: WSGI :: Server',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'Programming Language :: Python :: 2.5',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3'],
     )



