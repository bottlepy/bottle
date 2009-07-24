#!/usr/bin/env python

from distutils.core import setup
import bottle

setup(name='bottle',
      version=bottle.__version__,
      description='Fast and simple WSGI-framework for small web-applications.',
      long_description='Bottle is a fast and simple mirco-framework for small web-applications. It offers request dispatching (Routes) with url parameter support, Templates, key/value Databases, a build-in HTTP Server and adapters for many third party WSGI/HTTP-server and template engines. All in a single file and with no dependencies other than the Python Standard Library.',
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
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 3']
     )



