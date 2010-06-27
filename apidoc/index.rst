.. highlight:: python
.. currentmodule:: bottle


.. _mako: http://www.makotemplates.org/
.. _cheetah: http://www.cheetahtemplate.org/
.. _jinja2: http://jinja.pocoo.org/2/
.. _paste: http://pythonpaste.org/
.. _fapws3: http://github.com/william-os4y/fapws3
.. _flup: http://trac.saddi.com/flup
.. _cherrypy: http://www.cherrypy.org/
.. _WSGI: http://www.wsgi.org/wsgi/
.. _Python: http://python.org/
.. _testing: http://github.com/defnull/bottle/raw/master/bottle.py
.. _issue_tracker: http://github.com/defnull/bottle/issues
.. _PyPi: http://pypi.python.org/pypi/bottle

============================
Bottle: Python Web Framework
============================

Bottle is a fast, simple and lightweight WSGI_ micro web-framework for Python_. It is distributed as a single file module and has no dependencies other than the `Python Standard Library <http://docs.python.org/library/>`_. 

.. rubric:: Core Features

* **Routing:** Requests to function-call mapping with support for clean and  dynamic URLs.
* **Templates:** Fast and pythonic :ref:`build-in template engine <tutorial-templates>` and support for mako_, jinja2_ and cheetah_ templates.
* **Utilities:** Convenient access to form data, file uploads, cookies, headers and other HTTP related metadata.
* **Server:** Build-in HTTP development server and support for paste_, fapws3_, flup_, cherrypy_ or any other WSGI_ capable HTTP server.

.. rubric:: Example: "Hello World" in a bottle

::

  from bottle import route, run

  @route('/:name')
  def index(name='World'):
      return '<b>Hello %s!</b>' % name

  run(host='localhost', port=8080)

.. rubric:: Download and Install

.. _download:

.. __: http://github.com/defnull/bottle/raw/master/bottle.py

Install the latest stable release via PyPi_ (``easy_install -U bottle``) or download `bottle.py`__ (unstable) into your project directory. There are no hard [1]_ dependencies other than the Python standard library. Bottle runs with **Python 2.5+ and 3.x** (using 2to3)

Documentation
===============
The documentation is a work in progress. If you have questions not answered here, please check the :doc:`faq`, file a ticket at bottles issue_tracker_ or send an e-mail to the `mailing list <mailto:bottlepy@googlegroups.com>`_.

.. toctree::
   :maxdepth: 2

   tutorial
   recieps
   faq
   api
   stpl
   changelog
   development

Tutorials and Resources
=======================

.. toctree::
   :maxdepth: 2

   tutorial_app



Licence
==================

Code and documentation are available according to the MIT Licence::

  Copyright (c) 2010, Marcel Hellkamp.

  Permission is hereby granted, free of charge, to any person obtaining a copy
  of this software and associated documentation files (the "Software"), to deal
  in the Software without restriction, including without limitation the rights
  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
  copies of the Software, and to permit persons to whom the Software is
  furnished to do so, subject to the following conditions:

  The above copyright notice and this permission notice shall be included in all
  copies or substantial portions of the Software.

  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
  SOFTWARE.

The Bottle logo however is *NOT* covered by that licence. It is allowed to
use the logo as a link to the bottle homepage or in direct context with
the unmodified library. In all other cases please ask first.

.. rubric:: Footnotes

.. [1] Usage of the template or server adapter classes of course requires the corresponding template or server modules.

