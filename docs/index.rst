.. highlight:: python
.. currentmodule:: bottle

.. _mako: http://www.makotemplates.org/
.. _cheetah: http://www.cheetahtemplate.org/
.. _jinja2: http://jinja.pocoo.org/
.. _paste: http://pythonpaste.org/
.. _fapws3: https://github.com/william-os4y/fapws3
.. _bjoern: https://github.com/jonashaag/bjoern
.. _flup: http://trac.saddi.com/flup
.. _cherrypy: http://www.cherrypy.org/
.. _WSGI: http://www.wsgi.org/
.. _Python: http://python.org/
.. _testing: https://github.com/bottlepy/bottle/raw/master/bottle.py
.. _issue_tracker: https://github.com/bottlepy/bottle/issues
.. _PyPI: http://pypi.python.org/pypi/bottle
.. _gae: https://developers.google.com/appengine/

============================
Bottle: Python Web Framework
============================

Bottle is a fast, simple and lightweight WSGI_ micro web-framework for Python_. It is distributed as a single file module and has no dependencies other than the `Python Standard Library <http://docs.python.org/library/>`_.


* **Routing:** Requests to function-call mapping with support for clean and  dynamic URLs.
* **Templates:** Fast and pythonic :ref:`built-in template engine <tutorial-templates>` and support for mako_, jinja2_ and cheetah_ templates.
* **Utilities:** Convenient access to form data, file uploads, cookies, headers and other HTTP-related metadata.
* **Server:** Built-in HTTP development server and support for paste_, fapws3_, bjoern_, gae_, cherrypy_ or any other WSGI_ capable HTTP server.

.. rubric:: Example: "Hello World" in a bottle

::

  from bottle import route, run, template

  @route('/hello/<name>')
  def index(name):
      return template('<b>Hello {{name}}</b>!', name=name)

  run(host='localhost', port=8080)

Run this script or paste it into a Python console, then point your browser to `<http://localhost:8080/hello/world>`_. That's it.

.. rubric:: Download and Install

.. __: https://github.com/bottlepy/bottle/raw/master/bottle.py

Install the latest stable release with ``pip install bottle`` or download `bottle.py`__ (unstable) into your project directory. There are no hard [1]_ dependencies other than the Python standard library. Bottle supports **Python 2.7 and Python 3**.

.. deprecated:: 0.13
    Support for Python 2.5 and 2.6 was dropped with this release.


User's Guide
===============
Start here if you want to learn how to use the bottle framework for web development. If you have any questions not answered here, feel free to ask the `mailing list <mailto:bottlepy@googlegroups.com>`_.

.. toctree::
   :maxdepth: 2

   tutorial
   configuration
   routing
   stpl
   deployment
   api
   plugins/index


Knowledge Base
==============
A collection of articles, guides and HOWTOs.

.. toctree::
   :maxdepth: 2

   tutorial_app
   async
   recipes
   faq


Development and Contribution
============================

These chapters are intended for developers interested in the bottle development and release workflow.

.. toctree::
   :maxdepth: 2

   changelog
   development
   plugindev


.. toctree::
   :hidden:

   plugins/index
   contact

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

