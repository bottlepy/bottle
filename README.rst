Bottle Web Framework
====================

.. image:: http://bottlepy.org/docs/dev/_static/logo_nav.png
  :alt: Bottle Logo
  :align: right

Bottle is a fast and simple micro-framework for small web applications. It
offers request dispatching (URL routing) with URL parameter support, templates,
a built-in HTTP Server and adapters for many third party WSGI/HTTP-server and
template engines - all in a single file and with no dependencies other than the
Python Standard Library.

Homepage and documentation: http://bottlepy.org/
License: MIT (see LICENSE)

Installation and Dependencies
-----------------------------

Install bottle with ``pip install bottle`` or just `download bottle.py <http://pypi.python.org/pypi/bottle>`_ and place it in your project directory. There are no (hard) dependencies other than the Python Standard Library.

Or, for the truly lazy:

::

    curl https://raw.github.com/defnull/bottle/release/bottle.py -o bottle.py

Example
-------

.. code-block:: python

    from bottle import route, run

    @route('/hello/:name')
    def hello(name):
        return '<h1>Hello %s!</h1>' % name.title()

    run(host='localhost', port=8080)
