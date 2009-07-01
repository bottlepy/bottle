Bottle Web Framework
====================

`Bottle` is a simple, fast and useful one-file WSGI-framework. It is not a
full-stack framework with a ton of features, but a useful mirco-framework for
small web-applications that stays out of your way.



Dependencies
------------

`bottle.py` only depends on the Python Standard Library.
If you want to use a HTTP server other than wsgiref.simple_server you may need
cherrypy, flup or paste (your choice)



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

    from bottle import route, run, request, response, send_file, abort

    @route('/')
    def hello_world():
        return 'Hello World!'

    @route('/hello/:name')
    def hello_name(name):
        return 'Hello %s!' % name

    @route('/hello', method='POST')
    def hello_post():
        name = request.POST['name']
        return 'Hello %s!' % name

    @route('/static/:filename#.*#')
    def static_file(filename):
        send_file(filename, root='/path/to/static/files/')

    run(host='localhost', port=8080)



Licence (MIT)
-------------

    Copyright (c) 2009, Marcel Hellkamp.

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

