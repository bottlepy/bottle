Bottle Web Framework
====================

`Bottle` is a simple, fast and useful one-file WSGI-framework. It is not a
full-stack framework with a ton of features, but a useful mirco-framework for
small web-applications that stays out of your way.

Dependencies
------------

`bottle.py` only depends on stdlib and is tested with python 2.5 and 2.6.
 
Features
--------

  * Handy dictionaries for query-parameter (GET), wsgi.input data (POST) and cookies
    * Parsing happens on demand. No parsing overhead for dicts you're not using
  * Cookie- and HTTP-header manipulation with full featured helper-methods or simple dicts. 
  * A single decorator to bind handler-functions to specific URLs (Routing)
    * Static routes: `/hello/world` --> `say_hello(request)`
    * URL parameter: `/object/:id/:action` --> `do_something(request, id, action)`
      * Parameter validation: `/hello/:name![A-Z][a-z]+!`
      * Full-featured regular expressions: `/hello/(?P<name>[A-Z][a-z]+)`
    * Self optimising routes (frequently used routes are tested first)
  * Exceptions for common HTTP error-codes (NotFoundError, AccessError, ...)
  * Instant redirects (301 and 307)
  * Support for static-files using platform-specific high-performance file-transmission facilities, such as the Unix sendfile()
    * Depends on `wsgi.file_wrapper` provided by your WSGI-Server implementation.
    * Secure by denying access to files not in the specified directory
    * Automatic mime-type guessing
  * Adapter for common WSGI-Server modules
    * Currently supports wsgiref.simple_server (default), cherrypy, flup and paste. More to come...
  * Stays out of your way and does not force you to use:
    * Stiff `/:controller/:action` URL schemes or controller-classes
    * A specific template-engine (mako, cheetah, genshi, string.Template)
    * Specific Models or ORMs (SQLAlchemy, Elixir)
    * A specific Caching-facility (beaker, memcache)
    * But you may use all of these if you want to.

Example
-------

    from bottle import route, run, request, response

    @route('/')
    def hello_world():
        return 'Hello World!'

    @route('/hello/:name')
    def hello_name(name):
        return 'Hello %s!' % name

    @route('/hello', method='POST')
    def hello_post():
        return 'Hello %s!' % request.POST['name']

    @route('/static/:filename#.*#')
    def static_file(filename):
        response.send_file(filename, root='/path/to/static/files/')

    run(host='localhost', port=8080)
    


