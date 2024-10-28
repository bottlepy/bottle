.. currentmodule:: bottle



===============
User's Guide
===============

This guide introduces you to the concepts and features of the Bottle web framework and covers basic and advanced topics alike. You can read it from start to end, or use it as a reference later on. The automatically generated :doc:`api` may be interesting for you, too. It covers more details, but explains less than this tutorial. Solutions for the most common questions can be found in our :doc:`faq` collection or on the :doc:`faq` page. If you need any help, join our `mailing list <mailto:bottlepy@googlegroups.com>`_ or visit us in our `IRC channel <http://webchat.freenode.net/?channels=bottlepy>`_.

.. _installation:

Installation
==============================================================================

Bottle does not depend on any external libraries. You can just download `bottle.py </bottle.py>`_ into your project directory and start coding:

.. code-block:: bash

    $ wget https://bottlepy.org/bottle.py

This will get you the latest development snapshot that includes all the new features. If you prefer a more stable environment, you should stick with the stable releases. These are available on `PyPI <http://pypi.python.org/pypi/bottle>`_ and can be installed via :command:`pip` (recommended) or your package manager:

.. code-block:: bash

    $ pip install --user bottle            # better use a venv, see below
    $ sudo apt-get install python-bottle   # works for debian, ubuntu, ...

It is usually a better idea to create a `virtualenv <https://docs.python.org/3/library/venv.html>`_ per project and use that to install packages:

.. code-block:: bash

    $ python3 -m venv venv         # Create virtual environment
    $ source venv/bin/activate     # Change default python to virtual one
    (venv)$ pip install -U bottle  # Install bottle to virtual environment



Hello World!
==============================================================================

This tutorial assumes you have Bottle either :ref:`installed <installation>` or copied into your project directory. Let's start with a very basic "Hello World" example::

    from bottle import route, run

    @route('/hello')
    def hello():
        return "Hello World!"

    if __name__ == '__main__':
        run(host='localhost', port=8080, debug=True)

This is it. Run this script, visit http://localhost:8080/hello and you will see "Hello World!" in your browser. Here is how it works:

The :func:`route` decorator binds a piece of code to an URL path. In this case, we link the ``/hello`` path to the ``hello()`` function. This is called a `route` (hence the decorator name) and is the most important concept of this framework. You can define as many routes as you want. Whenever a browser requests a URL, the associated function is called and the return value is sent back to the browser. It's as simple as that.

The :func:`run` call in the last line starts a built-in development server. It runs on ``localhost`` port ``8080`` and serves requests until you hit :kbd:`Control-c`. You can switch the server backend later (see :doc:`/deployment`), but for now a development server is all we need. It requires no setup at all and is an incredibly painless way to get your application up and running for local tests.

:ref:`Debug Mode <tutorial-debugging>` is very helpful during early development, but should be switched off for public applications. Keep that in mind.

This is just a demonstration of the basic concept of how applications are built with Bottle. Continue reading and you'll see what else is possible.


.. _tutorial-default:

The Application Object
==============================================================================

For the sake of simplicity, most examples in this tutorial use a module-level :func:`route` and other decorators to define routes. Those refer to a global "default application", an instance of :class:`Bottle` that is automatically created the first time you call :func:`route` or its friends. If you prefer a more explicit approach and don't mind the extra typing, you can create a separate application object and use that instead of the global one::

    from bottle import Bottle, run

    app = Bottle()

    @app.route('/hello')
    def hello():
        return "Hello World!"

    if __name__ == '__main__':
        app.run(host='localhost', port=8080)

The object-oriented approach is further described in the :ref:`default-app` section. Just keep in mind that you have a choice.


.. _tutorial-debugging:

Debug Mode
==============================================================================

During early development, the debug mode can be very helpful.

::

    # Enable debug at runtime
    bottle.debug(True)
    # or during startup
    run(..., debug=True)

In this mode, Bottle is much more verbose and provides helpful debugging information whenever an error occurs. It also disables some optimisations that might get in your way and adds some checks that warn you about possible misconfiguration. Here is an incomplete list of things that change in debug mode:

* The default error page shows a traceback.
* Templates are not cached.
* Plugins are applied immediately.

Just make sure not to use the debug mode on a production server.

Auto Reloading
--------------

Tired of restarting the server every time you change your code?
The auto reloader can do this for you. Every time you edit a module
file, the reloader restarts the server process and loads the newest
version of your code.

