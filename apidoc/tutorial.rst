.. module:: bottle

.. _Apache Server:
.. _Apache: http://www.apache.org/
.. _cherrypy: http://www.cherrypy.org/
.. _decorator: http://docs.python.org/glossary.html#term-decorator
.. _fapws3: http://github.com/william-os4y/fapws3
.. _flup: http://trac.saddi.com/flup
.. _http_code: http://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html
.. _http_method: http://www.w3.org/Protocols/rfc2616/rfc2616-sec9.html
.. _json: http://de.wikipedia.org/wiki/JavaScript_Object_Notation
.. _lighttpd: http://www.lighttpd.net/
.. _mako: http://www.makotemplates.org/
.. _mod_wsgi: http://code.google.com/p/modwsgi/
.. _Paste: http://pythonpaste.org/
.. _Pound: http://www.apsis.ch/pound/
.. _`WSGI Specification`: http://www.wsgi.org/wsgi/
.. _issue: http://github.com/defnull/bottle/issues
.. _Python: http://python.org/
.. _SimpleCookie: http://docs.python.org/library/cookie.html#morsel-objects
.. _testing: http://github.com/defnull/bottle/raw/master/bottle.py

========
Tutorial
========

This tutorial introduces you to the concepts and features of the Bottle web framework. If you have questions not answered here, please check the :doc:`faq` page, file a ticket at the issue_ tracker or send an e-mail to the `mailing list <mailto:bottlepy@googlegroups.com>`_.

.. note::

    This is a copy&paste from the old docs and a work in progress. Handle with care :)

.. rubric:: A quick overview:

* :ref:`tutorial-routing`: Web development starts with binding URLs to code. This section tells you how to do it.
* :ref:`tutorial-output`: You have to return something to the Browser. Bottle makes it easy for you, supporting more than just plain strings.
* :ref:`tutorial-request`: Each client request carries a lot of information. HTTP-headers, form data and cookies to name just three. Here is how to use them.
* :ref:`tutorial-templates`: You don't want to write HTML within your python code, do you? Template separate code from presentation.
* :ref:`tutorial-debugging`: These tools and features will help you during development.
* :ref:`tutorial-deployment`: Get it up and running.



Getting started
===================

Bottle has no dependencies, so all you need is Python_ (2.5 up to 3.x should work fine) and the :ref:`bottle module <download>` file. Lets start with a very basic "Hello World" example::

    from bottle import route, run
    
    @route('/hello')
    def hello():
        return "Hello World!"
    
    run(host='localhost', port=8080)

Whats happening here?

1. First we import some bottle components. The :func:`route` decorator and the :func:`run` function. 
2. The :func:`route` :term:`decorator` is used do bind a piece of code to an URL. In this example we want to answer requests to the ``/hello`` URL.
3. This function is the :term:`handler function` or :term:`callback` for the ``/hello`` route. It is called every time someone requests the ``/hello`` URL and is responsable for generating the page content.
4. In this exmaple we simply return a string to the browser.
5. Now it is time to start the actual HTTP server. The default is a development server running on 'localhost' port 8080 and serving requests until you hit :kbd:`Control-c`.

This is it. Run this script, visit http://localhost:8080/hello and you will see "Hello World!" in your Browser. Of cause this is a very simple example, but it shows the basic concept of how applications are build with bottle. Continue reading and you'll see what else is possible.

.. rubric:: The Application Object

Several functions and decorators such as :func:`route` or :func:`run` rely on a global application object to store routes, callbacks and configuration. This makes writing small application easy, but can lead to problems in more complex scenarios. If you prefer a more explicit way to define your application and don't mind the extra typing, you can create your own concealed application object and use that instead of the global one::

    from bottle import Bottle, run

    myapp = Bottle()
    
    @myapp.route('/hello')
    def hello():
        return "Hello World!"
    
    run(app=myapp, host='localhost', port=8080)

This tutorial uses the global-application syntax for the sake of simplicity. Just keep in mind that you have a choice. The object-oriented approach is further described in the :ref:`tutorial-appobject` section.



