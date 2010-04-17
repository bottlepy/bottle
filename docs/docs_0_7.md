[TOC]

  [apache]: http://www.apache.org/
  [cherrypy]: http://www.cherrypy.org/
  [decorator]: http://docs.python.org/glossary.html#term-decorator
  [fapws3]: http://github.com/william-os4y/fapws3
  [flup]: http://trac.saddi.com/flup
  [http_code]: http://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html
  [http_method]: http://www.w3.org/Protocols/rfc2616/rfc2616-sec9.html
  [mako]: http://www.makotemplates.org/
  [mod_wsgi]: http://code.google.com/p/modwsgi/
  [paste]: http://pythonpaste.org/
  [wsgi]: http://www.wsgi.org/wsgi/

# Bottle Documentation

__This document is a work in progress__ and intended to be a tutorial, howto and an api documentation at the same time. If you have questions not answered here,
please check the [F.A.Q.](/page/faq) or file a ticket at bottles [issue tracker](http://github.com/defnull/bottle/issues).

This documentation describes the features of the **0.7 Release**


## "Hello World" in a Bottle

Lets start with a very basic example: Hello World

    #!Python
    from bottle import route, run
    @route('/hello')
    def hello():
        return "Hello World!"
    run() # This starts the HTTP server

Run this script, visit <http://localhost:8080/hello> and you will see "Hello World!" in your Browser. So, what happened here?

  1. First we imported some bottle components. The `route()` decorator and the `run()` function. 
  2. The `route()` [decorator][] is used to bind a piece of code to an URL. In this example we want to answer requests to the `/hello` URL.
  3. This function will be called every time someone hits the `/hello` URL on the web server. It is called a __handler function__ or __callback__.
  4. The return value of a handler function will be sent back to the Browser.
  5. Now it is time to start the actual HTTP server. The default is a development server running on *localhost* port *8080* and serving requests until you hit __Ctrl-C__




# Routing

Routes are used to map an URL to a callback function that generate the content for that specific URL. Bottle has a `route()` decorator to do that. You can add any number of routes to a callback.

    #!Python
    from bottle import route
    @route('/')
    @route('/index.html')
    def index():
        return "<a href='/hello'>Go to Hello World page</a>"

    @route('/hello')
    def hello():
        return "Hello World!"

As you can see, URLs and routes have nothing to do with actual files on the web server. Routes are unique names for your callbacks, nothing more and nothing less. Requests to URLs not matching any routes are answered with a 404 HTTP error page. Exceptions within your handler callbacks will cause a 500 error. 





## HTTP Request Methods

The `route()` decorator has an optional keyword argument `method` which defaults to `method='GET'`; only GET requests get answered by that route.
Possible values are `POST`, `PUT`, `DELETE`, `HEAD`, or any other [HTTP request method][http_method] you want to listen to. Also `ANY` which will be used as fallback for any method. As an alternative, you can use the `@get()`, `@post()`, `@put()` and `@delete()` aliases.

    #!Python
    from bottle import post, request
    @post('/form/submit')
    def form_submit():
        form_data = request.POST # (*)
        do_something_with(form_data)
        return "Done"

\* In this example we used [request.POST](#working-with-http-requests) to access POST form data.

Note that `HEAD` requests will fall back to `GET` routes and all requests will fall back to `ANY` routes, if there is no matching route for the original request method.






## Dynamic Routes

Static routes are fine, but URLs may carry information as well. Let's add a `:name` placeholder to our route.

    #!Python
    from bottle import route
    @route('/hello/:name')
    def hello(name):
        return "Hello %s!" % name

This dynamic route matches `/hello/alice` as well as `/hello/bob`. In fact, the `:name` part will match everything but a slash (`/`), so any name is possible. `/hello/bob/and/alice` or `/hellobob` won't match. Each part of the URL covered by a placeholder is provided as a keyword argument to your handler callback.

A normal placeholder matches everything up to the next slash. To change that, you can add a regular expression pattern:

    #!Python
    from bottle import route
    @route('/get_object/:id#[0-9]+#')
    def get(id):
        return "Object ID: %d" % int(id)

As you can see, URL parameters remain strings, even if they are configured to only match digits. You have to explicitly cast them into the type you need.




## The @validate() decorator

Bottle offers a handy decorator called `validate()` to check and manipulate URL parameters. It takes callables (function or class objects) as keyword arguments and filters every URL parameter through the corresponding callable before they are passed to your request handler.

    #!Python
    from bottle import route, validate
    # /test/validate/1/2.3/4,5,6,7
    @route('/test/validate/:i/:f/:csv')
    @validate(i=int, f=float, csv=lambda x: map(int, x.split(',')))
    def validate_test(i, f, csv):
        return "Int: %d, Float:%f, List:%s" % (i, f, repr(csv))

You may raise `ValueError` in your custom callable if a parameter does not validate.




# Generating content

The [WSGI specification][wsgi] expects an iterable list of byte strings to be returned from your application and can't handle unicode, dictionaries or exceptions. File objects will be handled as iterables in *pure* WSGI, with no conditional caching or `Content-Length` calculation.

    #!Python
    @route('/wsgi')
    def wsgi():
        return ['WSGI','wants a','list of','strings']

Bottle automatically tries to convert anything to a WSGI supported type, so you
don't have to. The following examples will work with Bottle, but won't work with
pure WSGI.

## Strings and Unicode

Returning strings (bytes) is not a problem. Unicode however needs to be encoded into a byte stream before 
the webserver can send it to the client. The default encoding is utf-8. If that fits your needs, you can
simply return unicode or unicode iterables.

    #!Python
    @route('/string')
    def get_string():
        return 'Bottle converts strings to iterables'
    
    @route('/unicode')
    def get_unicode():
        return u'Unicode is encoded with UTF-8 by default'

You can change Bottles default encoding by setting `response.content_type` to a value containing a `charset=...` parameter or by changing `response.charset` directly.

    #!Python
    from bottle import response
    @route('/iso')
    def get_iso():
        response.charset = 'ISO-8859-15'
        return u'This will be sent with ISO-8859-15 encoding.'

    @route('/latin9')
    def get_latin():
        response.content_type = 'text/html; charset=latin9'
        return u'ISO-8859-15 is also known as latin9.'

In some rare cases the Python encoding names differ from the names supported by the HTTP specification. Then, you have to do both: First set the `response.content_type` header (which is sent to the client unchanged) and then set the `response.charset` option (which is used to decode unicode).

## File Objects and Streams

Bottle passes everything that has a `read()` method (file objects) to the `wsgi.file_wrapper` provided by your WSGI server implementation. This wrapper should use optimised system calls (`sendfile` on UNIX) to transfer the file contents.

    #!Python
    @route('/file')
    def get_file():
        return open('some/file.txt','r')

## JSON

Even dictionaries are allowed. They are converted to [json](http://de.wikipedia.org/wiki/JavaScript_Object_Notation) and returned with the `Content-Type` header set to `application/json`. To disable this feature (and pass dicts to your middleware) you can set `bottle.app().autojson` to `False`.

    #!Python
    @route('/api/status')
    def api_status():
        return {'status':'online', 'servertime':time.time()}

## Static Files

You can directly return file objects, but `static_file()` is the recommended way to serve static files. It automatically guesses a mime-type, adds a `Last-Modified` header, restricts paths to a `root` directory for security reasons and generates appropriate error responses (401 on permission errors, 404 on missing files). It even supports the `If-Modified-Since` header and eventually generates a `304 Not modified` response. You can pass a custom mimetype to disable mimetype guessing.

    #!Python
    from bottle import static_file

    @route('/images/:filename#.*\.png#')
    def send_image(filename):
        return static_file(filename, root='/path/to/image/files', mimetype='image/png')
    
    @route('/static/:filename')
    def send_file(filename):
        return static_file(filename, root='/path/to/static/files')

You can raise the return value of `static_file()` as an exception if you really need to. The raised `HTTPResponse` exception is handled by the Bottle framework. 

## HTTPError, HTTPResponse and Redirects

The `abort(code[, message])` function is used to generate [HTTP error pages][http_code].

    #!Python
    from bottle import route, redirect, abort
    @route('/restricted')
    def restricted():
        abort(401, "Sorry, access denied.")

To redirect a client to a different URL, you can send a `303 See Other` response with the `Location` header set to the new URL. `redirect(url[, code])` does that for you. You may provide a different HTTP status code as a second parameter.

    #!Python
    from bottle import redirect
    @route('/wrong/url')
    def wrong():
        redirect("/right/url")

Both functions interrupt your handler code by raising a `HTTPError` exception.

You can return `HTTPError` exceptions instead of raising them. This is faster than raising and capturing Exceptions, but does exactly the same.

    #!Python
    from bottle import HTTPError

    @route('/denied')
    def denied():
        return HTTPError(401, 'Access denied!')

## Exceptions

All exceptions other than `HTTPResponse` or `HTTPError` will result in a `500 Internal Server Error` response, so they won't crash your WSGI server. You can turn off this behaviour to handle exceptions in your middleware by setting `bottle.app().catchall` to `False`.

# Working with HTTP Requests

Bottle parses the HTTP request data into a thread-save `request` object and provides some useful tools and methods to access this data. Most of the parsing happens on demand, so you won't see any overhead if you don't need the result. Here is a short summary:

  * `request[key]`: A shortcut for `request.environ[key]`
  * `request.environ`: WSGI environment dictionary. Use this with care.
  * `request.app`: Currently used Bottle instance (same as `bottle.app()`)
  * `request.method`: HTTP request-method (GET,POST,PUT,DELETE,...).
  * `request.query_string`: HTTP query-string (http://host/path?query_string)
  * `request.path`: Path string that matched the current route.
  * `request.fullpath`: Full path including the `SCRIPT_NAME` part.
  * `request.url`: The full URL as requested by the client (including `http(s)://` and hostname)
  * `request.input_length` The Content-Length header (if present) as an integer.
  * `request.header`: HTTP header dictionary.
  * `request.GET`: The parsed content of `request.query_string` as a dict. Each value may be a string or a list of strings.
  * `request.POST`: A dict containing parsed form data. Supports URL- and multipart-encoded form data. Each value may be a string, a file or a list of strings or files.
  * `request.COOKIES`: The cookie data as a dict.
  * `request.params`: A dict containing both, `request.GET` and `request.POST` data.
  * `request.body`: The HTTP body of the request as a buffer object.
  * `request.auth`: HTTP authorisation data as a named tuple. (experimental)
  * `request.get_cookie(key[, default])`: Returns a specific cookie and decodes secure cookies. (experimental)


## Cookies

Bottle stores cookies sent by the client in a dictionary called `request.COOKIES`. To create new cookies, the method `response.set_cookie(name, value[, **params])` is used. It accepts additional parameters as long as they are valid cookie attributes supported by [SimpleCookie](http://docs.python.org/library/cookie.html#morsel-objects).

    #!Python
    from bottle import response
    response.set_cookie('key','value', path='/', domain='example.com', secure=True, expires=+500, ...)

To set the `max-age` attribute use the `max_age` name.

TODO: It is possible to store python objects and lists in cookies. This produces signed cookies, which are pickled and unpickled automatically. 

## GET and POST values

Query strings and/or POST form submissions are parsed into dictionaries and made
available as `request.GET` and `request.POST`. Multiple values per
key are possible, so each value of these dictionaries may contain a string
or a list of strings.

You can use `.getall(key)` to get all values, or `.get(key[, default])` if you expect only one value. `getall` returns a list, `get` returns a string.

    #!Python
    from bottle import route, request
    @route('/search', method='POST')
    def do_search():
        query = request.POST.get('query', '').strip()
        if not query:
            return "You didn't supply a search query."
        else:
            return 'You searched for %s.' % query


## File Uploads

Bottle handles file uploads similar to normal POST form data.
Instead of strings, you will get file-like objects. These objects
have two primary attributes: `file` is a file object that can be
used to read it, and `value`, which will read the file and return
it as a string.

    #!Python
    from bottle import route, request
    @route('/upload', method='POST')
    def do_upload():
        datafile = request.POST.get('datafile')
        return datafile.file.read()

Here is an example HTML Form for file uploads

    #!html
    <form action="/upload" method="post" enctype="multipart/form-data">
      <input name="datafile" type="file" />
    </form>



# Templates

Bottle uses its own little template engine by default. You can use a template by
calling `template(template_name, **template_arguments)` and returning
the result.

    #!Python
    @route('/hello/:name')
    def hello(name):
        return template('hello_template', username=name)

This will load the template `hello_template.tpl` with the `username` variable set to the URL `:name` part and return the result as a string.

The `hello_template.tpl` file could look like this:

    #!html
    <h1>Hello {{username}}</h1>
    <p>How are you?</p>




## Template search path

The list `bottle.TEMPLATE_PATH` is used to map template names to actual 
file names. By default, this list contains `['./%s.tpl', './views/%s.tpl']`.




## Template caching

Templates are cached in memory after compilation. Modifications made to 
the template file will have no affect until you clear the template 
cache. Call `bottle.TEMPLATES.clear()` to do so.




## Template Syntax

The template syntax is a very thin layer around the Python language. 
It's main purpose is to ensure correct indention of blocks, so you 
can format your template without worrying about indentions. Here is the 
complete syntax description:

  * `%...` starts a line of python code. You don't have to worry about indentions. Bottle handles that for you.
  * `%end` closes a Python block opened by `%if ...`, `%for ...` or other block statements. Explicitly closing of blocks is required.
  * `{{...}}` prints the result of the included python statement.
  * `%include template_name optional_arguments` allows you to include other templates.
  * Every other line is returned as text.

Example:

    #!html
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




# Key/Value Databases

<div style="color:darkred">Warning: The included key/value database is depreciated.</div> Please switch to a [real](http://code.google.com/p/redis/) [key](http://couchdb.apache.org/) [value](http://www.mongodb.org/) [database](http://docs.python.org/library/anydbm.html).




# Using WSGI and Middleware

A call to `bottle.default_app()` returns your WSGI application. After applying as many WSGI middleware modules as you like, you can tell 
`bottle.run()` to use your wrapped application, instead of the default one.

    #!Python
    from bottle import default_app, run
    app = default_app()
    newapp = YourMiddleware(app)
    run(app=newapp)




## How default_app() works

Bottle creates a single instance of `bottle.Bottle()` and uses it as a default for most of the module-level decorators and the `bottle.run()` routine. 
`bottle.default_app()` returns (or changes) this default. You may, however, create your own instances of `bottle.Bottle()`.

    #!Python
    from bottle import Bottle, run
    mybottle = Bottle()
    @mybottle.route('/')
    def index():
      return 'default_app'
    run(app=mybottle)




# Development
Bottle has two features that may be helpfull during development.

## Debug Mode

In debug mode, bottle is much more verbose and tries to help you finding 
bugs. You should never use debug mode in production environments.

    #!Python
    import bottle
    bottle.debug(True)

This does the following:

  * Exceptions will print a stacktrace
  * Error pages will contain that stacktrace
  * Templates will not be cached.




## Auto Reloading

During development, you have to restart the server a lot to test your 
recent changes. The auto reloader can do this for you. Every time you 
edit a module file, the reloader restarts the server process and loads 
the newest version of your code. 

    #!Python
    from bottle import run
    run(reloader=True)

How it works: The main process will not start a server, but spawn a new 
child process using the same command line arguments used to start the 
main process. All module level code is executed at least twice! Be 
carefull.

The child process will have `os.environ['BOTTLE_CHILD']` set to `true` 
and start as a normal non-reloading app server. As soon as any of the 
loaded modules changes, the child process is terminated and respawned by 
the main process. Changes in template files will not trigger a reload. 
Please use debug mode to deactivate template caching.

The reloading depends on the ability to stop the child process. If you are
running on Windows or any other operating system not supporting 
`signal.SIGINT` (which raises `KeyboardInterrupt` in Python), 
`signal.SIGTERM` is used to kill the child. Note that exit handlers and 
finally clauses, etc., are not executed after a `SIGTERM`.




# Deployment

Bottle uses the build-in `wsgiref.SimpleServer` by default. This non-threading
HTTP server is perfectly fine for development and early production,
but may become a performance bottleneck when server load increases.

There are three ways to eliminate this bottleneck:

  * Use a multi-threaded server adapter
  * Spread the load between multiple bottle instances
  * Do both




## Multi-Threaded Server

The easiest way to increase performance is to install a multi-threaded and
WSGI-capable HTTP server like [Paste][paste], [flup][flup], [cherrypy][cherrypy]
or [fapws3][fapws3] and use the corresponding bottle server-adapter.

    #!Python
    from bottle import PasteServer, FlupServer, FapwsServer, CherryPyServer
    bottle.run(server=PasteServer) # Example
    
If bottle is missing an adapter for your favorite server or you want to tweak
the server settings, you may want to manually set up your HTTP server and use
`bottle.default_app()` to access your WSGI application.

    #!Python
    def run_custom_paste_server(self, host, port):
        myapp = bottle.default_app()
        from paste import httpserver
        httpserver.serve(myapp, host=host, port=port)




## Multiple Server Processes

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
  * It takes a lot of memory to run several copies of Python and Bottle 
at the same time.

One of the fastest load balancer available is [pound](http://www.apsis.ch/pound/) but most common web servers have a proxy-module that can do the work just fine.

I'll add examples for [lighttpd](http://www.lighttpd.net/) and 
[Apache](http://www.apache.org/) web servers soon.




## Apache mod_wsgi

Instead of running your own HTTP server from within Bottle, you can 
attach Bottle applications to an [Apache server][apache] using 
[mod_wsgi][] and Bottles WSGI interface.

All you need is an `app.wsgi` file that provides an 
`application` object. This object is used by mod_wsgi to start your 
application and should be a WSGI conform Python callable.

    #!Python
    # File: /var/www/yourapp/app.wsgi
    
    # Change working directory so relative paths (and template lookup) work again
    os.chdir(os.path.dirname(__file__))
    
    import bottle
    # ... add or import your bottle app code here ...
    # Do NOT use bottle.run() with mod_wsgi
    application = bottle.default_app()

The Apache configuration may look like this:

    #!ApacheConf
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




## Google AppEngine

I didn't test this myself but several Bottle users reported that this 
works just fine.

    #!Python
    import bottle
    from google.appengine.ext.webapp import util 
    # ... add or import your bottle app code here ...
    # Do NOT use bottle.run() with AppEngine
    util.run_wsgi_app(bottle.default_app())




## Good old CGI

CGI is slow as hell, but it works.

    #!Python
    import bottle
    # ... add or import your bottle app code here ...
    bottle.run(server=bottle.CGIServer)