::

    run(..., debug=True, reloader=True)

How it works: the main process will not start a server, but spawn a new
child process using the same command line arguments used to start the
main process. All module-level code is executed at least twice! Be
careful.

The child process will have ``os.environ['BOTTLE_CHILD']`` set to ``True``
and start as a normal non-reloading app server. As soon as any of the
loaded modules changes, the child process terminates and is re-spawned by
the main process. Changes in template files will not trigger a reload.
Please use debug mode to deactivate template caching.



.. _tutorial-cli:

Command Line Interface
==============================================================================

Bottle is not only a module, but also a command line executable that can be used to start your app instead of calling :func:`run` programmatically. If you installed bottle via `pip` or similar tools, there will also be a handy `bottle` command on your path. Try one of the following:

.. code-block:: console

    bottle --help
    python3 -m bottle --help
    ./path/to/bottle.py --help

Here is a quick example:

.. code-block:: console

    $ bottle --debug --reload mymodule
    Bottle v0.13-dev server starting up (using WSGIRefServer())...
    Listening on http://localhost:8080/
    Hit Ctrl-C to quit.

.. versionchanged:: 0.13

    The executable script installed into (virtual) environments was named ``bottle.py``, which could result in circular imports. The old name is now deprecated and the new executable ist named just ``bottle``.


.. _tutorial-routing:

Request Routing
==============================================================================

In the last chapter we built a very simple web application with only a single route. Here is the routing part of the "Hello World" example again::

    @route('/hello')
    def hello():
        return "Hello World!"

The :func:`route` decorator links an URL path to a callback function, and adds a new route to the :ref:`default application <tutorial-default>`. An application with just one route is kind of boring, though. Let's add some more (don't forget ``from bottle import template``)::

    @route('/')
    @route('/hello/<name>')
    def greet(name='Stranger'):
        return template('Hello {{name}}, how are you?', name=name)

This example demonstrates two things: You can bind more than one route to a single callback, and you can add wildcards to URLs and access them via keyword arguments.



.. _tutorial-dynamic-routes:

Dynamic Routes
-------------------------------------------------------------------------------

Routes that contain wildcards are called `dynamic routes` (as opposed to `static routes`) and match more than one URL at the same time. A simple wildcard consists of a name enclosed in angle brackets (e.g. ``<name>``) and accepts one or more characters up to the next slash (``/``). For example, the route ``/hello/<name>`` accepts requests for ``/hello/alice`` as well as ``/hello/bob``, but not for ``/hello``, ``/hello/`` or ``/hello/mr/smith``.

Each wildcard passes the covered part of the URL as a keyword argument to the request callback. You can use them right away and implement RESTful, nice-looking and meaningful URLs with ease. Here are some other examples along with the URLs they'd match::

    @route('/wiki/<pagename>')            # matches /wiki/Learning_Python
    def show_wiki_page(pagename):
        ...

    @route('/<action>/<user>')            # matches /follow/defnull
    def user_api(action, user):
        ...

Filters can be used to define more specific wildcards, and/or transform the covered part of the URL before it is passed to the callback. A filtered wildcard is declared as ``<name:filter>`` or ``<name:filter:config>``. The syntax for the optional config part depends on the filter used.

The following filters are implemented by default and more may be added:

* **:int** matches (signed) digits only and converts the value to integer.
* **:float** similar to :int but for decimal numbers.
* **:path** matches all characters including the slash character in a non-greedy way and can be used to match more than one path segment.
* **:re** allows you to specify a custom regular expression in the config field. The matched value is not modified.

Let's have a look at some practical examples::

    @route('/object/<id:int>')
    def callback(id):
        assert isinstance(id, int)

    @route('/show/<name:re:[a-z]+>')
    def callback(name):
        assert name.isalpha()

    @route('/static/<path:path>')
    def callback(path):
        return static_file(path, ...)

You can add your own filters as well. See :doc:`routing` for details.


HTTP Request Methods
------------------------------------------------------------------------------

The HTTP protocol defines several `request methods <https://www.rfc-editor.org/rfc/rfc9110.html#name-methods>`_ (sometimes referred to as "verbs") for different tasks. GET is the default for all routes with no other method specified. These routes will match GET requests only. To handle other methods such as POST, PUT, DELETE or PATCH, add a ``method`` keyword argument to the :func:`route` decorator or use one of the five alternative decorators: :func:`get`, :func:`post`, :func:`put`, :func:`delete` or :func:`patch`.

