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

This tutorial introduces you to the concepts and features of the Bottle web framework. If you have questions not answered here, please check the :doc:`faq` page, then file a ticket at the issue_ tracker or send an e-mail to the `mailing list <mailto:bottlepy@googlegroups.com>`_.

.. note::

    This is a copy&paste from the old docs and a work in progress. Handle with care :)

.. rubric:: A quick overview:

* :ref:`tutorial-routing`: Web development starts with binding URLs to code. This section tells you how to do it.
* :ref:`tutorial-request`: Each client request carries a lot of information. HTTP-headers, form data and cookies to name just three. Here is how to use them.
* :ref:`tutorial-output`: You have to return something to the Browser. Bottle makes it easy for you, supporting more than just plain strings.
* :ref:`tutorial-templates`: You don't want to write HTML within your python code, do you? Template separate code from presentation.
* :ref:`tutorial-debugging`: These tools and features will help you during development.
* :ref:`tutorial-deployment`: Get it up and running.





Getting started
===================

Bottle has no dependencies, so all you need is Python_ (2.5 up to 3.x should work fine) and the :ref:`bottle module <download>`. Lets start with a very basic "Hello World" example::

    from bottle import route, run
    @route('/hello')
    def hello():
        return "Hello World!"
    run(host='localhost', port=8080)

Run this script, visit http://localhost:8080/hello and you will see "Hello World!" in your Browser. So, what happened here?

1. First we imported some bottle components. The :func:`route` decorator and the :func:`run` function. 
2. The :func:`route` :term:`decorator` is used do bind a piece of code to an URL. In this example we want to answer requests to the ``/hello`` URL.
3. This function will be called every time someone hits the ``/hello`` URL on the web server. It is called a :term:`handler function` or :term:`callback`.
4. The return value of a handler function will be sent back to the Browser.
5. Now it is time to start the actual HTTP server. The default is a development server running on 'localhost' port 8080 and serving requests until you hit :kbd:`Control-c`.





.. _tutorial-routing:

Routing
==============================================================================

Routes are used to map URLs to callback functions that generate the content for that URLs. Bottle has a :func:`route` decorator to do that. You can add any number of routes to a callback.

::

    from bottle import route
    
    @route('/')
    @route('/index.html')
    def index():
        return "<a href='/hello'>Go to Hello World page</a>"
    
    @route('/hello')
    def hello():
        return "Hello World!"

As you can see, URLs and routes have nothing to do with actual files on the web server. Routes are unique names for your callbacks, nothing more and nothing less. Requests to URLs not matching any of the defined routes will result in a 404 HTTP error page.



.. rubric:: HTTP Request Methods

.. __: http_method_

The HTTP protocol defines several `request methods`__ for different tasks. With no method specified, routes will listen to ``GET`` requests only. To handle other methods such as ``POST``, ``PUT`` or ``DELETE``, you have to add a ``method`` keyword argument to the :func:`route` decorator or use one of the alternative decorators: :func:`get()`, :func:`post()`, :func:`put()` or :func:`delete()`.

Here is an example for a route handling ``POST`` requests::

    from bottle import post, request
    @post('/form/submit') # or @route('/form/submit', method='POST')
    def form_submit():
        form_data = request.POST
        do_something_with(form_data)
        return "Done"

In this example we used :attr:`Request.POST` to access form data as described in the :ref:`tutorial-request` section.

The special ``ANY`` method works as a low priority fallback. It matches requests regardless of their HTTP method but only if no other more specific route is installed. Also note that ``HEAD`` requests fall back to ``GET`` routes automatically, so you don't have to specify them explicitly.

To sum it up: ``HEAD`` requests fall back to ``GET`` routes and all requests fall back to ``ANY`` routes, if there is no matching route for the original request method.



.. _tutorial-dynamic-routes:

Dynamic Routes
------------------------------------------------------------------------------

Static routes are fine, but URLs may carry information as well. Let's add a ``:name`` placeholder to our route.

::

    from bottle import route
    @route('/hello/:name')
    def hello(name):
        return "Hello %s!" % name

This dynamic route matches ``/hello/alice`` as well as ``/hello/bob``. In fact, the ``:name`` part will match everything but a slash (``/``), so any name is possible. ``/hello/bob/and/alice`` or ``/hellobob`` won't match. Each part of the URL covered by a placeholder is provided as a keyword argument to your handler callback.

A normal placeholder matches everything up to the next slash. To change that, you can add a regular expression pattern::

    from bottle import route
    @route('/get_object/:id#[0-9]+#')
    def get(id):
        return "Object ID: %d" % int(id)

As you can see, URL parameters remain strings, even if they are configured to only match digits. You have to explicitly cast them into the type you need.






