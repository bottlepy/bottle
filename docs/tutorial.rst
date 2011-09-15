.. module:: bottle

.. _Apache Server:
.. _Apache: http://www.apache.org/
.. _cherrypy: http://www.cherrypy.org/
.. _decorator: http://docs.python.org/glossary.html#term-decorator
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

=============
Documentation
=============

This tutorial introduces you to the concepts and features of the Bottle web framework. If you have questions not answered here, please check the :doc:`faq` page, file a ticket at the issue_ tracker or send an e-mail to the `mailing list <mailto:bottlepy@googlegroups.com>`_.

.. rubric:: A quick overview:

* :ref:`tutorial-routing`: Web development starts with binding URLs to code. This section tells you how to do it.
* :ref:`tutorial-output`: You have to return something to the Browser. Bottle makes it easy for you, supporting more than just plain strings.
* :ref:`tutorial-request`: Each client request carries a lot of information. HTTP-headers, form data and cookies to name just three. Here is how to use them.
* :ref:`tutorial-templates`: You don't want to clutter your Python code with HTML fragments, do you? Templates separate code from presentation.
* :ref:`tutorial-debugging`: These tools and features will help you during development.
* :ref:`tutorial-deployment`: Get it up and running.

.. _installation:

Installation
==============================================================================

Bottle does not depend on any external libraries. You can just download `bottle.py </bottle.py>`_ into your project directory and start coding:

.. code-block:: bash

    $ curl -O http://bottlepy.org/bottle.py
    $ 2to3 -w bottle.py  # Python 3.x users only!

This will get you the latest development snapshot that includes all the new features. If you prefer a more stable environment, you should stick with the stable releases. These are available on `PyPi <http://pypi.python.org/pypi/bottle>`_ and can be installed via :command:`pip` (recommended), :command:`easy_install` or your package manager:

.. code-block:: bash

    $ sudo pip install bottle              # recommended
    $ sudo easy_install bottle             # alternative without pip
    $ sudo apt-get install python-bottle   # works for debian, ubuntu, ...

In either way, you'll need Python 2.5 or newer to run bottle applications. If you do not have permissions to install packages system-wide or simply don't want to, create a `virtualenv <http://pypi.python.org/pypi/virtualenv>`_ first. 
 

A minimal Bottle Application
==============================================================================

This tutorial assumes you have Bottle either :ref:`installed or copied <installation>` into your project directory. Lets start with a very basic "Hello World" example::

    from bottle import route, run
    
    @route('/hello')
    def hello():
        return "Hello World!"
    
    run(host='localhost', port=8080)


Whats happening here?

1. First we import some Bottle components. The :func:`route` decorator and the :func:`run` function. 
2. The :func:`route` :term:`decorator` is used do bind a piece of code to an URL. In this example we want to answer requests to ``/hello``.
3. This function is the :term:`handler function` or :term:`callback` for the ``/hello`` route. It is called every time someone requests the ``/hello`` URL and is responsible for generating the page content.
4. For now, we just return a simple string to the browser.
5. In the last line we start the actual HTTP server. The default is a development server running on 'localhost' port 8080 and serving requests until you hit :kbd:`Control-c`.

This is it. Run this script, visit http://localhost:8080/hello and you will see "Hello World!" in your browser. Of course this is a very simple example, but it shows the basic concept of how applications are built with Bottle. Continue reading and you'll see what else is possible.


.. rubric:: The Application Object

For the sake of simplicity, most examples in this tutorial use a module-level :func:`route` decorator to bind routes. This decorator adds routes to a global application object that is created for you automatically. If you prefer a more explicit way to define your application and don't mind the extra typing, you can create a separate application object and use that instead of the global one::

    from bottle import Bottle, run
    
    app = Bottle()
    
    @app.route('/hello')
    def hello():
        return "Hello World!"
    
    run(app, host='localhost', port=8080)

The object-oriented approach is further described in the :ref:`default-app` section. Just keep in mind that you have a choice.