The POST method is commonly used for HTML form submission. This example shows how to handle a login form using POST::

    from bottle import get, post, request # or route

    @get('/login') # or @route('/login')
    def login():
        return '''
            <form action="/login" method="POST">
                Username: <input name="username" type="text" />
                Password: <input name="password" type="password" />
                <input value="Login" type="submit" />
            </form>
        '''

    @post('/login') # or @route('/login', method='POST')
    def do_login():
        username = request.forms.username
        password = request.forms.password
        if check_login(username, password):
            return "<p>Your login information was correct.</p>"
        else:
            return "<p>Login failed.</p>"

In this example the ``/login`` URL is linked to two distinct callbacks, one for GET requests and another for POST requests. The first one displays a HTML form to the user. The second callback is invoked on a form submission and checks the login credentials the user entered into the form. The use of :attr:`Request.forms <BaseRequest.forms> is further described in the :ref:`tutorial-request` section.

.. rubric:: Special Methods: HEAD and ANY

The HEAD method is used to ask for the response identical to the one that would correspond to a GET request, but without the response body. This is useful for retrieving meta-information about a resource without having to download the entire document. Bottle handles these requests automatically by falling back to the corresponding GET route and cutting off the request body, if present. You don't have to specify any HEAD routes yourself.

Additionally, the non-standard ANY method works as a low priority fallback: Routes that listen to ANY will match requests regardless of their HTTP method but only if no other more specific route is defined. This is helpful for *proxy-routes* that redirect requests to more specific sub-applications.

To sum it up: HEAD requests fall back to GET routes and all requests fall back to ANY routes, but only if there is no matching route for the original request method. It's as simple as that.


.. _tutorial-static-files:

Serving Assets
==================================================================================

Static files or assets such as images or CSS files are not served automatically. You have to add a route and a callback to control which files get served and where to find them. Bottle comes with a handy :func:`static_file` function that does most of the work and serves files in a safe and convenient way::

  from bottle import static_file
  @route('/static/<filepath:path>')
  def server_static(filepath):
      return static_file(filepath, root='/path/to/your/static/files')

Note that we used the ``:path`` route filter here to allow slash characters in ``filepath`` and serve files from sub-directories, too.

The :func:`static_file` helper function has a lot of benefits compared to handling files manually. Most importantly it prevents `directory traversal attacks <https://owasp.org/www-community/attacks/Path_Traversal>`_ (e.g. ``GET /static/../../../../etc/secrets``) by restricting file access to the specified ``root`` directory. Make sure to use an absolut path for ``root``, though. Relative paths (staring with ``./``) are resolved against the current work directory which may not always be the same as your project directory.

The :func:`static_file` function returns :class:`HTTPResponse` or :class:`HTTPError`, which can be raised as an exception if you need to.

.. rubric:: File downloads

Most browsers try to open downloaded files with the associated application if the MIME type is known (e.g. PDF files). If this is not what you want, you can force a download dialog and even suggest a filename to the user::

    @route('/download/<filename>')
    def download(filename):
        return static_file(filename, root='/path/to/static/files', download=f"download-{filename}")

If the ``download`` parameter is just ``True``, the original filename is used.


.. _tutorial-output:

Generating content
==============================================================================

We already learned that route callbacks can return strings as content, but there is more: Bottle supports a bunch of other data types and even adds ``Content-Length`` and other headers if possible, so you don't have to. Here is a list of data types you may return from your application callbacks and a short description of how these are handled by the framework:

Dictionaries
    Python dictionaries (or subclasses thereof) are automatically transformed into JSON strings and returned to the browser with the ``Content-Type`` header set to ``application/json``. This makes it easy to implement JSON-based APIs and is actually implemented by the :class:`JsonPlugin` which is applied to all routes automatically. You can configure and disable JSON handling if you need to.

Empty Strings, ``False``, ``None`` or other non-true values:
    These will produce an empty response.

Lists of strings
    Lists of byte or unicode strings are joined into a single string then processed as usual (see blow).

Unicode strings
    Unicode strings are automatically encoded with the codec specified in the ``Content-Type`` header (``utf8`` by default) and then processed as byte strings (see below).

Byte strings
    Raw byte strings are written to the response as-is.

