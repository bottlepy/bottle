.. image:: http://bottlepy.org/docs/dev/_static/logo_nav.png
  :target: http://bottlepy.org/
  :alt: Bottle Logo
  :align: right

.. image:: https://travis-ci.org/bottlepy/bottle.svg?branch=master
    :target: https://travis-ci.org/bottlepy/bottle
    :alt: Bottle Build

.. image:: https://coveralls.io/repos/github/bottlepy/bottle/badge.svg?branch=master
   :target: https://coveralls.io/github/bottlepy/bottle?branch=master
   :alt: Coverage 

.. image:: https://img.shields.io/pypi/dm/bottle.svg
    :target: https://pypi.python.org/pypi/bottle/
    :alt: Downloads

.. image:: https://img.shields.io/pypi/v/bottle.svg
    :target: https://pypi.python.org/pypi/bottle/
    :alt: Latest Version

.. image:: https://img.shields.io/pypi/l/bottle.svg
    :target: https://pypi.python.org/pypi/bottle/
    :alt: License

.. _mako: http://www.makotemplates.org/
.. _cheetah: http://www.cheetahtemplate.org/
.. _jinja2: http://jinja.pocoo.org/
.. _paste: http://pythonpaste.org/
.. _fapws3: https://github.com/william-os4y/fapws3
.. _bjoern: https://github.com/jonashaag/bjoern
.. _cherrypy: http://www.cherrypy.org/
.. _WSGI: http://www.wsgi.org/
.. _Python: http://python.org/

============================
Bottle: Python Web Framework
============================

Bottle is a fast, simple and lightweight WSGI_ micro web-framework for Python_. It is distributed as a single file module and has no dependencies other than the `Python Standard Library <http://docs.python.org/library/>`_.


* **Routing:** Requests to function-call mapping with support for clean and  dynamic URLs.
* **Templates:** Fast and pythonic `*built-in template engine* <http://bottlepy.org/docs/dev/tutorial.html#tutorial-templates>`_ and support for mako_, jinja2_ and cheetah_ templates.
* **Utilities:** Convenient access to form data, file uploads, cookies, headers and other HTTP-related metadata.
* **Server:** Built-in HTTP development server and support for paste_, fapws3_, bjoern_, `Google App Engine <https://cloud.google.com/appengine/>`_, cherrypy_ or any other WSGI_ capable HTTP server.

Homepage and documentation: http://bottlepy.org


Example: "Hello World" in a bottle
----------------------------------

.. code-block:: python

  from bottle import route, run, template

  @route('/hello/<name>')
  def index(name):
      return template('<b>Hello {{name}}</b>!', name=name)

  run(host='localhost', port=8080)

Run this script or paste it into a Python console, then point your browser to `<http://localhost:8080/hello/world>`_. That's it.


Download and Install
--------------------

.. __: https://github.com/bottlepy/bottle/raw/master/bottle.py

Install the latest stable release with ``pip install bottle``, ``easy_install -U bottle`` or download `bottle.py`__ (unstable) into your project directory. There are no hard dependencies other than the Python standard library. Bottle runs with **Python 2.7 and 3.2+**.


License
-------

.. __: https://github.com/bottlepy/bottle/raw/master/LICENSE

Code and documentation are available according to the MIT License (see LICENSE__).

The Bottle logo however is *NOT* covered by that license. It is allowed to use the logo as a link to the bottle homepage or in direct context with the unmodified library. In all other cases please ask first.