.. _tutorial-routing:

Request Routing
==============================================================================

As you have learned before, applications consist of *routes* that map *URLs* to *callback functions*. These callbacks are executed once for each request that matches the route. The return value is sent to the client. You can add any number of routes to a callback simply by applying the :func:`route` decorator::

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

The :func:`static_file` function is a helper to serve files in a safe and convenient way (see :ref:`tutorial-static-files`). This example is limited to files directly within the ``/path/to/your/static/files`` directory because the ``:filename`` wildcard won't match a path with a slash in it. To serve files in subdirectories too, we can loosen the wildcard a bit::

  @route('/static/:path#.+#')
  def server_static(path):
      return static_file(path, root='/path/to/your/static/files')

Be careful when specifying a relative root-path such as ``root='./static/files'``. The working directory (``./``) and the project directory are not always the same.


.. _tutorial-errorhandling:

Error Pages
------------------------------------------------------------------------------

If anything goes wrong, Bottle displays an informative but fairly boring error page. You can override the default for a specific HTTP status code with the :func:`error` decorator::

  @error(404)
  def error404(error):
      return 'Nothing here, sorry'

From now on, `404 File not Found` errors will display a custom error page to the user. The only parameter passed to the error-handler is an instance of :exc:`HTTPError`. Apart from that, an error-handler is quite similar to a regular request callback. You can read from :data:`request`, write to :data:`response` and return any supported data-type except for :exc:`HTTPError` instances.

Error handlers are used only if your application returns or raises an :exc:`HTTPError` exception (:func:`abort` does just that). Changing :attr:`Request.status` or returning :exc:`HTTPResponse` won't trigger the error handler.




.. _tutorial-output:

Generating content
==============================================================================

In pure WSGI, the range of types you may return from your application is very limited. Applications must return an iterable yielding byte strings. You may return a string (because strings are iterable) but this causes most servers to transmit your content char by char. Unicode strings are not allowed at all. This is not very practical.

Bottle is much more flexible and supports a wide range of types. It even adds a ``Content-Length`` header if possible and encodes unicode automatically, so you don't have to. What follows is a list of data types you may return from your application callbacks and a short description of how these are handled by the framework:

Dictionaries
    As mentioned above, Python dictionaries (or subclasses thereof) are automatically transformed into JSON strings and returned to the browser with the ``Content-Type`` header set to ``application/json``. This makes it easy to implement json-based APIs. Data formats other than json are supported too. See the :ref:`tutorial-output-filter` to learn more.

Empty Strings, ``False``, ``None`` or other non-true values:
    These produce an empty output with ``Content-Length`` header set to 0. 

Unicode strings
    Unicode strings (or iterables yielding unicode strings) are automatically encoded with the codec specified in the ``Content-Type`` header (utf8 by default) and then treated as normal byte strings (see below).

Byte strings
    Bottle returns strings as a whole (instead of iterating over each char) and adds a ``Content-Length`` header based on the string length. Lists of byte strings are joined first. Other iterables yielding byte strings are not joined because they may grow too big to fit into memory. The ``Content-Length`` header is not set in this case.

Instances of :exc:`HTTPError` or :exc:`HTTPResponse`
    Returning these has the same effect as when raising them as an exception. In case of an :exc:`HTTPError`, the error handler is applied. See :ref:`tutorial-errorhandling` for details.

File objects
    Everything that has a ``.read()`` method is treated as a file or file-like object and passed to the ``wsgi.file_wrapper`` callable defined by the WSGI server framework. Some WSGI server implementations can make use of optimized system calls (sendfile) to transmit files more efficiently. In other cases this just iterates over chunks that fit into memory. Optional headers such as ``Content-Length`` or ``Content-Type`` are *not* set automatically. Use :func:`send_file` if possible. See :ref:`tutorial-static-files` for details.