.. _tutorial-routing:

Routing
==============================================================================

As you have learned before, *routes* are used to map URLs to callback functions. These functions are executed on every request that matches the route and their return value is returned to the browser. You can add any number of routes to a callback using the :func:`route` decorator.

::

    from bottle import route
    
    @route('/')
    @route('/index.html')
    def index():
        return "<a href='/hello'>Go to Hello World page</a>"
    
    @route('/hello')
    def hello():
        return "Hello World!"

As you can see, URLs and routes have nothing to do with actual files on the web server. Routes are unique names for your callbacks, nothing more and nothing less. All URLs not covered by a route are answered with a "404 Page not found" error page.



.. _tutorial-dynamic-routes:

Dynamic Routes
------------------------------------------------------------------------------

Bottle has a special syntax to add wildcards to a route and allow a single route to match a wide range of URLs. These *dynamic routes* are often used by blogs or wikis to create nice looking and meaningful URLs such as ``/archive/2010/04/21`` or ``/wiki/Page_Title``. Why? Because `cool URIs don't change <http://www.w3.org/Provider/Style/URI>`_. Let's add a ``:name`` wildcard to our last example::

    @route('/hello/:name')
    def hello(name):
        return "Hello %s!" % name

This dynamic route will match ``/hello/alice`` as well as ``/hello/bob``. Each URL fragment covered by a wildcard is passed to the callback function as a keyword argument so you can use the information in your application.

Normal wildcards match everything up to the next slash. You can add a regular expression to change that::

    @route('/object/:id#[0-9]+#')
    def view_object(id):
        return "Object ID: %d" % int(id)

As you can see, the keyword argument contains a string even if the wildcard is configured to only match digits. You have to explicitly cast it into an integer if you need to.

HTTP Request Methods
------------------------------------------------------------------------------

.. __: http_method_

The HTTP protocol defines several `request methods`__ (sometimes referred to as "verbs") for different tasks. GET is the default for all routes with no other method specified. These routes will match GET requests only. To handle other methods such as POST, PUT or DELETE, you may add a ``method`` keyword argument to the :func:`route` decorator or use one of the four alternative decorators: :func:`get`, :func:`post`, :func:`put` or :func:`delete`.

The POST method is commonly used for HTML form submission. This example shows how to handle a login form using POST::

    from bottle import get, post, request

    #@route('/login')
    @get('/login')
    def login_form():
        return '''<form method="POST">
                    <input name="name"     type="text" />
                    <input name="password" type="password" />
                  </from>'''

    #@route('/login', method='POST')
    @post('/login')
    def login_submit():
        name     = request.forms.get('name')
        password = request.forms.get('password')
        if check_login(name, password):
            return "<p>Your login was correct</p>"
        else:
            return "<p>Login failed</p>"

In this example the ``/login`` URL is bound to two distinct callbacks, one for GET requests and another for POST requests. The first one displays a HTML form to the user. The second callback is invoked on a form submission and checks the login credentials the user entered into the form. The use of :attr:`Request.forms` is further described in the :ref:`tutorial-request` section. 

.. rubric:: Automatic Fallbacks

The special HEAD method is used to ask for the response identical to the one that would correspond to a GET request, but without the response body. This is useful for retrieving meta-information about a resource without having to download the entire document. Bottle handles these requests automatically by falling back to the corresponding GET route and cutting off the request body, if present. You don't have to specify any HEAD routes yourself.

Additionally, the non-standard ANY method works as a low priority fallback: Routes that listen to ANY will match requests regardless of their HTTP method but only if no other more specific route is defined. This is helpful for *proxy-routes* that redirect requests to more specific sub-applications.

To sum it up: HEAD requests fall back to GET routes and all requests fall back to ANY routes, but only if there is no matching route for the original request method. It's as simple as that.

Routing Static Files
------------------------------------------------------------------------------

Static files such as images or css files are not served automatically. You have to add a route and a callback to control which files get served and where to find them::

  from bottle import static_file
  @route('/static/:filename')
  def server_static(filename):
      return static_file(filename, root='/path/to/your/static/files')

