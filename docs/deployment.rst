.. _flup: http://trac.saddi.com/flup
.. _gae: http://code.google.com/appengine/docs/python/overview.html
.. _wsgiref: http://docs.python.org/library/wsgiref.html
.. _cherrypy: http://www.cherrypy.org/
.. _paste: http://pythonpaste.org/
.. _rocket: http://pypi.python.org/pypi/rocket
.. _gunicorn: http://pypi.python.org/pypi/gunicorn
.. _fapws3: http://www.fapws.org/
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



.. _tutorial-deployment:

================================================================================
Deployment
================================================================================

The bottle :func:`run` function, when called without any parameters, starts a local development server on port 8080. You can access and test your application via http://localhost:8080/ if you are on the same host.

To get your application available to the outside world, specify the IP of the interface the server should listen to (e.g. ``run(host='192.168.0.1')``) or let the server listen to all interfaces at once (e.g. ``run(host='0.0.0.0')``). The listening port can be changed in a similar way, but you need root or admin rights to choose a port below 1024. Port 80 is the standard for HTTP servers::

  run(host='0.0.0.0', port=80) # Listen to HTTP requests on all interfaces

Server Options
================================================================================

The built-in default server is based on `wsgiref WSGIServer <http://docs.python.org/library/wsgiref.html#module-wsgiref.simple_server>`_. This non-threading HTTP server is perfectly fine for development and early production, but may become a performance bottleneck when server load increases. There are three ways to eliminate this bottleneck:

* Use a different server that is either multi-threaded or asynchronous.
* Start multiple server processes and spread the load with a load-balancer.
* Do both.

**Multi-threaded** servers are the 'classic' way to do it. They are very robust, reasonably fast and easy to manage. As a drawback, they can only handle a limited number of connections at the same time and utilize only one CPU core due to the "Global Interpreter Lock" (GIL) of the Python runtime. This does not hurt most applications, they are waiting for network IO most of the time anyway, but may slow down CPU intensive tasks (e.g. image processing).

**Asynchronous** servers are very fast, can handle a virtually unlimited number of concurrent connections and are easy to manage. To take full advantage of their potential, you need to design your application accordingly and understand the concepts of the specific server.

**Multi-processing** (forking) servers are not limited by the GIL and utilize more than one CPU core, but make communication between server instances more expensive. You need a database or external message query to share state between processes, or design your application so that it does not need any shared state. The setup is also a bit more complicated, but there are good tutorials available. 

Switching the Server Backend
================================================================================

The easiest way to increase performance is to install a multi-threaded server library like paste_ or cherrypy_ and tell Bottle to use that instead of the single-threaded default server::

    bottle.run(server='paste')

Bottle ships with a lot of ready-to-use adapters for the most common WSGI servers and automates the setup process. Here is an incomplete list:

========  ============  ======================================================
Name      Homepage      Description
========  ============  ======================================================
cgi                     Run as CGI script
flup      flup_         Run as FastCGI process
gae       gae_          Helper for Google App Engine deployments
wsgiref   wsgiref_      Single-threaded default server
cherrypy  cherrypy_     Multi-threaded and very stable
paste     paste_        Multi-threaded, stable, tried and tested
rocket    rocket_       Multi-threaded
waitress  waitress_     Multi-threaded, poweres Pyramid
gunicorn  gunicorn_     Pre-forked, partly written in C
eventlet  eventlet_     Asynchronous framework with WSGI support.
gevent    gevent_       Asynchronous (greenlets)
diesel    diesel_       Asynchronous (greenlets)
fapws3    fapws3_       Asynchronous (network side only), written in C
tornado   tornado_      Asynchronous, powers some parts of Facebook
twisted   twisted_      Asynchronous, well tested but... twisted
meinheld  meinheld_     Asynchronous, partly written in C
bjoern    bjoern_       Asynchronous, very fast and written in C
auto                    Automatically selects an available server adapter
========  ============  ======================================================

The full list is available through :data:`server_names`.

If there is no adapter for your favorite server or if you need more control over the server setup, you may want to start the server manually. Refer to the server documentation on how to run WSGI applications. Here is an example for paste_::

    application = bottle.default_app()
    from paste import httpserver
    httpserver.serve(application, host='0.0.0.0', port=80)