Iterables and generators
    You are allowed to use ``yield`` within your callbacks or return an iterable, as long as the iterable yields byte strings, unicode strings, :exc:`HTTPError` or :exc:`HTTPResponse` instances. Nested iterables are not supported, sorry. Please note that the HTTP status code and the headers are sent to the browser as soon as the iterable yields its first non-empty value. Changing these later has no effect.
  
The ordering of this list is significant. You may for example return a subclass of :class:`str` with a ``read()`` method. It is still treated as a string instead of a file, because strings are handled first.

.. rubric:: Changing the Default Encoding

Bottle uses the `charset` parameter of the ``Content-Type`` header to decide how to encode unicode strings. This header defaults to ``text/html; charset=UTF8`` and can be changed using the :attr:`Response.content_type` attribute or by setting the :attr:`Response.charset` attribute directly. (The :class:`Response` object is described in the section :ref:`tutorial-response`.)

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

In some rare cases the Python encoding names differ from the names supported by the HTTP specification. Then, you have to do both: first set the :attr:`Response.content_type` header (which is sent to the client unchanged) and then set the :attr:`Response.charset` attribute (which is used to encode unicode).

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

All exceptions other than :exc:`HTTPResponse` or :exc:`HTTPError` will result in a ``500 Internal Server Error`` response, so they won't crash your WSGI server. You can turn off this behavior to handle exceptions in your middleware by setting ``bottle.app().catchall`` to ``False``.


.. _tutorial-response:

The :class:`Response` Object
--------------------------------------------------------------------------------

Response meta-data such as the HTTP status code, response header and cookies are stored in an object called :data:`response` up to the point where they are transmitted to the browser. You can manipulate these meta-data directly or use the predefined helper methods to do so. The full API and feature list is described in the API section (see :class:`Response`), but the most common use cases and features are covered here, too.

.. rubric:: Status Code

The `HTTP status code <http_code>`_ controls the behavior of the browser and defaults to ``200 OK``. In most scenarios you won't need to set the :attr:`Response.status` attribute manually, but use the :func:`abort` helper or return an :exc:`HTTPResponse` instance with the appropriate status code. Any integer is allowed but only the codes defined by the `HTTP specification <http_code>`_ will have an effect other than confusing the browser and breaking standards.

.. rubric:: Response Header

Response headers such as ``Cache-Control`` or ``Location`` are defined via :meth:`Response.set_header`. This method takes two parameters, a header name and a value. The name part is case-insensitive::

  @route('/wiki/:page')
  def wiki(page):
      response.set_header('Content-Language', 'en')
      ...

Most headers are exclusive, meaning that only one header per name is send to the client. Some special headers however are allowed to appear more than once in a response. To add an additional header, use :meth:`Response.add_header` instead of :meth:`Response.set_header`::

    response.set_header('Set-Cookie', 'name=value')
    response.add_header('Set-Cookie', 'name2=value2')

Please not that this is just an example. If you want to work with cookies, read :ref:`ahead <tutorial-cookies>`.


.. _tutorial-cookies:

Cookies
-------------------------------------------------------------------------------

A cookie is a named piece of text stored in the user's browser cache. You can access previously defined cookies via :meth:`Request.get_cookie` and set new cookies with :meth:`Response.set_cookie`::

    @route('/hello')
    def hello_again(self):
        if request.get_cookie("visited"):
            return "Welcome back! Nice to see you again"
        else:
            response.set_cookie("visited", "yes")
            return "Hello there! Nice to meet you"

The :meth:`Response.set_cookie` method accepts a number of additional keyword arguments that control the cookies lifetime and behavior. Some of the most common settings are described here:

* **max_age:**    Maximum age in seconds. (default: None)
* **expires:**    A datetime object or UNIX timestamp. (default: None)
* **domain:**     The domain that is allowed to read the cookie. (default: current domain)
* **path:**       Limit the cookie to a given path (default: ``/``)
* **secure:**     Limit the cookie to HTTPS connections (default: off).
* **httponly:**   Prevent client-side javascript to read this cookie (default: off, requires Python 2.6 or newer).