The :func:`static_file` function is a helper to serve files in a save and convenient way (see :ref:`tutorial-static-files`). This example is limited to files directly within the ``/path/to/your/static/files`` directory because the ``:filename`` wildcard won't match a path with a slash in it. To serve files in subdirectories too, we can loosen the wildcard a bit::

  @route('/static/:path#.+#')
  def server_static(path):
      return static_file(path, root='/path/to/your/static/files')

Be carefull when specifying a relative root-path such as ``root='./static/files'``. The working directory (``./``) and the project directory are not always the same.

Error Pages
------------------------------------------------------------------------------

If anything goes wrong, Bottle displays an informative but fairly booring error page. You can override the default error pages using the :func:`error` decorator. It works similar to the :func:`route` decorator, but expects an HTTP status code instead of a route::

  @error(404)
  def error404(error):
      return 'Nothing here, sorry'

The ``error`` parameter passed to the error handler is an instance of :exc:`HTTPError`.




.. _tutorial-output:

Generating content
==============================================================================

In pure WSGI, the range of types you may return from your application is very limited. Applications must return an iterable yielding byte strings. You may return a string (because strings are iterable) but this causes most servers to transmit your content char by char. Unicode strings are not allowed at all. This is not very practical.

Bottle is much more flexible and supports a wide range of types. It even adds a ``Content-Length`` header if possible and encodes unicode automatically, so you don't have to. What follows is a list of data types you may return from your application callbacks and a short description of how these are handled by the framework:

Dictionaries
    As I have already mentioned above, Python dictionaries (or subclasses thereof) are automatically transformed into JSON strings and returned to the browser with the ``Content-Type`` header set to ``application/json``. This makes it easy to implement json-bases APIs. Data formats other than json are supported too. See the :ref:`tutorial-output-filter` to learn more.

Empty Strings, ``False``, ``None`` or other non-true values:
    These produce an empty output with ``Content-Length`` header set to 0. 

Unicode strings
    Unicode strings (or iterables yielding unicode strings) are automatically encoded with the codec specified in the ``Content-Type`` header (utf8 by default) and then treated as normal byte strings (see below).

Byte strings
    Bottle returns strings as a whole (instead of iterating over each char) and adds a ``Content-Length`` header based on the string length. Lists of byte strings are joined first. Other iterables yielding byte strings are not joined because they may grow to big to fit into memory. The ``Content-Length`` header is not set in this case.

Instances of :exc:`HTTPError` or :exc:`HTTPResponse`
    Returning these has the same effect than raising them as an exception. In case of an :exc:`HTTPError`, the error handler are applied. See :ref:`tutorial-errorhandling` for details.

File objects
    Everything that has a ``.read()`` method is treated as a file or file-like object and passed to the ``wsgi.file_wrapper`` callable defined by the WSGI server framework. Some WSGI server implementations can make use of optimized system calls (sendfile) to transmit files more efficiently. In other cases this just iterates over chuncks that fit into memory. Optional headers such as ``Content-Length`` or ``Content-Type`` are *not* set automatically. Use :func:`send_file` if possible. See :ref:`tutorial-static-files` for details.

Iterables and generators
    You are allowed to use ``yield`` within your callbacks or return an iterable, as long as the iterable yields byte strings, unicode strings, :exc:`HTTPError` or :exc:`HTTPResponse` instances. Nested iterables are not supported, sorry. Please note that the HTTP status code and the headers are sent to the browser as soon as the iterable yields its first non-empty value. Changing these later has no effect.
  
The ordering of this list is significant. You may for example return a subclass of :class:`str` with a ``read()`` method. It is still treated as a string instead of a file, because strings are handled first.

.. rubric:: Changing the Default Encoding

