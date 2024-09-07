.. currentmodule:: bottle

.. _beaker: https://beaker.readthedocs.io/en/latest/
.. _mod_python: http://www.modpython.org/
.. _mod_wsgi: http://code.google.com/p/modwsgi/
.. _paste: https://pythonpaste.readthedocs.io/
.. _pylons: https://pylonsproject.org/
.. _gevent: http://www.gevent.org/
.. _heroku: http://heroku.com
.. _django: https://www.djangoproject.com/
.. _werkzeug: https://werkzeug.palletsprojects.com/en/3.0.x/

==================
F.A.Q.
==================

This is a loosely ordered collection of frequently asked questions, solutions for common problems, tips and other bits of knowledge. 

General questions
===========================

Is bottle suitable for complex applications?
---------------------------------------------

Bottle is first and foremost a *micro* framework. It is small, fast, easy to learn, stays out of your way and provides just enough functionality to get you started. This is perfect for prototyping, weekend projects, small applications, REST APIs or micro services, but you'll have to get your hands dirty at some point. If there is no :doc:`plugin <plugins/list>` available for the feature you need, you'll have to write some glue code yourself. But that's not as bad as it sounds. Bottle is small and straight forward. Unlike most other frameworks, you can actually find answers by reading its code. If you want to really understand and fully gasp your tech stack, then bottle is for you. But if you have tight deadlines and do not want to deal with any details, a more complete full-stack framework like django_ may be a better choice.

What about Flask?
---------------------------------------------

Flask was heavily inspired by Bottle (`* <https://github.com/bottlepy/bottle/issues/1158#issuecomment-526602488>`_) and looks very similar on the surface, but took some very different design decisions. Most importantly, Flask is built on top of other libraries (e.g. Werkzeug, Jinja, Click and many more) which makes Flask itself small, but the actual code required to serve a single request is huge in comparison. I would not call it a *micro* framework at this point, but that's just my personal opinion. If you prefer Flask, go for it.


Common errors and pitfalls
==========================

"Template Not Found" in mod_wsgi/mod_python
--------------------------------------------------------------------------------

Bottle searches in ``./`` and ``./views/`` for templates. In a mod_python_ or mod_wsgi_ environment, the working directory (``./``) depends on your Apache settings. You should add an absolute path to the template search path::

    bottle.TEMPLATE_PATH.insert(0,'/absolut/path/to/templates/')

so bottle searches the right paths.

Dynamic Routes and Slashes
--------------------------------------------------------------------------------

In :ref:`dynamic route syntax <tutorial-dynamic-routes>`, a placeholder token (``<name>``) matches everything up to the next slash. This equals to ``[^/]+`` in regular expression syntax. To accept slashes too, you have to add a custom regular pattern to the placeholder. An example: ``/images/<filepath:path>`` would match ``/images/icons/error.png`` but ``/images/<filename>`` won't.

Problems with reverse proxies
--------------------------------------------------------------------------------

Redirects and url-building only works if bottle knows the public address and location of your application. If you run bottle locally behind a reverse proxy or load balancer, some information might get lost along the way. For example, the ``wsgi.url_scheme`` value or the ``Host`` header might reflect the local request by your proxy, not the real request by the client. Here is a small WSGI middleware snippet that helps to fix these values::

  def fix_environ_middleware(app):
    def fixed_app(environ, start_response):
      environ['wsgi.url_scheme'] = 'https'
      environ['HTTP_X_FORWARDED_HOST'] = 'example.com'
      return app(environ, start_response)
    return fixed_app

  app = bottle.default_app()    
  app.wsgi = fix_environ_middleware(app.wsgi)
  


Recieps for common tasks
============================


This is a collection of code snippets and examples for common use cases. 

Keeping track of Sessions
----------------------------