Instances of :exc:`HTTPError` or :exc:`HTTPResponse`
    Raising or returning an instance of :exc:`HTTPResponse` will overwrite any changes made to the global :data:`request` object and then continue as usual. In case of an :exc:`HTTPError`, error handler are applied first. See :ref:`tutorial-errorhandling` for details.

Files or file-like objects
    Anything that has a ``.read()`` method is treated as a file or file-like object and passed to the ``wsgi.file_wrapper`` callable defined by the WSGI server framework. Some WSGI server implementations can make use of optimized system calls (e.g. sendfile) to transmit files more efficiently. In other cases this just iterates over chunks that fit into memory. Optional headers such as ``Content-Length`` or ``Content-Type`` are *not* set automatically. For security and other reasons you should always prefer :func:`static_file` over returning raw files, though. See :ref:`tutorial-static-files` for details.

Iterables or generators
    You can ``yield`` either byte- or unicode strings (not both) from your route callback and bottle will write those to the response in a streaming fashion. The ``Content-Length`` header is not set in this case, because the final response size is not known. Nested iterables are not supported, sorry. Please note that HTTP status code and headers are sent to the browser as soon as the iterable yields its first non-empty value. Changing these later has no effect. If the first element of the iterable is either :exc:`HTTPError` or :exc:`HTTPResponse`, the rest of the iterator is ignored.

The ordering of this list is significant. You may for example return a subclass of :class:`str` with a ``read()`` method. It is still treated as a string instead of a file, because strings are handled first.

.. rubric:: Changing the Default Encoding

Bottle uses the `charset` parameter of the ``Content-Type`` header to decide how to encode unicode strings. This header defaults to ``text/html; charset=UTF8`` and can be changed using the :attr:`Response.content_type <BaseResponse.content_type>` attribute or by setting the :attr:`Response.charset <BaseResponse.charset>` attribute directly. (The :class:`Response` object is described in the section :ref:`tutorial-response`.)

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

In some rare cases the Python encoding names differ from the names supported by the HTTP specification. Then, you have to do both: first set the :attr:`Response.content_type <BaseResponse.content_type>` header (which is sent to the client unchanged) and then set the :attr:`Response.charset <BaseResponse.charset>` attribute (which is used to encode unicode).


.. _tutorial-errorhandling:

Error handling
==============================================

If anything goes wrong, Bottle displays an informative but fairly plain error page. It contains a stacktrace if :func:`debug` mode is on. You can override the default error page and register an error handler for a specific HTTP status code with the :func:`error` decorator::

  from bottle import error

  @error(404)
  def error404(error):
      return 'Nothing here, sorry'

From now on, ``404`` (File not found) errors will display a custom error page to the user. The only parameter passed to the error-handler is an instance of :exc:`HTTPError`. Apart from that, an error-handler is quite similar to a regular request callback. You can read from :data:`request`, write to :data:`response` and return any supported data-type except for :exc:`HTTPError` instances.

Error handlers are used only if your application returns or raises an :exc:`HTTPError` exception (:func:`abort` does just that). Setting :attr:`Response.status <BaseResponse.status>` to an error code or returning :exc:`HTTPResponse` won't trigger error handlers.

.. rubric:: Triggering errors with :func:`abort`

The :func:`abort` function is a shortcut for triggering HTTP errors.

::

    from bottle import route, abort
    @route('/restricted')
    def restricted():
        abort(401, "Sorry, access denied.")

You do not need to return anything when using :func:`abort`. It raises an :exc:`HTTPError` exception.

.. rubric:: Other Exceptions

All exceptions other than :exc:`HTTPResponse` or :exc:`HTTPError` will result in a ``500 Internal Server Error`` response, so they won't crash your WSGI server. You can turn off this behavior to handle exceptions in your middleware by setting ``bottle.app().catchall`` to ``False``.



.. _tutorial-response:

The :data:`response` Object
--------------------------------------------------------------------------------

Response metadata such as the HTTP status code, response headers and cookies are stored in an object called :data:`response` up to the point where they are transmitted to the browser. You can manipulate these metadata directly or use the predefined helper methods to do so. The full API and feature list is described in the API section (see :class:`BaseResponse`), but the most common use cases and features are covered here, too.

.. rubric:: Status Code