Bottle uses the `charset` parameter of the ``Content-Type`` header to decide how to encode unicode strings. This header defaults to ``text/html; charset=UTF8`` and can be changed using the :attr:`Response.content_type` attribute or by setting the :attr:`Response.charset` attribute directly. (The :class:`Response` object is described in the section: :ref:`tutorial-response`)::

    from bottle import response
    @route('/iso')
    def get_iso():
        response.charset = 'ISO-8859-15'
        return u'This will be sent with ISO-8859-15 encoding.'

    @route('/latin9')
    def get_latin():
        response.content_type = 'text/html; charset=latin9'
        return u'ISO-8859-15 is also known as latin9.'

In some rare cases the Python encoding names differ from the names supported by the HTTP specification. Then, you have to do both: First set the :attr:`Response.content_type` header (which is sent to the client unchanged) and then set the :attr:`Response.charset` attribute (which is used to decode unicode).

.. _tutorial-static-files:

Static Files
--------------------------------------------------------------------------------

You can directly return file objects, but :func:`static_file` is the recommended way to serve static files. It automatically guesses a mime-type, adds a ``Last-Modified`` header, restricts paths to a ``root`` directory for security reasons and generates appropriate error responses (401 on permission errors, 404 on missing files). It even supports the ``If-Modified-Since`` header and eventually generates a ``304 Not modified`` response. You can pass a custom mimetype to disable mimetype guessing.

::

    from bottle import static_file
    @route('/images/:filename#.*\.png#')
    def send_image(filename):
        return static_file(filename, root='/path/to/image/files', mimetype='image/png')
    
    @route('/static/:filename')
    def send_static(filename):
        return static_file(filename, root='/path/to/static/files')

You can raise the return value of :func:`static_file` as an exception if you really need to.

.. rubric:: Forced Download

Most browsers try to open downloaded files if the MIME type is known and assigned to an application (e.g. PDF files). If this is not what you want, you can force a download-dialog and even suggest a filename to the user::

    @route('/download/:filename')
    def download(filename):
        return static_file(filename, root='/path/to/static/files', download=filename)

If the ``download`` parameter is just ``True``, the original filename is used.

.. _tutorial-error:

HTTP Errors and Redirects
--------------------------------------------------------------------------------

The :func:`abort` function is a shortcut for generating HTTP error pages.

::

    from bottle import route, abort
    @route('/restricted')
    def restricted():
        abort(401, "Sorry, access denied.")

To redirect a client to a different URL, you can send a ``303 See Other`` response with the ``Location`` header set to the new URL. :func:`redirect` does that for you::

    from bottle import redirect
    @route('/wrong/url')
    def wrong():
        redirect("/right/url")

You may provide a different HTTP status code as a second parameter.

.. note::
    Both functions will interrupt your callback code by raising an :exc:`HTTPError` exception.

.. rubric:: Other Exceptions

All exceptions other than :exc:`HTTPResponse` or :exc:`HTTPError` will result in a ``500 Internal Server Error`` response, so they won't crash your WSGI server. You can turn off this behaviour to handle exceptions in your middleware by setting ``bottle.app().catchall`` to ``False``.


.. _tutorial-response:

The :class:`Response` Object
--------------------------------------------------------------------------------

Response meta-data such as the HTTP status code, response header and cookies are stored in an object called :data:`response` up to the point where they are transmitted to the browser. You can manipulate these meta-data directly or use the predefined helper methods to do so. The full API and feature list is described in the API section (see :class:`Response`), but the most common use cases and features are covered here, too.

.. rubric:: Status Code

The `HTTP status code <http_code>`_ controls the behaviour of the browser and defaults to ``200 OK``. In most scenarios you won't need to set the :attr:`Response.status` attribute manually, but use the :func:`abort` helper or return an :exc:`HTTPResponse` instance with the appropriate status code. Any integer is allowed but only the codes defined by the `HTTP specification <http_code>`_ will have an effect other than confusing the browser and breaking standards.

.. rubric:: Response Header

Add values to the :attr:`Response.headers` dictionary to add or change response headers. Note that the keys are case-insensitive.

::
  
  @route('/wiki/:page')
  def wiki(page):
      response.headers['Content-Language'] = 'en'
      return get_wiki_page(page)