There is no built-in support for sessions because there is no *right* way to do it (in a micro framework). Depending on requirements and environment you could use beaker_ middleware with a fitting backend or implement it yourself. Here is an example for beaker sessions with a file-based backend::

    from bottle import Bottle, request
    from beaker.middleware import SessionMiddleware

    app = Bottle()

    session_opts = {
        'session.type': 'file',
        'session.cookie_expires': 300,
        'session.data_dir': './data',
        'session.auto': True
    }
    app = SessionMiddleware(app, session_opts)

    @app.route('/test')
    def test():
      s = request['beaker.session']
      s['test'] = s.get('test',0) + 1
      s.save()
      return 'Test counter: %d' % s['test']

    app.run()

WARNING: Beaker's SessionMiddleware is not thread safe.  If two concurrent requests modify the same session at the same time, one of the updates might get lost. For this reason, sessions should only be populated once and treated as a read-only store after that. If you find yourself updating sessions regularly, and don't want to risk losing any updates, think about using a real database instead or seek alternative session middleware libraries.


Debugging with Style: Debugging Middleware
--------------------------------------------------------------------------------

Bottle catches all Exceptions raised in your app code to prevent your WSGI server from crashing. If the built-in :func:`debug` mode is not enough and you need exceptions to propagate to a debugging middleware, you can turn off this behaviour::

    import bottle
    app = bottle.Bottle() 
    app.catchall = False  # Now most exceptions are re-raised within bottle.
    myapp = DebuggingMiddleware(app) #Replace this with a middleware of your choice (see below)
    bottle.run(app=myapp)

Now, bottle only catches its own exceptions (:exc:`HTTPError`, :exc:`HTTPResponse` and :exc:`BottleException`) and your middleware can handle the rest.

The werkzeug_ and paste_ libraries both ship with very powerful debugging WSGI middleware. Look at :class:`werkzeug.debug.DebuggedApplication` for werkzeug_ and :class:`paste.evalexception.middleware.EvalException` for paste_. They both allow you do inspect the stack and even execute python code within the stack context, so **do not use these in production**!


Unit-Testing Bottle Applications
--------------------------------------------------------------------------------

Unit-testing is usually performed against methods defined in your web application without running a WSGI environment.

A simple example::

    import bottle
    
    @bottle.route('/')
    def index():
        return 'Hi!'

    if __name__ == '__main__':
        bottle.run()

Test script::

    import mywebapp
    
    def test_webapp_index():
        assert mywebapp.index() == 'Hi!'

In the example the Bottle route() method is never executed - only index() is tested.

If the code being tested requires access to ``bottle.request`` you can mock it using `Boddle <https://github.com/keredson/boddle>`_::

    import bottle
    
    @bottle.route('/')
    def index():
        return 'Hi %s!' % bottle.request.params['name']

Test script::

    import mywebapp
    from boddle import boddle
    
    def test_webapp_index():
        with boddle(params={'name':'Derek'}):
            assert mywebapp.index() == 'Hi Derek!'


Functional Testing Bottle Applications
--------------------------------------------------------------------------------

Any HTTP-based testing system can be used with a running WSGI server, but some testing frameworks work more intimately with WSGI, and provide the ability the call WSGI applications in a controlled environment, with tracebacks and full use of debugging tools.

Example using `WebTest <https://docs.pylonsproject.org/projects/webtest/en/latest/index.html>`_::

    from webtest import TestApp
    import myapp

    def test_functional_login_logout():
        app = TestApp(myapp.app)

        app.post('/login', {'user': 'foo', 'pass': 'bar'}) # log in and get a cookie

        assert app.get('/admin').status == '200 OK'        # fetch a page successfully

        assert app.get('/logout').status_code == 200        # log out
        app.reset()                                        # drop the cookie

        # fetch the same page, unsuccessfully
        assert app.get('/admin', expect_errors=True).status == '401 Unauthorized'


Ignore trailing slashes
--------------------------------------------------------------------------------

For Bottle, ``/example`` and ``/example/`` are two different routes [1]_. To treat both URLs the same you can add two ``@route`` decorators::

    @route('/test')
    @route('/test/')
    def test(): return 'Slash? no?'

add a WSGI middleware that strips trailing slashes from all URLs::

    class StripPathMiddleware(object):
      def __init__(self, app):
        self.app = app
      def __call__(self, e, h):
        e['PATH_INFO'] = e['PATH_INFO'].rstrip('/')
        return self.app(e,h)
    
    app = bottle.app()
    myapp = StripPathMiddleware(app)
    bottle.run(app=myapp)

