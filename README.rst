.. image:: http://bottlepy.org/docs/dev/_static/logo_nav.png
  :target: http://bottlepy.org/
  :alt: Bottle Logo
  :align: right

.. image:: https://github.com/bottlepy/bottle/workflows/Tests/badge.svg
    :target: https://github.com/bottlepy/bottle/workflows/Tests
    :alt: Tests Status

.. image:: https://img.shields.io/pypi/v/bottle.svg
    :target: https://pypi.python.org/pypi/bottle/
    :alt: Latest Version

.. image:: https://img.shields.io/pypi/l/bottle.svg
    :target: https://pypi.python.org/pypi/bottle/
    :alt: License

.. _Python: https://python.org/
.. _mako: https://www.makotemplates.org/
.. _cheetah: https://www.cheetahtemplate.org/
.. _jinja2: https://jinja.palletsprojects.com/

.. _WSGI: https://peps.python.org/pep-3333/
.. _gunicorn: https://gunicorn.org/
.. _paste: https://pythonpaste.readthedocs.io/
.. _cheroot: https://cheroot.cherrypy.dev/

============================
Bottle: Python Web Framework
============================

Bottle is a fast, simple and lightweight WSGI_ micro web-framework for Python_. It is distributed as a single file module and has no dependencies other than the `Python Standard Library <http://docs.python.org/library/>`_.

* **Routing:** Requests to function-call mapping with support for clean and dynamic URLs.
* **Templates:** Fast `built-in template engine <http://bottlepy.org/docs/dev/tutorial.html#tutorial-templates>`_ and support for mako_, jinja2_ and cheetah_ templates.
* **Utilities:** Convenient access to form data, file uploads, cookies, headers and other HTTP features.
* **Server:** Built-in development server and ready-to-use adapters for a wide range of WSGI_ capable HTTP server (e.g. gunicorn_, paste_ or cheroot_).


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

Install the latest stable release with ``pip install bottle`` or download `bottle.py`__ (unstable) into your project directory. There are no hard dependencies other than the Python standard library.

License
-------

.. __: https://github.com/bottlepy/bottle/raw/master/LICENSE

Code and documentation are available according to the MIT License (see LICENSE__).

The Bottle logo however is *NOT* covered by that license. It is allowed to use the logo as a link to the bottle homepage or in direct context with the unmodified library. In all other cases, please ask first.
