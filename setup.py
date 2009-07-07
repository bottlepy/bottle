#!/usr/bin/env python

from distutils.core import setup
import bottle

setup(name='bottle',
      version='%d.%d.%d' % bottle.__version__,
      description='WSGI micro web framework + templates',
      author='Marcel Hellkamp',
      author_email='marc@gsites.de',
      url='http://github.com/defnull/bottle',
      py_modules=['bottle'],
      license='MIT',
      classifiers=['Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content :: CGI Tools/Libraries',
        'Topic :: Internet :: WWW/HTTP :: HTTP Servers',
        'Topic :: Internet :: WWW/HTTP :: WSGI',
        'Topic :: Internet :: WWW/HTTP :: WSGI :: Application',
        'Topic :: Internet :: WWW/HTTP :: WSGI :: Middleware',
        'Topic :: Internet :: WWW/HTTP :: WSGI :: Server',
        'Topic :: Software Development :: Libraries :: Application Frameworks']
     )