or add a ``before_request`` hook to strip the trailing slashes::

    @hook('before_request')
    def strip_path():
        request['PATH_INFO'] = request['PATH_INFO'].rstrip('/')

.. rubric:: Footnotes

.. [1] Because they are. See <http://www.ietf.org/rfc/rfc3986.txt>


Keep-alive requests
-------------------

.. note::

    For a more detailed explanation, see :doc:`async`.

Several "push" mechanisms like XHR multipart need the ability to write response data without closing the connection in conjunction with the response header "Connection: keep-alive". WSGI does not easily lend itself to this behavior, but it is still possible to do so in Bottle by using the gevent_ async framework. Here is a sample that works with either the gevent_ HTTP server or the paste_ HTTP server (it may work with others, but I have not tried). Just change ``server='gevent'`` to ``server='paste'`` to use the paste_ server::

    from gevent import monkey; monkey.patch_all()

    import gevent
    from bottle import route, run
    
    @route('/stream')
    def stream():
        yield 'START'
        gevent.sleep(3)
        yield 'MIDDLE'
        gevent.sleep(5)
        yield 'END'
    
    run(host='0.0.0.0', port=8080, server='gevent')

If you browse to ``http://localhost:8080/stream``, you should see 'START', 'MIDDLE', and 'END' show up one at a time (rather than waiting 8 seconds to see them all at once).

Gzip Compression in Bottle
--------------------------

A common feature request is for Bottle to support Gzip compression, which speeds up sites by compressing static resources (like CSS and JS files) during a request.

Supporting Gzip compression is not a straightforward proposition, due to a number of corner cases that crop up frequently. A proper Gzip implementation must:

* Compress on the fly and be fast doing so.
* Do not compress for browsers that don't support it.
* Do not compress files that are compressed already (images, videos).
* Do not compress dynamic files.
* Support two differed compression algorithms (gzip and deflate).
* Cache compressed files that don't change often.
* De-validate the cache if one of the files changed anyway.
* Make sure the cache does not get to big.
* Do not cache small files because a disk seek would take longer than on-the-fly compression.

Because of these requirements, it is the recommendation of the Bottle project that Gzip compression is best handled by the WSGI server Bottle runs on top of. WSGI servers and reverse proxies often provide built-in features that allow transparent compression without changing the application itself.


Using hooks to handle CORS
--------------------------

Hooks are useful to unconditionally do something before or after each
request. For example, if you want to allow Cross-Origin requests for your
entire application, instead of writing a :doc:`plugin <plugins/dev>` you can
use hooks to add the appropiate headers::

    from bottle import hook, response, HTTPResponse

    cors_headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
        # 'Access-Control-Allow-Headers': 'X-Token, ...',
        # 'Access-Control-Expose-Headers': 'X-My-Custom-Header, ...',
        # 'Access-Control-Max-Age': '86400',
        # 'Access-Control-Allow-Credentials': 'true',
    }

    @hook('before_request')
    def handle_options():
        if request.method == 'OPTIONS':
            # Bypass request routing and immediately return a response
            raise HTTPResponse(headers=cors_headers)

    @hook('after_request')
    def enable_cors():
        for key, value in cors_headers.items():
           response.set_header(key, value)


Using Bottle with Heroku
------------------------

Heroku_, a popular cloud application platform now provides support
for running Python applications on their infrastructure. 

This recipe is based upon the `Heroku Quickstart 
<http://devcenter.heroku.com/articles/quickstart>`_, 
with Bottle specific code replacing the 
`Write Your App <http://devcenter.heroku.com/articles/python#write_your_app>`_ 
section of the `Getting Started with Python on Heroku/Cedar 
<http://devcenter.heroku.com/articles/python>`_ guide::

    import os
    from bottle import route, run

    @route("/")
    def hello_world():
        return "Hello World!"

    run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

Heroku's app stack passes the port that the application needs to
listen on for requests, using the `os.environ` dictionary.