Apache mod_wsgi
--------------------------------------------------------------------------------

Instead of running your own HTTP server from within Bottle, you can attach Bottle applications to an `Apache server <apache>`_ using mod_wsgi_.

All you need is an ``app.wsgi`` file that provides an ``application`` object. This object is used by mod_wsgi to start your application and should be a WSGI-compatible Python callable.

File ``/var/www/yourapp/app.wsgi``::

    # Change working directory so relative paths (and template lookup) work again
    os.chdir(os.path.dirname(__file__))
    
    import bottle
    # ... build or import your bottle application here ...
    # Do NOT use bottle.run() with mod_wsgi
    application = bottle.default_app()

The Apache configuration may look like this::

    <VirtualHost *>
        ServerName example.com
        
        WSGIDaemonProcess yourapp user=www-data group=www-data processes=1 threads=5
        WSGIScriptAlias / /var/www/yourapp/app.wsgi
        
        <Directory /var/www/yourapp>
            WSGIProcessGroup yourapp
            WSGIApplicationGroup %{GLOBAL}
            Order deny,allow
            Allow from all
        </Directory>
    </VirtualHost>



Google AppEngine
--------------------------------------------------------------------------------

.. versionadded:: 0.9

New App Engine applications using the Python 2.7 runtime environment support any WSGI application and should be configured to use the Bottle application object directly. For example suppose your application's main module is ``myapp.py``::

    import bottle

    @bottle.route('/')
    def home():
        return '<html><head></head><body>Hello world!</body></html>'

    app = bottle.default_app()

Then you can configure App Engine's ``app.yaml`` to use the ``app`` object like so::

    application: myapp
    version: 1
    runtime: python27
    api_version: 1

    handlers:
    - url: /.*
      script: myapp.app

Bottle also provides a ``gae`` server adapter for legacy App Engine applications using the Python 2.5 runtime environment. It works similar to the ``cgi`` adapter in that it does not start a new HTTP server, but prepares and optimizes your application for Google App Engine and makes sure it conforms to their API::

    bottle.run(server='gae') # No need for a host or port setting.

It is always a good idea to let GAE serve static files directly. Here is example for a working  ``app.yaml`` (using the legacy Python 2.5 runtime environment)::

    application: myapp
    version: 1
    runtime: python
    api_version: 1

    handlers:
    - url: /static
      static_dir: static

    - url: /.*
      script: myapp.py


Load Balancer (Manual Setup)
--------------------------------------------------------------------------------

A single Python process can utilize only one CPU at a time, even if there are more CPU cores available. The trick is to balance the load between multiple independent Python processes to utilize all of your CPU cores.

Instead of a single Bottle application server, you start one instance for each CPU core available using different local port (localhost:8080, 8081, 8082, ...). You can choose any server adapter you want, even asynchronous ones. Then a high performance load balancer acts as a reverse proxy and forwards each new requests to a random port, spreading the load between all available back-ends. This way you can use all of your CPU cores and even spread out the load between different physical servers.

One of the fastest load balancers available is Pound_ but most common web servers have a proxy-module that can do the work just fine.

Pound example::

    ListenHTTP
        Address 0.0.0.0
        Port    80

        Service
            BackEnd
                Address 127.0.0.1
                Port    8080
            End
            BackEnd
                Address 127.0.0.1
                Port    8081
            End
        End
    End

Apache example::

    <Proxy balancer://mycluster>
    BalancerMember http://127.0.0.1:8080
    BalancerMember http://127.0.0.1:8081
    </Proxy>
    ProxyPass / balancer://mycluster 

Lighttpd example::

    server.modules += ( "mod_proxy" )
    proxy.server = (
        "" => (
            "wsgi1" => ( "host" => "127.0.0.1", "port" => 8080 ),
            "wsgi2" => ( "host" => "127.0.0.1", "port" => 8081 )
        )
    )


Good old CGI
================================================================================

A CGI server starts a new process for each request. This adds a lot of overhead but is sometimes the only option, especially on cheap hosting packages. The `cgi` server adapter does not actually start a CGI server, but transforms your bottle application into a valid CGI application::

    bottle.run(server='cgi')