The HTTP status code controls the behavior of the browser and defaults to ``200 OK``. In most scenarios you won't need to set the :attr:`Response.status <BaseResponse.status>` attribute manually, but use the :func:`abort` helper or return an :exc:`HTTPResponse` instance with the appropriate status code. Any integer is allowed, but codes other than the ones defined by the `HTTP specification <https://www.rfc-editor.org/rfc/rfc9110.html#name-status-codes>`_ will only confuse the browser and break standards.

.. rubric:: Response Headers

Response headers such as ``Cache-Control`` or ``Location`` are defined via :meth:`Response.set_header <BaseResponse.set_header>`. This method takes two parameters, a header name and a value. The name part is case-insensitive::

  @route('/wiki/<page>')
  def wiki(page):
      response.set_header('Content-Language', 'en')
      ...

Most headers are unique, meaning that only one header per name is send to the client. Some special headers however are allowed to appear more than once in a response. To add an additional header, use :meth:`Response.add_header <BaseResponse.add_header>` instead of :meth:`Response.set_header <BaseResponse.set_header>`::

    response.set_header('Set-Cookie', 'name=value')
    response.add_header('Set-Cookie', 'name=value2')

Please note that this is just an example. If you want to work with cookies, read :ref:`ahead <tutorial-cookies>`.

.. rubric:: Redirects

To redirect a client to a different URL, you can send a ``303 See Other`` response with the ``Location`` header set to the new URL. :func:`redirect` does that for you::

    from bottle import route, redirect
    @route('/wrong/url')
    def wrong():
        redirect("/right/url")


.. _tutorial-cookies:

Cookies
-------------------------------------------------------------------------------

A cookie is a named piece of text stored in the user's browser profile. You can access previously defined cookies via :meth:`Request.get_cookie <BaseRequest.get_cookie>` and set new cookies with :meth:`Response.set_cookie <BaseResponse.set_cookie>`::

    @route('/hello')
    def hello_again():
        if request.get_cookie("visited"):
            return "Welcome back! Nice to see you again"
        else:
            response.set_cookie("visited", "yes")
            return "Hello there! Nice to meet you"

The :meth:`Response.set_cookie <BaseResponse.set_cookie>` method accepts a number of additional keyword arguments that control the cookies lifetime and behavior. Some of the most common settings are described here:

* **max_age:**    Maximum age in seconds. (default: ``None``)
* **expires:**    A datetime object or UNIX timestamp. (default: ``None``)
* **domain:**     The domain that is allowed to read the cookie. (default: current domain)
* **path:**       Limit the cookie to a given path (default: ``/``)
* **secure:**     Limit the cookie to HTTPS connections (default: off).
* **httponly:**   Prevent client-side javascript to read this cookie (default: off, requires Python 2.7 or newer).
* **samesite:**   Disables third-party use for a cookie. Allowed attributes: `lax` and `strict`. In strict mode the cookie will never be sent. In lax mode the cookie is only sent with a top-level GET request.

If neither `expires` nor `max_age` is set, the cookie expires at the end of the browser session or as soon as the browser window is closed. There are some other gotchas you should consider when using cookies:

* Cookies are limited to 4 KB of text in most browsers.
* Some users configure their browsers to not accept cookies at all. Most search engines ignore cookies too. Make sure that your application still works without cookies.
* Cookies are stored at client side and are not encrypted in any way. Whatever you store in a cookie, the user can read it. Worse than that, an attacker might be able to steal a user's cookies through `XSS <http://en.wikipedia.org/wiki/HTTP_cookie#Cookie_theft_and_session_hijacking>`_ vulnerabilities on your side. Some viruses are known to read the browser cookies, too. Thus, never store confidential information in cookies.
* Cookies are easily forged by malicious clients. Do not trust cookies.

.. _tutorial-signed-cookies:

.. rubric:: Signed Cookies

As mentioned above, cookies are easily forged by malicious clients. Bottle can cryptographically sign your cookies to prevent this kind of manipulation. All you have to do is to provide a signature key via the `secret` keyword argument whenever you read or set a cookie and keep that key a secret. As a result, :meth:`Request.get_cookie <BaseRequest.get_cookie>` will return ``None`` if the cookie is not signed or the signature keys don't match::

    @route('/login')
    def do_login():
        username = request.forms.get('username')
        password = request.forms.get('password')
        if check_login(username, password):
            response.set_cookie("account", username, secret='some-secret-key')
            return template("<p>Welcome {{name}}! You are now logged in.</p>", name=username)
        else:
            return "<p>Login failed.</p>"

    @route('/restricted')
    def restricted_area():
        username = request.get_cookie("account", secret='some-secret-key')
        if username:
            return template("Hello {{name}}. Welcome back.", name=username)
        else:
            return "You are not logged in. Access denied."

