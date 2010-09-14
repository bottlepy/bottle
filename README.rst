Bottle Web Framework
====================

.. image:: http://bottle.paws.de/bottle-logo.png
  :alt: Bottle Logo
  :align: right

Bottle is a fast and simple micro-framework for small web applications. It
offers request dispatching (URL routing) with URL parameter support, templates,
a built-in HTTP Server and adapters for many third party WSGI/HTTP-server and
template engines - all in a single file and with no dependencies other than the
Python Standard Library.

Homepage and documentation: http://bottle.paws.de/


Installation and Dependencies
-----------------------------

Install bottle with ``pip install bottle`` or just `download bottle.py <http://pypi.python.org/pypi/bottle>`_ and place it in your project directory. There are no (hard) dependencies other than the Python Standard Library.


Example
-------

::

    from bottle import route, run

    @route('/hello/:name')
    def hello(name):
        return '<h1>Hello %s!</h1>' % name.title()

    run(host='localhost', port=8080)


Licence (MIT)
-------------

    Copyright (c) 2010, Marcel Hellkamp.

    Permission is hereby granted, free of charge, to any person obtaining a copy
    of this software and associated documentation files (the "Software"), to deal
    in the Software without restriction, including without limitation the rights
    to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
    copies of the Software, and to permit persons to whom the Software is
    furnished to do so, subject to the following conditions:

    The above copyright notice and this permission notice shall be included in
    all copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
    AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
    OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
    THE SOFTWARE.
