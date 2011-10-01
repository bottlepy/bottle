#!/usr/bin/env python

import sys
import os
from distutils.core import setup

if sys.version_info < (2,5):
    raise NotImplementedError("Sorry, you need at least Python 2.5 or Python 3.x to use bottle.")

try:
    from distutils.command.build_py import build_py_2to3 as build_py
except ImportError:
    from distutils.command.build_py import build_py

# Ugly, but we can't import bottle with 3.x to read __version__ (throws SyntaxError)
for line in open(os.path.join(os.path.dirname(sys.argv[0]),'bottle.py')):
    if line.startswith('__version__'):
        version = eval(line.split('=')[-1])

setup(name='bottle',
      version=version,
      description='Fast and simple WSGI-framework for small web-applications.',
      long_description='Bottle is a fast and simple micro-framework for small web-applications. It offers request dispatching (Routes) with url parameter support, Templates, a built-in HTTP Server and adapters for many third party WSGI/HTTP-server and template engines. All in a single file and with no dependencies other than the Python Standard Library.',
      author='Marcel Hellkamp',
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
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 3'],
      cmdclass = {'build_py': build_py}
     )