In addition, Bottle automatically pickles and unpickles any data stored to signed cookies. This allows you to store any pickle-able object (not only strings) to cookies, as long as the pickled data does not exceed the 4 KB limit.

.. warning:: Signed cookies are not encrypted (the client can still see the content) and not copy-protected (the client can restore an old cookie). The main intention is to make pickling and unpickling safe and prevent manipulation, not to store secret information at client side.









.. _tutorial-request:

Request Data
==============================================================================

Cookies, HTTP header, form data and other request data is available through the global :data:`request` object. This special object always refers to the *current* request, even in multi-threaded environments where multiple client connections are handled at the same time::

  from bottle import request, route, template

  @route('/hello')
  def hello():
      name = request.cookies.username or 'Guest'
      return template('Hello {{name}}', name=name)

The :data:`request` object is a subclass of :class:`BaseRequest` and has a very rich API to access data. We only cover the most commonly used features here, but it should be enough to get started.


HTTP Headers
--------------------------------------------------------------------------------

All HTTP headers sent by the client (e.g. ``Referer``, ``Agent`` or ``Accept-Language``) are stored in a :class:`WSGIHeaderDict` and accessible through the :attr:`Request.headers <BaseRequest.headers>` attribute. A :class:`WSGIHeaderDict` is basically a dictionary with case-insensitive keys::

  from bottle import route, request
  @route('/is_ajax')
  def is_ajax():
      if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
          return 'This is an AJAX request'
      else:
          return 'This is a normal request'


Cookies
--------------------------------------------------------------------------------

Cookies are small pieces of text stored in the clients browser and sent back to the server with each request. They are useful to keep some state around for more than one request (HTTP itself is stateless), but should not be used for security related stuff. They can be easily forged by the client.

All cookies sent by the client are available through :attr:`Request.cookies <BaseRequest.cookies>` (a :class:`FormsDict`). This example shows a simple cookie-based view counter::

  from bottle import route, request, response
  @route('/counter')
  def counter():
      count = int( request.cookies.get('counter', '0') )
      count += 1
      response.set_cookie('counter', str(count))
      return 'You visited this page %d times' % count

The :meth:`Request.get_cookie <BaseRequest.get_cookie>` method is a different way do access cookies. It supports decoding :ref:`signed cookies <tutorial-signed-cookies>` as described in a separate section.


Query parameters, Forms and File uploads
---------------------------------------------

Query and form data is parsed on demand and accessible via :data:`request` properties and methods. Some of those properties combine values from different sources for easier access. Have a look at the following table for a quick overview.

============================================   ==============================================================
Property                                       Data source
============================================   ==============================================================
:attr:`Request.GET <BaseRequest.GET>`          Query parameters
:attr:`Request.query <BaseRequest.query>`      Alias for :attr:`Request.GET <BaseRequest.GET>`
:attr:`Request.POST <BaseRequest.POST>`        orm fields and file uploads combined
:attr:`Request.forms <BaseRequest.forms>`      orm fields
:attr:`Request.files <BaseRequest.files>`      File uploads or very large form fields
:attr:`Request.params <BaseRequest.params>`    Query parameters and form fields combined
============================================   ==============================================================

.. rubric:: Introducing :class:`FormsDict`

Bottle uses a special type of dictionary to store those parameters. :class:`FormsDict` behaves like a normal dictionary, but has some additional features to make your life easier.

First of all, :class:`FormsDict` is a subclass of :class:`MultiDict` and can store more than one value per key. The standard dictionary access methods will only return the first of many values, but the :meth:`MultiDict.getall` method returns a (possibly empty) list of all values for a specific key::

  for choice in request.forms.getall('multiple_choice'):
      do_something(choice)

To simplify dealing with lots of unreliable user input, :class:`FormsDict` exposes all its values as attributes, but with a twist: These virtual attributes always return properly encoded unicode strings, even if the value is missing or character decoding fails. They never return ``None`` or throw an exception, but return an empty string instead::

  name = request.query.name    # may be an empty string