.. _tutorial-request:

The Request Object
==============================================================================

Bottle parses the HTTP request data into a thread-save ``request`` object and provides some useful tools and methods to access this data. Most of the parsing happens on demand, so you won't see any overhead if you don't need the result. Here is a short summary:

* ``request[key]``: A shortcut for ``request.environ[key]``
* ``request.environ``: WSGI environment dictionary. Use this with care.
* ``request.app``: Currently used Bottle instance (same as ``bottle.app()``)
* ``request.method``: HTTP request-method (GET,POST,PUT,DELETE,...).
* ``request.query_string``: HTTP query-string (http://host/path?query_string)
* ``request.path``: Path string that matched the current route.
* ``request.fullpath``: Full path including the ``SCRIPT_NAME`` part.
* ``request.url``: The full URL as requested by the client (including ``http(s)://`` and hostname)
* ``request.input_length`` The Content-Length header (if present) as an integer.
* ``request.header``: HTTP header dictionary.
* ``request.GET``: The parsed content of ``request.query_string`` as a dict. Each value may be a string or a list of strings.
* ``request.POST``: A dict containing parsed form data. Supports URL- and multipart-encoded form data. Each value may be a string, a file or a list of strings or files.
* ``request.COOKIES``: The cookie data as a dict.
* ``request.params``: A dict containing both, ``request.GET`` and ``request.POST`` data.
* ``request.body``: The HTTP body of the request as a buffer object.
* ``request.auth``: HTTP authorisation data as a named tuple. (experimental)
* ``request.get_cookie(key[, default])``: Returns a specific cookie. If it is a :term:`secure cookie` it is decoded. (experimental)



Cookies
------------------------------------------------------------------------------

Bottle stores cookies sent by the client in a dictionary called ``request.COOKIES``. To create new cookies, the method ``response.set_cookie(name, value[, **params])`` is used. It accepts additional parameters as long as they are valid cookie attributes supported by `SimpleCookie`_.

::

    from bottle import response
    response.set_cookie('key','value', path='/', domain='example.com', secure=True, expires=+500, ...)

To set the ``max-age`` attribute use the ``max_age`` name.

TODO: It is possible to store python objects and lists in cookies. This produces signed cookies, which are pickled and unpickled automatically. 



GET and POST values
------------------------------------------------------------------------------

Query strings and/or POST form submissions are parsed into dictionaries and made
available as ``request.GET`` and ``request.POST``. Multiple values per
key are possible, so these dictionaries actually are instances of :class:`MultiDict`
which returns the newest value by default. You can use ``.getall(key)`` to get a
list of all available values for that key.


::

    from bottle import route, request
    @route('/search', method='POST')
    def do_search():
        if 'query' in request.POST:
            return 'You searched for %s.' % request.POST['query'].strip()
        else:
            return "You didn't supply a search query."




File Uploads
------------------------------------------------------------------------------

Bottle handles file uploads similar to normal POST form data. Instead of strings, you will get file-like objects. 

::

    from bottle import route, request
    @route('/upload', method='POST')
    def do_upload():
        datafile = request.POST.get('datafile')
        return datafile.read()

Here is an example HTML Form for file uploads:

.. code-block:: html

    <form action="/upload" method="post" enctype="multipart/form-data">
      <input name="datafile" type="file" />
    </form>





.. _tutorial-output:

Generating content
==============================================================================

The `WSGI specification`_ expects an iterable list of byte strings to be returned by your application and can't handle unicode, dictionaries or exceptions. Bottle automatically tries to convert anything to a WSGI supported type, so you don't have to. The following examples will work with Bottle, but won't work with pure WSGI.




The Response Object
------------------------------------------------------------------------------

TODO

Strings and Unicode
------------------------------------------------------------------------------

Returning strings (bytes) is not a problem. Unicode however needs to be encoded before the webserver can send it to the client. The default encoding is utf-8. If that fits your needs, you can simply return unicode or iterables yielding unicode.

::

    @route('/string')
    def get_string():
        return 'Bottle converts strings to iterables'
    
    @route('/unicode')
    def get_unicode():
        return u'Unicode is encoded with UTF-8 by default'

You can change the encoding by setting :attr:`Response.content_type` to a value containing a ``charset=...`` parameter or by changing :attr:`Response.charset` directly. (The :class:`Response` object is described in the section: :ref:`tutorial-request`)

::

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



File Objects and Streams
--------------------------------------------------------------------------------

Bottle passes everything that has a ``read()`` method (file objects) to the ``wsgi.file_wrapper`` provided by your WSGI server implementation. This wrapper should use optimised system calls (``sendfile`` on UNIX) to transfer the file contents.

::

    @route('/file')
    def get_file():
        return open('some/file.txt','r')



JSON
--------------------------------------------------------------------------------

Even dictionaries are allowed. They are converted to json_ and returned with the ``Content-Type`` header set to ``application/json``. To disable this feature (and pass dicts to your middleware) you can set ``bottle.app().autojson`` to ``False``.

::

    @route('/api/status')
    def api_status():
        return {'status':'online', 'servertime':time.time()}



Static Files
--------------------------------------------------------------------------------

You can directly return file objects, but ``static_file()`` is the recommended way to serve static files. It automatically guesses a mime-type, adds a ``Last-Modified`` header, restricts paths to a ``root`` directory for security reasons and generates appropriate error responses (401 on permission errors, 404 on missing files). It even supports the ``If-Modified-Since`` header and eventually generates a ``304 Not modified`` response. You can pass a custom mimetype to disable mimetype guessing.

::

    from bottle import static_file
    @route('/images/:filename#.*\.png#')
    def send_image(filename):
        return static_file(filename, root='/path/to/image/files', mimetype='image/png')
    
    @route('/static/:filename')
    def send_static(filename):
        return static_file(filename, root='/path/to/static/files')

You can raise the return value of ``static_file()`` as an exception if you really need to. The raised ``HTTPResponse`` exception is handled by the Bottle framework. 



HTTPError, HTTPResponse and Redirects
--------------------------------------------------------------------------------

The ``abort(code[, message])`` function is used to generate [HTTP error pages][http_code].

::

    from bottle import route, redirect, abort
    @route('/restricted')
    def restricted():
        abort(401, "Sorry, access denied.")

To redirect a client to a different URL, you can send a ``303 See Other`` response with the ``Location`` header set to the new URL. ``redirect(url[, code])`` does that for you. You may provide a different HTTP status code as a second parameter.

::

    from bottle import redirect
    @route('/wrong/url')
    def wrong():
        redirect("/right/url")

Both functions interrupt your handler code by raising a ``HTTPError`` exception.

You can return ``HTTPError`` exceptions instead of raising them. This is faster than raising and capturing Exceptions, but does exactly the same.

::

    from bottle import HTTPError
    @route('/denied')
    def denied():
        return HTTPError(401, 'Access denied!')



Exceptions
--------------------------------------------------------------------------------

All exceptions other than ``HTTPResponse`` or ``HTTPError`` will result in a ``500 Internal Server Error`` response, so they won't crash your WSGI server. You can turn off this behaviour to handle exceptions in your middleware by setting ``bottle.app().catchall`` to ``False``.






.. _tutorial-templates:

Templates
================================================================================

Bottle uses its own little template engine by default. You can use a template by
calling ``template(template_name, **template_arguments)`` and returning
the result.

::

    @route('/hello/:name')
    def hello(name):
        return template('hello_template', username=name)

This will load the template ``hello_template.tpl`` with the ``username`` variable set to the URL ``:name`` part and return the result as a string.

.. highlight:: html+django

The ``hello_template.tpl`` file could look like this::

    <h1>Hello {{username}}</h1>
    <p>How are you?</p>



Template search path
--------------------------------------------------------------------------------

The list ``bottle.TEMPLATE_PATH`` is used to map template names to actual 
file names. By default, this list contains ``['./%s.tpl', './views/%s.tpl']``.



Template caching
--------------------------------------------------------------------------------

Templates are cached in memory after compilation. Modifications made to 
the template file will have no affect until you clear the template 
cache. Call ``bottle.TEMPLATES.clear()`` to do so.



Template Syntax
--------------------------------------------------------------------------------

The template syntax is a very thin layer around the Python language. 
It's main purpose is to ensure correct indention of blocks, so you 
can format your template without worrying about indentions. Here is the 
complete syntax description:

* ``%...`` starts a line of python code. You don't have to worry about indentions. Bottle handles that for you.
* ``%end`` closes a Python block opened by ``%if ...``, ``%for ...`` or other block statements. Explicitly closing of blocks is required.
* ``{{...}}`` prints the result of the included python statement.
* ``%include template_name optional_arguments`` allows you to include other templates.
* Every other line is returned as text.

Example::

    %header = 'Test Template'
    %items = [1,2,3,'fly']
    %include http_header title=header, use_js=['jquery.js', 'default.js']
    <h1>{{header.title()}}</h1>
    <ul>
    %for item in items:
      <li>
        %if isinstance(item, int):
          Zahl: {{item}}
        %else:
          %try:
            Other type: ({{type(item).__name__}}) {{repr(item)}}
          %except:
            Error: Item has no string representation.
          %end try-block (yes, you may add comments here)
        %end
        </li>
      %end
    </ul>
    %include http_footer





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

