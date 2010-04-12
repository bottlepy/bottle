.. module:: bottle

.. _beaker: http://beaker.groovie.org/
.. _mod_python: http://www.modpython.org/
.. _mod_wsgi: http://code.google.com/p/modwsgi/
.. _werkzeug: http://werkzeug.pocoo.org/documentation/dev/debug.html
.. _paste: http://pythonpaste.org/modules/evalexception.html
.. _pylons: http://pylonshq.com/

==========================
Frequently Asked Questions
==========================

About Bottle
============

Is bottle suitable for complex applications?
---------------------------------------------

Bottle is a *micro* framework designed for prototyping and building small web applications and services. It stays out of your way and allows you to get things done fast, but misses some advanced features and ready-to-use solutions found in other frameworks (MVC, ORM, Form validation, scaffolding, XML-RPC). Although it *is* possible to add these features and build complex applications with Bottle, you should consider using a full-stack Web Framework like pylons_ or paste_ instead.



How do I ...?
=============




Sessions
--------------------------------------------------------------------------------

There is no build in support for sessions because there is no *right* way to do it (in a micro framework). Depending on requirements and environment you could use beaker_ middleware with a fitting backend or implement it yourself. Here is an example for beaker sessions with a file-based backend::

    import bottle
    from beaker.middleware import SessionMiddleware

    session_opts = {
        'session.type': 'file',
        'session.cookie_expires': 300,
        'session.data_dir': './data',
        'session.auto': True
    }
    app = SessionMiddleware(bottle.app(), session_opts)

    @bottle.route('/test')
    def test():
      s = bottle.request.environ.get('beaker.session')
      s['test'] = s.get('test',0) + 1
      s.save()
      return 'Test counter: %d' % s['test']

    bottle.run(app=app)

Debugging Middleware
--------------------------------------------------------------------------------

Bottle catches all Exceptions raised in your app code to prevent your WSGI server from crashing. If the build-in :func:`debug` mode is not enough and you need exceptions to propagate to a debugging middleware, you can turn off this behaviour::

    import bottle
    app = bottle.app() 
    app.catchall = False #Now most exceptions are re-raised within bottle.
    myapp = DebuggingMiddleware(app) #Replace this with a middleware of your choice (see below)
    bottle.run(app=myapp)

Now, bottle only catches its own exceptions (:exc:`HTTPError`, :exc:`HTTPResponse` and :exc:`BottleException`) and your middleware can handle the rest.

The werkzeug_ and paste_ libraries both ship with very powerfull debugging WSGI middleware. Look at :class:`werkzeug.debug.DebuggedApplication` for werkzeug_ and :class:`paste.evalexception.middleware.EvalException` for paste_. They both allow you do inspect the stack and even execute python code within the stack context, so **do not use them in production**.


AuthKit
--------------------------------------------------------------------------------

TODO

Embedding other WSGI Apps
--------------------------------------------------------------------------------

This is not the recommend way (you should use a middleware in front of bottle to do this) but you can call other WSGI applications from within your bottle app and let bottle act as a pseudo-middleware. Here is an example::

    from bottle import request, response, route
    subproject = SomeWSGIApplication()

    @route('/subproject/:subpath#.*#', method='ALL')
    def call_wsgi(subpath):
        new_environ = request.environ.copy()
        new_environ['SCRIPT_NAME'] = new_environ.get('SCRIPT_NAME','') + '/subproject'
        new_environ['PATH_INFO'] = '/' + subpath
        def start_response(status, headerlist):
            response.status = int(status.split()[0])
            for key, value in headerlist:
                response.add_header(key, value)
      return app(new_environ, start_response)

Again, this is not the recommend way to implement subprojects. It is only here because many people asked for this and to show how bottle maps to WSGI.


Ignore tailing slashes
--------------------------------------------------------------------------------

For Bottle, ``/example`` and ``/example/`` are two different routes [1]_. To handle both URLs you can add two ``@route`` decorators::

    @route('/test')
    @route('/test/')
    def test(): return 'Slash? no?'

or add a WSGI middleware that strips tailing slashes from all URLs::

    class StripPathMiddleware(object):
      def __init__(self, app):
        self.app = app
      def __call__(self, e, h):
        e['PATH_INFO'] = e['PATH_INFO'].rstrip('/')
        return self.app(e,h)
    
    app = bottle.app()
    myapp = StripPathMiddleware(app)
    bottle.run(app=appmy)






Common Problems and Pitfalls
============================





"Template Not Found" in mod_wsgi/mod_python
--------------------------------------------------------------------------------

Bottle searches in ``./`` and ``./views/`` for templates. In a mod_python_ or mod_wsgi_ environment, the working directory (``./``) depends on your Apache settings. You should add an absolute path to the template search path::

    bottle.TEMPLATE_PATH.insert(0,'/absolut/path/to/templates/')

or change the working directory::

    os.chdir(os.path.dirname(__file__))

so bottle searches the right paths.

Dynamic Routes and Slashes
--------------------------------------------------------------------------------

In :ref:`dynamic route syntax <tutorial-dynamic-routes>`, a placeholder token (``:name``) matches everything up to the next slash. This equals to ``[^/]+`` in regular expression syntax. To accept slashes too, you have to add a custom regular pattern to the placeholder. An example: ``/images/:filepath#.*#`` would match ``/images/icons/error.png`` but ``/images/:filename`` won't.






.. rubric:: Footnotes

.. [1] Because they are. See <http://www.ietf.org/rfc/rfc3986.txt>