If neither `expires` nor `max_age` is set, the cookie expires at the end of the browser session or as soon as the browser window is closed. There are some other gotchas you should consider when using cookies:

* Cookies are limited to 4kb of text in most browsers.
* Some users configure their browsers to not accept cookies at all. Most search-engines ignore cookies, too. Make sure that your application still works without cookies.
* Cookies are stored at client side and not encrypted in any way. Whatever you store in a cookie, the user can read it. Worth than that, an attacker might be able to steal a user's cookies through `XSS <http://en.wikipedia.org/wiki/HTTP_cookie#Cookie_theft_and_session_hijacking>`_ vulnerabilities on your side. Some viruses are known to read the browser cookies, too. Do not store confidential information in cookies, ever.
* Cookies are easily forged by malicious clients. Do not trust cookies.

.. _tutorial-signed-cookies:

.. rubric:: Signed Cookies

As mentioned above, cookies are easily forged by malicious clients. Bottle can cryptographically sign your cookies to prevent this kind of manipulation. All you have to do is to provide a signature key via the `secret` keyword argument whenever you read or set a cookie and keep that key a secret. As a result, :meth:`Request.get_cookie` will return ``None`` if the cookie is not signed or the signature keys don't match::

    @route('/login')
    def login():
        username = request.forms.get('username')
        password = request.forms.get('password')
        if check_user_credentials(username, password):
            response.set_cookie("account", username, secret='some-secret-key')
            return "Welcome %s! You are now logged in." % username
        else:
            return "Login failed."

    @route('/restricted')
    def restricted_area(self):
        username = request.get_cookie("account", secret='some-secret-key')
        if username:
            return "Hello %s. Welcome back." % username
        else:
            return "You are not logged in. Access denied."

In addition, Bottle automatically pickles and unpickles any data stored to signed cookies. This allows you to store any pickle-able object (not only strings) to cookies, as long as the pickled data does not exceed the 4kb limit.

.. warning:: Signed cookies are not encrypted (the client can still see the content) and not copy-protected (the client can restore an old cookie). The main intention is to make pickling and unpickling safe and prevent manipulation, not to store secret information at client side.









.. _tutorial-request:

Accessing Request Data
==============================================================================

Bottle provides access to HTTP related meta-data such as cookies, headers and POST form data through a global ``request`` object. This object always contains information about the *current* request, as long as it is accessed from within a callback function. This works even in multi-threaded environments where multiple requests are handled at the same time. For details on how a global object can be thread-safe, see :doc:`contextlocal`.

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

Cookies are stored in :attr:`Request.COOKIES` as a normal dictionary. The :meth:`Request.get_cookie` method allows access to :ref:`tutorial-signed-cookies` as described in a separate section. This example shows a simple cookie-based view counter::

  from bottle import route, request, response
  @route('/counter')
  def counter():
      count = int( request.COOKIES.get('counter', '0') )
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
        if name and data.file:
            raw = data.file.read() # This is dangerous for big files
            filename = data.filename
            return "Hello %s! You uploaded %s (%d bytes)." % (name, filename, len(raw))
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

Bottle comes with a fast and powerful built-in template engine called :doc:`stpl`. To render a template you can use the :func:`template` function or the :func:`view` decorator. All you have to do is to provide the name of the template and the variables you want to pass to the template as keyword arguments. Here’s a simple example of how to render a template::

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

The template syntax is a very thin layer around the Python language. Its main purpose is to ensure correct indentation of blocks, so you can format your template without worrying about indentation. Follow the link for a full syntax description: :doc:`stpl`

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




.. _plugins:

Plugins
================================================================================

.. versionadded:: 0.9

Bottle's core features cover most common use-cases, but as a micro-framework it has its limits. This is where "Plugins" come into play. Plugins add missing functionality to the framework, integrate third party libraries, or just automate some repetitive work.

We have a growing :doc:`/plugins/index` and most plugins are designed to be portable and re-usable across applications. The chances are high that your problem has already been solved and a ready-to-use plugin exists. If not, the :doc:`/plugindev` may help you.

