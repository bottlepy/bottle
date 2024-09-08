.. highlight:: python
.. currentmodule:: bottle

.. _mako: http://www.makotemplates.org/
.. _cheetah: http://www.cheetahtemplate.org/
.. _jinja2: https://jinja.palletsprojects.com/
.. _paste: https://pythonpaste.readthedocs.io/
.. _bjoern: https://github.com/jonashaag/bjoern
.. _flup: http://trac.saddi.com/flup
.. _gunicorn: https://gunicorn.org/
.. _cheroot: https://cheroot.cherrypy.dev/
.. _WSGI: https://peps.python.org/pep-3333/
.. _Python: http://python.org/
.. _testing: https://github.com/bottlepy/bottle/raw/master/bottle.py
.. _issue_tracker: https://github.com/bottlepy/bottle/issues
.. _PyPI: http://pypi.python.org/pypi/bottle
.. _gae: https://developers.google.com/appengine/

============================
Bottle: Python Web Framework
============================

Bottle is a fast, simple and lightweight WSGI_ micro web-framework for Python_. It is distributed as a single file module and has no dependencies other than the `Python Standard Library <http://docs.python.org/library/>`_.


* **Routing:** Requests to function-call mapping with support for clean and dynamic URLs.
* **Templates:** Fast and pythonic :ref:`built-in template engine <tutorial-templates>` and support for mako_, jinja2_ and cheetah_ templates.
* **Utilities:** Convenient access to form data, file uploads, cookies, headers and other HTTP features.
* **Server:** Built-in HTTP development server and support for a wide range of WSGI_ capable HTTP server (e.g. gunicorn_, paste_ or cheroot_).

.. rubric:: Example: "Hello World" in a bottle

::

  from bottle import route, run, template

  @route('/hello/<name>')
  def index(name):
      return template('<b>Hello {{name}}</b>!', name=name)

  run(host='localhost', port=8080)

Run this script or paste it into a Python console, then point your browser to `<http://localhost:8080/hello/world>`_. That's it.

Download and Install
====================

.. __: https://github.com/bottlepy/bottle/raw/master/bottle.py

Install the latest stable release with ``pip install bottle`` or download `bottle.py`__ (unstable) into your project directory. There are no hard [1]_ dependencies other than the Python standard library.

Dead Snakes
===========

Bottle up to version 0.12 supported an absurd range of Python versions, some of which reached their end-of-life well over a decade ago. Starting with Bottle 0.13 we ensure backwards compatibility with `maintained versions of Python <https://devguide.python.org/versions/>`_ only. Outdated Python versions may still work, but are no longer tested for compatibility.

If you are in the unfortunate position to have to rely on "dead snakes" for production, just stick with Bottle 0.12 (LTS) or whichever release of Bottle still supports it. Everyone else should upgrade regularly to benefit from new features and improvements.

.. list-table:: Python Support Matrix
   :widths: 50 25 25
   :header-rows: 1

   * - Bottle Release
     - Python 2
     - Python 3
   * - 0.12
     - 2.5 - 2.7
     - 3.2 - 3.12
   * - 0.13
     - 2.7
     - >=3.8 [2]_
   * - 0.14 (planned)
     - *dropped*
     - >=3.8



Documentation
=============

.. toctree::
   :maxdepth: 2
   :caption: Getting Started

   tutorial
   api
   changelog
   faq

.. toctree::
   :maxdepth: 2
   :caption: Advanced Topics

   routing
   configuration
   stpl
   deployment
   async

.. toctree::
   :maxdepth: 2
   :caption: Plugins

   plugins/index
   plugins/dev
   plugins/list

.. toctree::
   :maxdepth: 2
   :caption: Additional Notes

   tutorial_app

.. toctree::
   :maxdepth: 2
   :caption: Development

   development
   contributors


License
==================

Code and documentation are available according to the MIT License:

.. include:: ../LICENSE
  :literal:

The Bottle logo however is *NOT* covered by that license. It is allowed to
use the logo as a link to the bottle homepage or in direct context with
the unmodified library. In all other cases please ask first.

.. rubric:: Footnotes

.. [1] Usage of the template or server adapter classes requires the corresponding template or server modules.
.. [2] Bottle 0.13 technically still works with Python 3.6 and 3.7 but is not tested with those versions.