.. _tutorial-secure-cookies:

Cookies
-------------------------------------------------------------------------------

TODO

.. rubric:: Secure Cookies

TODO








.. _tutorial-request:

Accessing Request Data
==============================================================================

Bottle provides access to HTTP related meta-data such as cookies, headers and POST form data through a global ``request`` object. This object always contains information about the *current* request, as long as it is accessed from within a callback function. This works even in multi-threaded environments where multiple requests are handled at the same time. For details on how a global object can be thread-save, see :doc:`contextlocal`.

.. note::
  Bottle stores most of the parsed HTTP meta-data in :class:`MultiDict` instances. These behave like normal dictionaries but are able to store multiple values per key. The standard dictionary access methods will only return a single value. Use the :meth:`MultiDict.getall` method do receive a (possibly empty) list of all values for a specific key. The :class:`HeaderDict` class inherits from :class:`MultiDict` and  additionally uses case insensitive keys. 

The full API and feature list is described in the API section (see :class:`Request`), but the most common use cases and features are covered here, too.

.. rubric:: HTTP Header

Header are stored in :attr:`Request.header`. The attribute is an instance of :class:`HeaderDict` which is basically a dictionary with case-insensitive keys::

  from bottle import route, request
  @route('/is_ajax')
  def is_ajax():
      if request.header.get('X-Requested-With') == 'XMLHttpRequest':
          return 'This is an AJAX request'
      else:
          return 'This is a normal request'

.. rubric:: Cookies

Cookies are stored in :attr:`Request.COOKIES` as a normal dictionary. The :meth:`Request.get_cookie` method allows access to :ref:`tutorial-secure-cookies` as described in a separate section. This example shows a simple cookie-based view counter::

  from bottle import route, request, response
  @route('/counter')
  def counter():
      count = int( request.COOKIES.get('counter', '0') ) + 1
      count += 1
      response.set_cookie('counter', str(count))
      return 'You visited this page %d times' % count


.. rubric:: Query Strings

The query string (as in ``/forum?id=1&page=5``) is commonly used to transmit a small number of key/value pairs to the server. You can use the :attr:`Request.GET` dictionary to access these values and the :attr:`Request.query_string` attribute to get the whole string.

::

  from bottle import route, request, response
  @route('/forum')
  def display_forum():
      forum_id = request.GET.get('id')
      page = request.GET.get('page', '1')
      return 'Forum ID: %s (page %s)' % (forum_id, page)


.. rubric:: POST Form Data and File Uploads

The request body of POST and PUT requests may contain form data encoded in various formats. Use the :attr:`Request.forms` attribute (a :class:`MultiDict`) to access normal POST form fields. File uploads are stored separately in :attr:`Request.files` as :class:`cgi.FieldStorage` instances. The :attr:`Request.body` attribute holds a file object with the raw body data.

Here is an example for a simple file upload form:

.. code-block:: html

    <form action="/upload" method="post" enctype="multipart/form-data">
      <input type="text" name="name" />
      <input type="file" name="data" />
    </form>

::

    from bottle import route, request
    @route('/upload', method='POST')
    def do_upload():
        name = request.forms.get('name')
        data = request.files.get('data')
        if name and data:
            raw = data.file.read() # This is dangerous for big files
            filename = data.filename
            return "Hello %s! Your uploaded %s (%d bytes)." % (name, filename, len(raw))
        return "You missed a field."


.. rubric:: WSGI environment

The :class:`Request` object stores the WSGI environment dictionary in :attr:`Request.environ` and allows dict-like access to its values. See the `WSGI specification`_ for details. 

::

  @route('/my_ip')
  def show_ip():
      ip = request.environ.get('REMOTE_ADDR')
      # or ip = request.get('REMOTE_ADDR')
      # or ip = request['REMOTE_ADDR']
      return "Your IP is: %s" % ip












.. _tutorial-templates:

Templates
================================================================================

