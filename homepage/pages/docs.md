[TOC]

Bottle Documentation
====================

This document is a work in progress. If you have questions not answered here,
please file a ticket at bottle's [issue 
tracker](http://github.com/defnull/bottle/issues).

## Basic Routes

Routes are used to map request URLs to callables that generate the response content. Bottle has a `route()` decorator to do that.

    #!Python
    from bottle import route, run
    @route('/hello')
    def hello():
        return "Hello World!"
    run() # This starts the HTTP server

Run this script, visit <http://localhost:8080/hello> and you will see "Hello World!" in your Browser.



### GET, POST, HEAD, ...

The route decorator has an optional keyword argument `method` which defaults to `method='GET'`.
Possible values are `POST`, `PUT`, `DELETE`, `HEAD` or any other HTTP request method you want to listen to.

    #!Python
    from bottle import route, request
    @route('/form/submit', method='POST')
    def form_submit():
        form_data = request.POST
        do_something(form_data)
        return "Done"








## Dynamic Routes

You can extract parts of the URL and create dynamic routes with an easy syntax.

    #!Python
    @route('/hello/:name')
    def hello(name):
        return "Hello %s!" % name

By default, a `:placeholder` matches everything up to the next 
slash. To change that, you can add some regular expression in between `#`s:

    #!Python
    @route('/get_object/:id#[0-9]+#')
    def get(id):
        return "Object ID: %d" % int(id)

or even use full features regular expressions with named groups:

    #!Python
    @route('/get_object/(?P<id>[0-9]+)')
    def get(id):
        return "Object ID: %d" % int(id)

As you can see, URL parameters remain strings, even if they are 
configured to only match digits. You have to explicitly cast them into 
the type you need.

### The @validate() decorator

Bottle offers a handy decorator called `validate()` to check and manipulate URL parameters.
It takes callables as keyword arguments and filters every URL parameter 
through the corresponding callable before they are passed to your 
request handler.

    #!Python
    from bottle import route, validate
    # /test/validate/1/2.3/4,5,6,7
    @route('/test/validate/:i/:f/:csv')
    @validate(i=int, f=float, csv=lambda x: map(int, x.split(',')))
    def validate_test(i, f, csv):
        return "Int: %d, Float:%f, List:%s" % (i, f, repr(csv))

You may raise `ValueError` in your custom callable if the parameter 
does not validate.





## Returning files and JSON

The WSGI specification expects an iterable list of strings and can't handle file
objects or plain strings. Bottle automatically converts them to iterables, so
you don't have to. The following example will work with Bottle, but won't work
with pure WSGI.

    #!Python
    @route('/get_string')
    def get_string():
        return "This is not a list of strings, but a single string"
    @route('/file')
    def get_file():
        return open('some/file.txt','r')

Even dictionaries are allowed. They are converted to
[json](http://de.wikipedia.org/wiki/JavaScript_Object_Notation) and returned
as `Content-Type: application/json`.

    #!Python
    @route('/api/status')
    def api_status():
        return {'status':'online', 'servertime':time.time()}

You can turn off this feature: `bottle.default_app().autojson = False`

## HTTP errors and redirects

    #!Python
    from bottle import redirect, abort
    
    @route('/wrong/url')
    def wrong():
        redirect("/right/url")
    
    @route('/restricted')
    def restricted():
        abort(401, "Sorry, access denied.")


## Static files

    #!Python
    from bottle import send_file
    
    @route('/static/:filename')
    def static_file(filename):
        send_file(filename, root='/path/to/static/files')


## Cookies

Bottle stores cookies sent by the client in a dictionary called `request.COOKIES`. To create new cookies,
the method `response.set_cookie(name, value[, **params])` is used. It accepts additional parameters as long as they are valid 
cookie attributes supported by [SimpleCookie](http://docs.python.org/library/cookie.html#morsel-objects).

    #!Python
    from bottle import response
    response.set_cookie('key','value', path='/', domain='example.com', secure=True, expires=+500, ...)

To set the `max-age` attribute (which is not a valid Python parameter name) you can directly access an instance of 
[cookie.SimpleCookie](http://docs.python.org/library/cookie.html#Cookie.SimpleCookie) in `response.COOKIES`. 

    #!Python
    from bottle import response
    response.COOKIES['key'] = 'value'
    response.COOKIES['key']['max-age'] = 500











## Templates

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

### Template search path

The list `bottle.TEMPLATE_PATH` is used to map template names to actual 
file names. By default, this list contains `['./%s.tpl', './views/%s.tpl']`.

### Template caching

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













## Key/Value Databases

Bottle (>0.4.6) offers a persistent key/value database accessible through the
`bottle.db` module variable. You can use key or attribute syntax to store or
fetch any pickle-able object to the database. Both 
`bottle.db.bucket_name.key_name` and `bottle.db[bucket_name][key_name]` 
will work.

Missing buckets are created on demand. You don't have to check for 
their existence before using them. Just be sure to use alphanumeric 
bucket-names.

The bucket objects behave like mappings (dictionaries), except that 
only strings are allowed for keys and values must be pickle-able. 
Printing a bucket object doesn't print the keys and values, and the 
`items()` and `values()` methods are not supported. Missing keys will raise 
`KeyError` as expected.

### Persistence
During a request live-cycle, all changes are cached in thread-local memory. At
the end of the request, the changes are saved automatically so the next request
will have access to the updated values. Each bucket is stored in a separate file
in `bottle.DB_PATH`. Be sure to allow write-access to this path and use bucket
names that are allowed in filenames.

### Race conditions
You don't have do worry about file corruption but race conditions are still a
problem in multi-threaded or forked environments. You can call
`bottle.db.save()` or `botle.db.bucket_name.save()` to flush the thread-local
memory cache to disk, but there is no way to detect database changes made in
other threads until these threads call `bottle.db.save()` or leave the current
request cycle.

### Example

    #!Python
    from bottle import route, db
    @route('/db/counter')
    def db_counter():
        if 'hits' not in db.counter:
            db.counter.hits = 0
        db['counter']['hits'] += 1
        return "Total hits: %d!" % db.counter.hits










## Using WSGI and Middleware

A call to `bottle.default_app()` returns your WSGI application. After applying as many WSGI middleware modules as you like, you can tell 
`bottle.run()` to use your wrapped application, instead of the default one.

    #!Python
    from bottle import default_app, run
    app = default_app()
    newapp = YourMiddleware(app)
    run(app=newapp)

### How default_app() works

Bottle creates a single instance of `bottle.Bottle()` and uses it as a default for most of the modul-level decorators and the `bottle.run()` routine. 
`bottle.default_app()` returns (or changes) this default. You may, however, create your own instances of `bottle.Bottle()`.

    #!Python
    from bottle import Bottle, run
    mybottle = Bottle()
    @mybottle.route('/')
    def index():
      return 'default_app'
    run(app=mybottle)


## Deployment

Bottle uses the build-in `wsgiref.SimpleServer` by default. This non-threading
HTTP server is perfectly fine for development and early production,
but may become a performance bottleneck when server load increases.

There are three ways to eliminate this bottleneck:

  * Use a multi-threaded server adapter
  * Spread the load between multiple bottle instances
  * Do both

### Multi-Threaded Server

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

### Multiple Server Processes

A single Python process can only utilize one CPU at a time, even if 
there are more CPU cores available. The trick is to balance the load 
between multiple independent Python processes to utilize all of your 
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

### Apache mod_wsgi

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


### Google AppEngine

    #!Python
    import bottle
    from google.appengine.ext.webapp import util 
    # ... add or import your bottle app code here ...
    # Do NOT use bottle.run() with AppEngine
    util.run_wsgi_app(bottle.default_app())

### Good old CGI

CGI is slow as hell, but it works.

    #!Python
    import bottle
    # ... add or import your bottle app code here ...
    bottle.run(server=bottle.CGIServer)

[mako]: http://www.makotemplates.org/
[cherrypy]: http://www.cherrypy.org/
[flup]: http://trac.saddi.com/flup
[paste]: http://pythonpaste.org/
[fapws3]: http://github.com/william-os4y/fapws3
[apache]: http://www.apache.org/
[mod_wsgi]: http://code.google.com/p/modwsgi/