.. rubric:: A word on unicode and character encodings

HTTP is a byte-based wire protocol. The server has to decode byte strings somehow before they are passed to the application. To be on the safe side, WSGI suggests ISO-8859-1 (aka latin1), a reversible single-byte codec that can be re-encoded with a different encoding later. Bottle does that for :meth:`FormsDict.getunicode` and attribute access, but not for :meth:`FormsDict.get` or item-access. These return the unchanged values as provided by the server implementation, which is probably not what you want.

::

    >>> request.query['city']
    'GÃ¶ttingen' # An utf8 string provisionally decoded as ISO-8859-1 by the server
    >>> request.query.city
    'Göttingen'  # The same string correctly re-encoded as utf8 by bottle

If you need the whole dictionary with correctly decoded values (e.g. for WTForms), you can call :meth:`FormsDict.decode` to get a fully re-encoded copy.


Query Parameters
--------------------------------------------------------------------------------

The query string (as in ``/forum?id=1&page=5``) is commonly used to transmit a small number of key/value pairs to the server. You can use the :attr:`Request.query <BaseRequest.query>` attribute (a :class:`FormsDict`) to access these values and the :attr:`Request.query_string <BaseRequest.query_string>` attribute to get the whole string.

::

  from bottle import route, request, response, template
  @route('/forum')
  def display_forum():
      forum_id = request.query.id
      page = request.query.page or '1'
      return template('Forum ID: {{id}} (page {{page}})', id=forum_id, page=page)


HTML `<form>` Handling
----------------------

Let us start from the beginning. In HTML, a typical ``<form>`` looks something like this:

.. code-block:: html

    <form action="/login" method="post">
        Username: <input name="username" type="text" />
        Password: <input name="password" type="password" />
        <input value="Login" type="submit" />
    </form>

The ``action`` attribute specifies the URL that will receive the form data. ``method`` defines the HTTP method to use (``GET`` or ``POST``). With ``method="get"`` the form values are appended to the URL and available through :attr:`Request.query <BaseRequest.query>` as described above. This is sometimes considered insecure and has other limitations, so we use ``method="post"`` here. If in doubt, use ``POST`` forms.

Form fields transmitted via ``POST`` are stored in :attr:`Request.forms <BaseRequest.forms>` as a :class:`FormsDict`. The server side code may look like this::

    from bottle import route, request

    @route('/login')
    def login():
        return '''
            <form action="/login" method="post">
                Username: <input name="username" type="text" />
                Password: <input name="password" type="password" />
                <input value="Login" type="submit" />
            </form>
        '''

    @route('/login', method='POST')
    def do_login():
        username = request.forms.username
        password = request.forms.password
        if check_login(username, password):
            return "<p>Your login information was correct.</p>"
        else:
            return "<p>Login failed.</p>"


File Uploads
------------

To support file uploads, we have to change the ``<form>`` tag a bit. First, we tell the browser to encode the form data in a different way by adding an ``enctype="multipart/form-data"`` attribute to the ``<form>`` tag. Then, we add ``<input type="file" />`` tags to allow the user to select a file. Here is an example:

.. code-block:: html

    <form action="/upload" method="post" enctype="multipart/form-data">
      Category:      <input type="text" name="category" />
      Select a file: <input type="file" name="upload" />
      <input type="submit" value="Start upload" />
    </form>

Bottle stores file uploads in :attr:`Request.files <BaseRequest.files>` as :class:`FileUpload` instances, along with some metadata about the upload. Let us assume you just want to save the file to disk::

    @route('/upload', method='POST')
    def do_upload():
        category   = request.forms.category
        upload     = request.files.get('upload')
        name, ext = os.path.splitext(upload.filename)
        if ext not in ('.png','.jpg','.jpeg'):
            return 'File extension not allowed.'

        save_path = get_save_path_for_category(category)
        upload.save(save_path) # appends upload.filename automatically
        return 'OK'

:attr:`FileUpload.filename` contains the name of the file on the clients file system, but is cleaned up and normalized to prevent bugs caused by unsupported characters or path segments in the filename. If you need the unmodified name as sent by the client, have a look at :attr:`FileUpload.raw_filename`.

The :attr:`FileUpload.save` method is highly recommended if you want to store the file to disk. It prevents some common errors (e.g. it does not overwrite existing files unless you tell it to) and stores the file in a memory efficient way. You can access the file object directly via :attr:`FileUpload.file`. Just be careful.