Bottle comes with a fast and powerful build-in template engine called :doc:`stpl`. To render a template you can use the :func:`template` function or the :func:`view` decorator. All you have to do is to provide the name of the template and the variables you want to pass to the template as keyword arguments. Here’s a simple example of how to render a template::

    @route('/hello')
    @route('/hello/:name')
    def hello(name='World'):
        return template('hello_template', name=name)

This will load the template file ``hello_template.tpl`` and render it with the ``name`` variable set. Bottle will look for templates in the ``./views/`` folder or any folder specified in the ``bottle.TEMPLATE_PATH`` list.

The :func:`view` decorator allows you to return a dictionary with the template variables instead of calling :func:`template`::

    @route('/hello')
    @route('/hello/:name')
    @view('hello_template')
    def hello(name='World'):
        return dict(name=name)

.. rubric:: Syntax

.. highlight:: html+django

The template syntax is a very thin layer around the Python language. It's main purpose is to ensure correct indention of blocks, so you can format your template without worrying about indentions. Follow the link for a full syntax description: :doc:`stpl`

Here is an example template::

    %if name == 'World':
        <h1>Hello {{name}}!</h1>
        <p>This is a test.</p>
    %else:
        <h1>Hello {{name.title()}}!</h1>
        <p>How are you?</p>
    %end

.. rubric:: Caching

Templates are cached in memory after compilation. Modifications made to the template files will have no affect until you clear the template cache. Call ``bottle.TEMPLATES.clear()`` to do so. Caching is disabled in debug mode.






.. highlight:: python

.. _tutorial-debugging:

Development
================================================================================

Bottle has two features that may be helpfull during development.



Debug Mode
--------------------------------------------------------------------------------

In debug mode, bottle is much more verbose and tries to help you finding 
bugs. You should never use debug mode in production environments.

.. highlight:: python

::

    import bottle
    bottle.debug(True)

This does the following:

* Exceptions will print a stacktrace
* Error pages will contain that stacktrace
* Templates will not be cached.



Auto Reloading
--------------------------------------------------------------------------------

During development, you have to restart the server a lot to test your 
recent changes. The auto reloader can do this for you. Every time you 
edit a module file, the reloader restarts the server process and loads 
the newest version of your code. 

::

    from bottle import run
    run(reloader=True)

How it works: The main process will not start a server, but spawn a new 
child process using the same command line agruments used to start the 
main process. All module level code is executed at least twice! Be 
carefull.

The child process will have ``os.environ['BOTTLE_CHILD']`` set to ``true`` 
and start as a normal non-reloading app server. As soon as any of the 
loaded modules changes, the child process is terminated and respawned by 
the main process. Changes in template files will not trigger a reload. 
Please use debug mode to deactivate template caching.

The reloading depends on the ability to stop the child process. If you are
running on Windows or any other operating system not supporting 
``signal.SIGINT`` (which raises ``KeyboardInterrupt`` in Python), 
``signal.SIGTERM`` is used to kill the child. Note that exit handlers and 
finally clauses, etc., are not executed after a ``SIGTERM``.


.. _tutorial-deployment:

Deployment
================================================================================

Bottle uses the build-in ``wsgiref.SimpleServer`` by default. This non-threading
HTTP server is perfectly fine for development and early production,
but may become a performance bottleneck when server load increases.

There are three ways to eliminate this bottleneck:

* Use a multi-threaded server adapter
* Spread the load between multiple bottle instances
* Do both



Multi-Threaded Server
--------------------------------------------------------------------------------

The easiest way to increase performance is to install a multi-threaded and
WSGI-capable HTTP server like Paste_, flup_, cherrypy_
or fapws3_ and use the corresponding bottle server-adapter.

::

    from bottle import PasteServer, FlupServer, FapwsServer, CherryPyServer
    bottle.run(server=PasteServer) # Example
    
If bottle is missing an adapter for your favorite server or you want to tweak
the server settings, you may want to manually set up your HTTP server and use
``bottle.default_app()`` to access your WSGI application.

::

    def run_custom_paste_server(self, host, port):
        myapp = bottle.default_app()
        from paste import httpserver
        httpserver.serve(myapp, host=host, port=port)