The effects and APIs of plugins are manifold and depend on the specific plugin. The 'sqlite' plugin for example detects callbacks that require a ``db`` keyword argument and creates a fresh database connection object every time the callback is called. This makes it very convenient to use a database::

    from bottle import route, install, template
    from bottle_sqlite import SQLitePlugin
    
    install(SQLitePlugin(dbfile='/tmp/test.db'))

    @route('/show/:post_id')
    def show(db, post_id):
        c = db.execute('SELECT title, content FROM posts WHERE id = ?', (int(post_id),))
        row = c.fetchone()
        return template('show_post', title=row['title'], text=row['content'])

    @route('/contact')
    def contact_page():
        ''' This callback does not need a db connection. Because the 'db'
            keyword argument is missing, the sqlite plugin ignores this callback
            completely. '''
        return template('contact')

Other plugin may populate the thread-save :data:`local` object, change details of the :data:`request` object, filter the data returned by the callback or bypass the callback completely. An "auth" plugin for example could check for a valid session and return a login page instead of calling the original callback. What happens exactly depends on the plugin.


Application-wide Installation
--------------------------------------------------------------------------------

Plugins can be installed application-wide or just to some specific routes that need additional functionality. Most plugins are save to be installed to all routes and are smart enough to not add overhead to callbacks that do not need their functionality.

Let us take the 'sqlite' plugin for example. It only affects route callbacks that need a database connection. Other routes are left alone. Because of this, we can install the plugin application-wide with no additional overhead.

To install a plugin, just call :func:`install` with the plugin as first argument::

    from bottle_sqlite import SQLitePlugin
    install(SQLitePlugin(dbfile='/tmp/test.db'))

The plugin is not applied to the route callbacks yet. This is delayed to make sure no routes are missed. You can install plugins first and add routes later, if you want to. The order of installed plugins is significant, though. If a plugin requires a database connection, you need to install the database plugin first.


.. rubric:: Uninstall Plugins

You can use a name, class or instance to :func:`uninstall` a previously installed plugin::

    sqlite_plugin = SQLitePlugin(dbfile='/tmp/test.db')
    install(sqlite_plugin)

    uninstall(sqlite_plugin) # uninstall a specific plugin
    uninstall(SQLitePlugin)  # uninstall all plugins of that type
    uninstall('sqlite')      # uninstall all plugins with that name
    uninstall(True)          # uninstall all plugins at once

Plugins can be installed and removed at any time, even at runtime while serving requests. This enables some neat tricks (installing slow debugging or profiling plugins only when needed) but should not be overused. Each time the list of plugins changes, the route cache is flushed and all plugins are re-applied.

.. note::
    The module-level :func:`install` and :func:`uninstall` functions affect the :ref:`default-app`. To manage plugins for a specific application, use the corresponding methods on the :class:`Bottle` application object.


Route-specific Installation
--------------------------------------------------------------------------------

The ``apply`` parameter of the :func:`route` decorator comes in handy if you want to install plugins to only a small number of routes::

    sqlite_plugin = SQLitePlugin(dbfile='/tmp/test.db')

    @route('/create', apply=[sqlite_plugin])
    def create(db):
        db.execute('INSERT INTO ...')


Blacklisting Plugins
--------------------------------------------------------------------------------

You may want to explicitly disable a plugin for a number of routes. The :func:`route` decorator has a ``skip`` parameter for this purpose::

    sqlite_plugin = SQLitePlugin(dbfile='/tmp/test.db')
    install(sqlite_plugin)

    @route('/open/:db', skip=[sqlite_plugin])
    def open_db(db):
        # The 'db' keyword argument is not touched by the plugin this time.
        if db in ('test', 'test2'):
            # The plugin handle can be used for runtime configuration, too.
            sqlite_plugin.dbfile = '/tmp/%s.db' % db
            return "Database File switched to: /tmp/%s.db" % db
        abort(404, "No such database.")