JSON
--------------------

For JavaScript and REST APIs it is very common to send ``application/json`` to the server instead of from data.
The :attr:`Request.json <BaseRequest.json>` attribute contains the parsed data structure if available, or ``None`` for empty
requests or those that did not contain ``application/json`` data. Parsing errors trigger an appropiate :exc:`HTTPError`.


Raw Request Data
--------------------

You can access the raw body data as a file-like object via :attr:`Request.body <BaseRequest.body>`. This is a :class:`io.BytesIO` buffer or a temporary file depending on the content length and :attr:`Request.MEMFILE_MAX <BaseRequest.MEMFILE_MAX>` setting. In both cases the body is completely buffered before you can access the attribute. If you expect huge amounts of data and want to get direct unbuffered access to the stream, have a look at ``request['wsgi.input']``.


WSGI Environment
--------------------------------------------------------------------------------

Each :class:`BaseRequest` instance wraps a WSGI environment dictionary which is stored in :attr:`Request.environ <BaseRequest.environ>`. Most of the interesting information is also exposed through special methods or properties, but if you want to access the raw `WSGI environ <https://peps.python.org/pep-3333/>`_ directly, you can do so::

  @route('/my_ip')
  def show_ip():
      ip = request.environ.get('REMOTE_ADDR')
      # or ip = request.get('REMOTE_ADDR')
      # or ip = request['REMOTE_ADDR']
      return template("Your IP is: {{ip}}", ip=ip)







.. _tutorial-templates:

Templates
================================================================================

Bottle comes with a fast and powerful built-in template engine called :doc:`stpl`. To render a template you can use the :func:`template` function or the :func:`view` decorator. All you have to do is to provide the name of the template and the variables you want to pass to the template as keyword arguments. Here’s a simple example of how to render a template::

    @route('/hello')
    @route('/hello/<name>')
    def hello(name='World'):
        return template('hello_template', name=name)

This will load the template file ``hello_template.tpl`` and render it with the ``name`` variable set. Bottle will look for templates in the ``./views/`` folder or any folder specified in the ``bottle.TEMPLATE_PATH`` list.

The :func:`view` decorator allows you to return a dictionary with the template variables instead of calling :func:`template`::

    @route('/hello')
    @route('/hello/<name>')
    @view('hello_template')
    def hello(name='World'):
        return dict(name=name)

.. rubric:: Syntax

The template syntax is a very thin layer around the Python language. Its main purpose is to ensure correct indentation of blocks, so you can format your template without worrying about indentation. Follow the link for a full syntax description: :doc:`stpl`
Here is an example template:

.. code-block:: html+django

    %if name == 'World':
        <h1>Hello {{name}}!</h1>
        <p>This is a test.</p>
    %else:
        <h1>Hello {{name.title()}}!</h1>
        <p>How are you?</p>
    %end

.. rubric:: Caching

Templates are cached in memory after compilation. Modifications made to the template files will have no affect until you clear the template cache. Call ``bottle.TEMPLATES.clear()`` to do so. Caching is disabled in debug mode.


.. _default-app:

Structuring Applications
================================================================================

Bottle maintains a global stack of :class:`Bottle` instances and uses the top of the stack as a default for some of the module-level functions and decorators. The :func:`route` decorator or `run()` function for example are shortcuts for :meth:`Bottle.route` or :meth:`Bottle.run` on the default application::

    @route('/')
    def hello():
        return 'Hello World'

    if __name__ == '__main__':
        run()

This is very convenient for small applications and saves you some typing, but also means that, as soon as your module is imported, routes are installed to the global default application. To avoid this kind of import side-effects, Bottle offers a second, more explicit way to build applications::

    app = Bottle()

    @app.route('/')
    def hello():
        return 'Hello World'

    app.run()

Separating the application object improves re-usability a lot, too. Other developers can safely import the ``app`` object from your module and use :meth:`Bottle.mount` to merge applications together.


.. versionadded:: 0.13

Starting with bottle-0.13 you can use :class:`Bottle` instances as context managers::

    app = Bottle()

    with app:

        # Our application object is now the default
        # for all shortcut functions and decorators

        assert my_app is default_app()

        @route('/')
        def hello():
            return 'Hello World'

        # Also useful to capture routes defined in other modules
        import some_package.more_routes


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