Multiple Server Processes
--------------------------------------------------------------------------------

A single Python process can only utilise one CPU at a time, even if 
there are more CPU cores available. The trick is to balance the load 
between multiple independent Python processes to utilise all of your 
CPU cores.

Instead of a single Bottle application server, you start one instances 
of your server for each CPU core available using different local port 
(localhost:8080, 8081, 8082, ...). Then a high performance load 
balancer acts as a reverse proxy and forwards each new requests to 
a random Bottle processes, spreading the load between all available 
backed server instances. This way you can use all of your CPU cores and 
even spread out the load between different physical servers.

But there are a few drawbacks:

* You can't easily share data between multiple Python processes.
* It takes a lot of memory to run several copies of Python and Bottle at the same time.

One of the fastest load balancer available is Pound_ but most common web servers have a proxy-module that can do the work just fine.

I'll add examples for lighttpd_ and 
Apache_ web servers soon.

Using WSGI and Middleware
--------------------------------------------------------------------------------

A call to `bottle.default_app()` returns your WSGI application. After applying as many WSGI middleware modules as you like, you can tell 
`bottle.run()` to use your wrapped application, instead of the default one.

::

    from bottle import default_app, run
    app = default_app()
    newapp = YourMiddleware(app)
    run(app=newapp)

.. rubric: How default_app() works

Bottle creates a single instance of `bottle.Bottle()` and uses it as a default for most of the modul-level decorators and the `bottle.run()` routine. 
`bottle.default_app()` returns (or changes) this default. You may, however, create your own instances of `bottle.Bottle()`.

::

    from bottle import Bottle, run
    mybottle = Bottle()
    @mybottle.route('/')
    def index():
      return 'default_app'
    run(app=mybottle)

Apache mod_wsgi
--------------------------------------------------------------------------------

Instead of running your own HTTP server from within Bottle, you can 
attach Bottle applications to an `Apache server`_ using 
mod_wsgi_ and Bottle's WSGI interface.

All you need is an ``app.wsgi`` file that provides an 
``application`` object. This object is used by mod_wsgi to start your 
application and should be a WSGI conform Python callable.

File ``/var/www/yourapp/app.wsgi``::

    # Change working directory so relative paths (and template lookup) work again
    os.chdir(os.path.dirname(__file__))
    
    import bottle
    # ... add or import your bottle app code here ...
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

I didn't test this myself but several Bottle users reported that this 
works just fine::

    import bottle
    from google.appengine.ext.webapp import util 
    # ... add or import your bottle app code here ...
    # Do NOT use bottle.run() with AppEngine
    util.run_wsgi_app(bottle.default_app())




Good old CGI
--------------------------------------------------------------------------------

CGI is slow as hell, but it works::

    import bottle
    # ... add or import your bottle app code here ...
    bottle.run(server=bottle.CGIServer)





.. _tutorial-glossary:

Glossary
========

.. glossary::

   callback
      Programmer code that is to be called when some external action happens.
      In the context of web frameworks, the mapping between URL paths and 
      application code is often achieved by specifying a callback function
      for each URL.

   decorator
      A function returning another function, usually applied as a function transformation using the ``@decorator`` syntax. See `python documentation for function definition  <http://docs.python.org/reference/compound_stmts.html#function>`_ for more about decorators.

   environ
      A structure where information about all documents under the root is
      saved, and used for cross-referencing.  The environment is pickled
      after the parsing stage, so that successive runs only need to read
      and parse new and changed documents.

   handler function
      A function to handle some specific event or situation. In a web
      framework, the application is developed by attaching a handler function
      as callback for each specific URL composing the application.

   secure cookie
      bottle creates signed cookies with objects that can be pickled. A secure
      cookie will be created automatically when a type that is not a string is
      use as value in :meth:`request.set_cookie` and bottle's config
      includes a `securecookie.key` entry with a salt.

   source directory
      The directory which, including its subdirectories, contains all
      source files for one Sphinx project.