The ``skip`` parameter accepts a single value or a list of values. You can use a name, class or instance to identify the plugin that is to be skipped. Set ``skip=True`` to skip all plugins at once.

Plugins and Sub-Applications
--------------------------------------------------------------------------------

Most plugins are specific to the application they were installed to. Consequently, they should not affect sub-applications mounted with :meth:`Bottle.mount`. Here is an example::

    root = Bottle()
    root.mount(apps.blog, '/blog')
    
    @root.route('/contact', template='contact')
    def contact():
        return {'email': 'contact@example.com'}
    
    root.install(plugins.WTForms())

Whenever you mount an application, Bottle creates a proxy-route on the main-application that relays all requests to the sub-application. Plugins are disabled for this kind of proxy-routes by default. As a result, our (fictional) `WTForms` plugin affects the ``/contact`` route, but does not affect the routes of the ``/blog`` sub-application.

This behavior is intended as a sane default, but can be overridden. The following example re-activates all plugins for a specific proxy-route::

    root.mount(apps.blog, '/blog', skip=None)

But there is a snag: The plugin sees the whole sub-application as a single route, namely the proxy-route mentioned above. In order to affect each individual route of the sub-application, you have to install the plugin to the application explicitly.



Development
================================================================================

You learned the basics and want to write your own application? Here are
some tips that might help you to be more productive.

.. _default-app:

Default Application
--------------------------------------------------------------------------------

Bottle maintains a global stack of :class:`Bottle` instances and uses the top of the stack as a default for some of the module-level functions and decorators. The :func:`route` decorator, for example, is a shortcut for calling :meth:`Bottle.route` on the default application::

    @route('/')
    def hello():
        return 'Hello World'

This is very convenient for small applications and saves you some typing, but also means that, as soon as your module is imported, routes are installed to the global application. To avoid this kind of import side-effects, Bottle offers a second, more explicit way to build applications::

    app = Bottle()
    
    @app.route('/')
    def hello():
        return 'Hello World'

Separating the application object improves re-usability a lot, too. Other developers can safely import the ``app`` object from your module and use :meth:`Bottle.mount` to merge applications together.

As an alternative, you can make use of the application stack to isolate your routes while still using the convenient shortcuts::

    default_app.push()

    @route('/')
    def hello():
        return 'Hello World'

    app = default_app.pop()

Both :func:`app` and :func:`default_app` are instance of :class:`AppStack` and implement a stack-like API. You can push and pop applications from and to the stack as needed. This also helps if you want to import a third party module that does not offer a separate application object::

    default_app.push()

    import some.module

    app = default_app.pop()


.. _tutorial-debugging:


Debug Mode
--------------------------------------------------------------------------------

During early development, the debug mode can be very helpful.

.. highlight:: python

::

    bottle.debug(True)

In this mode, Bottle is much more verbose and provides helpful debugging information whenever an error occurs. It also disables some optimisations that might get in your way and adds some checks that warn you about possible misconfiguration.

Here is an incomplete list of things that change in debug mode:

* The default error page shows a traceback.
* Templates are not cached.
* Plugins are applied immediately.

Just make sure to not use the debug mode on a production server.

Auto Reloading
--------------------------------------------------------------------------------

During development, you have to restart the server a lot to test your 
recent changes. The auto reloader can do this for you. Every time you 
edit a module file, the reloader restarts the server process and loads 
the newest version of your code. 

::

    from bottle import run
    run(reloader=True)

How it works: the main process will not start a server, but spawn a new 
child process using the same command line arguments used to start the 
main process. All module-level code is executed at least twice! Be 
careful.

The child process will have ``os.environ['BOTTLE_CHILD']`` set to ``True`` 
and start as a normal non-reloading app server. As soon as any of the 
loaded modules changes, the child process is terminated and re-spawned by 
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

