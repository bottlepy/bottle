.. Bottle documentation master file, created by
   sphinx-quickstart on Thu Feb 18 13:47:50 2010.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

.. highlight:: python


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


============================
Bottle: Python Web Framework
============================

Bottle is a fast, simple and lightweight WSGI_ micro web-framework for Python_ with no external dependencies and packed into a single file.

.. rubric:: Core Features

* **Routes:** Mapping URLs to code with a simple but powerful pattern syntax.
* **Templates:** Fast build-in template engine and support for mako_, jinja2_ and cheetah_ templates.
* **Server:** Build-in HTTP development server and support for paste_, fapws3_, flup_, cherrypy_ or any other WSGI_ capable server.
* **Plug&Run:** All in a single file and no dependencies other than the Python standard library.

.. rubric:: Download

.. _download:

You can install the latest stable release with ``easy_install -U bottle`` or just download the newest testing_ version into your project directory. There are no hard [1]_ dependencies other than the Python standard library. Bottle runs with **Python 2.5+ and 3.x** (using 2to3)

.. rubric:: "Hello World" in a bottle

This is a minimal bottle application serving a single URL::

  from bottle import route, run
  @route('/')
  def index():
      return 'Hello World!'
  run(host='localhost', port=8080)

Documentation
===============
This documentation is a work in progress. If you have questions not answered here, please check the :doc:`faq`, then file a ticket at bottles issue_tracker_ or send an e-mail to the `mailing list <mailto:bottlepy@googlegroups.com>`_.

.. toctree::
   :maxdepth: 2

   tutorial
   tutorial_app
   faq
   api
   stpl
   download
   development

Licence
==================

Copyright (c) 2009, Marcel Hellkamp.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

.. rubric:: Footnotes

.. [1] Usage of the template or server adapter classes of course requires the corresponding template or server modules.

