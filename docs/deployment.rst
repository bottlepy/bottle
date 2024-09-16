.. highlight:: python
.. currentmodule:: bottle

.. _flup: https://pypi.org/project/flup/
.. _gae: http://code.google.com/appengine/docs/python/overview.html
.. _wsgiref: http://docs.python.org/library/wsgiref.html
.. _cherrypy: https://cherrypy.dev/
.. _paste: https://pythonpaste.readthedocs.io/
.. _gunicorn: http://pypi.python.org/pypi/gunicorn
.. _tornado: http://www.tornadoweb.org/
.. _twisted: http://twistedmatrix.com/
.. _diesel: http://dieselweb.org/
.. _meinheld: http://pypi.python.org/pypi/meinheld
.. _bjoern: http://pypi.python.org/pypi/bjoern
.. _gevent: http://www.gevent.org/
.. _eventlet: http://eventlet.net/
.. _waitress: http://readthedocs.org/docs/waitress/en/latest/
.. _apache: http://httpd.apache.org/
.. _mod_wsgi: http://code.google.com/p/modwsgi/
.. _pound: http://www.apsis.ch/pound
.. _nginx: http://nginx.org/
.. _lighttpd: http://www.lighttpd.net/
.. _cherokee: http://cherokee-project.com/
.. _uWSGI: https://uwsgi-docs.readthedocs.io/en/latest/
.. _cheroot: https://cheroot.cherrypy.dev/

.. _tutorial-deployment:

================================================================================
Deployment
================================================================================

The bottle :func:`run` function, when called without any parameters, starts a local development server on port 8080. You can access and test your application via http://localhost:8080/ if you are on the same host.

To get your application available to the outside world, specify the IP the server should listen to (e.g. ``run(host='192.168.0.1')``) or let the server listen to all interfaces at once (e.g. ``run(host='0.0.0.0')``). The listening port can be changed in a similar way, but you need root or admin rights to choose a port below 1024. Port 80 is the standard for HTTP servers::

  # Listen to HTTP on all interfaces
  if __name__ == '__main__':
      run(host='0.0.0.0', port=80)

Scaling for Production
================================================================================

The built-in development server is base on `wsgiref WSGIServer <http://docs.python.org/library/wsgiref.html#module-wsgiref.simple_server>`_, which is a very simple non-threading HTTP server implementation. This is perfectly fine for development, but may become a performance bottleneck when server load increases.

The easiest way to increase performance is to install a multi-threaded server library like cheroot_ or gunicorn_ and tell Bottle to use that instead of the single-threaded wsgiref server::

    run(server='cheroot', ...)   # Pure Python, runs everywhere
    run(server='gunicorn', ...)  # High performance

Or using the ``bottle`` command line interface:

.. code-block:: sh

    python3 -m bottle --server gunicorn [...] mymodule:app

For production deployments gunicorn_ is a really good choice. It comes with its own command line utility that supports a lot more options than bottle. Since :class:`Bottle` instances are WSGI applications, you can tell gunicorn_ (or any other WSGI server) to load your app instead of calling :func:`run` yourself:

.. code-block:: sh

    gunicorn -w 4 mymodule:app

This will start your application with 4 gunicorn workers and sane default settings. For more details and more complete examples, check out `Gunicorn Documentation <https://docs.gunicorn.org/>`_.

Server adapters
------------------------------------------------------------------------------

Bottle ships with a bunch of ready-to-use adapters for the most common WSGI servers so you can try out different server backends easily. You can select a server backend via `run(server='NAME')` or `python3 -m bottle --server NAME`. Here is an incomplete list:

========  ============  ======================================================
Name      Homepage      Description
========  ============  ======================================================
cgi                     Run as CGI script
flup      flup_         Run as FastCGI process
gae       gae_          Helper for Google App Engine deployments
wsgiref   wsgiref_      Single-threaded default server
cherrypy  cherrypy_     Multi-threaded (deprectated))
cheroot   cheroot_      Successor of cheerypy
paste     paste_        Multi-threaded, stable, tried and tested
waitress  waitress_     Multi-threaded, poweres Pyramid
gunicorn  gunicorn_     Pre-forked, partly written in C
eventlet  eventlet_     Asynchronous framework with WSGI support.
gevent    gevent_       Asynchronous (greenlets)
diesel    diesel_       Asynchronous (greenlets)
tornado   tornado_      Asynchronous, powers some parts of Facebook
twisted   twisted_      Asynchronous, well tested but... twisted
meinheld  meinheld_     Asynchronous, partly written in C
bjoern    bjoern_       Asynchronous, very fast and written in C
auto                    Automatically selects the first available server adapter
========  ============  ======================================================

Those adapters are very basic and just for convenience, though. If you need more control over your deployment, refer to the server backend documentation and mount your Bottle application just like any other WSGI application.


WSGI Deployment
------------------------------------------------------------------------------

If there is no adapter for your favorite server or if you need more control over the server setup, you may want to start the server manually. Refer to the server documentation on how to run WSGI applications. Here is an example for cheroot_::

    import cheroot.wsgi
    import mymodule.app

    wsgi_server = cheroot.wsgi.Server(
        bind_addr=('0.0.0.0', 80),
        wsgi_app=mymodule.app
    )

    try:
        wsgi_server.start()
    finally:
        wsgi_server.stop()