Bottle runs on the built-in `wsgiref WSGIServer <http://docs.python.org/library/wsgiref.html#module-wsgiref.simple_server>`_  by default. This non-threading HTTP server is perfectly fine for development and early production, but may become a performance bottleneck when server load increases.

There are three ways to eliminate this bottleneck:

* Use a multi-threaded or asynchronous HTTP server.
* Spread the load between multiple Bottle instances.
* Do both.



Multi-Threaded Server
--------------------------------------------------------------------------------

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

The easiest way to increase performance is to install a multi-threaded or asynchronous WSGI server like paste_ or cherrypy_ and tell Bottle to start it instead of the default single-threaded one::

    bottle.run(server='paste') # Example

Bottle ships with a lot of ready-to-use adapters for the most common WSGI servers and automates the setup process. Here is an incomplete list:

========  ============  ======================================================
Name      Homepage      Description
========  ============  ======================================================
cgi                     Run as CGI script
flup      flup_         Run as Fast CGI process
gae       gae_          Helper for Google App Engine deployments
wsgiref   wsgiref_      Single-threaded default server
cherrypy  cherrypy_     Multi-threaded and very stable
paste     paste_        Multi-threaded, stable, tried and tested
rocket    rocket_       Multi-threaded
gunicorn  gunicorn_     Pre-forked, partly written in C
fapws3    fapws3_       Asynchronous, written in C
tornado   tornado_      Asynchronous, powers some parts of Facebook
twisted   twisted_      Asynchronous, well tested
diesel    diesel_       Asynchronous, based on greenlet
meinheld  meinheld_     Asynchronous, partly written in C
bjoern    bjoern_       Asynchronous, very fast and written in C
auto                    Automatically selects an available server adapter
========  ============  ======================================================

The full list is available through :data:`server_names`.

If there is no adapter for your favorite server or if you need more control over the server setup, you may want to start the server manually. Refer to the server documentation on how to mount WSGI applications. Here is an example for paste_::

    from paste import httpserver
    httpserver.serve(bottle.default_app(), host='0.0.0.0', port=80)


Multiple Server Processes
--------------------------------------------------------------------------------

A single Python process can only utilise one CPU at a time, even if 
there are more CPU cores available. The trick is to balance the load 
between multiple independent Python processes to utilize all of your 
CPU cores.

Instead of a single Bottle application server, you start one instance 
of your server for each CPU core available using different local port 
(localhost:8080, 8081, 8082, ...). Then a high performance load 
balancer acts as a reverse proxy and forwards each new requests to 
a random Bottle processes, spreading the load between all available 
back end server instances. This way you can use all of your CPU cores and 
even spread out the load between different physical servers.

One of the fastest load balancers available is Pound_ but most common web servers have a proxy-module that can do the work just fine.


Apache mod_wsgi
--------------------------------------------------------------------------------

Instead of running your own HTTP server from within Bottle, you can 
attach Bottle applications to an `Apache server`_ using 
mod_wsgi_ and Bottle's WSGI interface.

All you need is an ``app.wsgi`` file that provides an 
``application`` object. This object is used by mod_wsgi to start your 
application and should be a WSGI-compatible Python callable.

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

The ``gae`` adapter completely automates the Google App Engine deployment. It even ensures that a ``main()`` function is present in your ``__main__`` module to enable `App Caching <http://code.google.com/appengine/docs/python/runtime.html#App_Caching>`_ (which drastically improves performance)::

    import bottle
    # ... build or import your bottle application here ...
    bottle.run(server='gae')

It is always a good idea to let GAE serve static files directly. Here is example ``app.yaml``::

    application: myapp
    version: 1
    runtime: python
    api_version: 1

    handlers:
    - url: /static
      static_dir: static

    - url: /.*
      script: myapp.py


Good old CGI
--------------------------------------------------------------------------------

CGI is slow as hell, but it works::

    import bottle
    # ... build or import your bottle application here ...
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
      as callback for each specific URL comprising the application.

   source directory
      The directory which, including its subdirectories, contains all
      source files for one Sphinx project.

