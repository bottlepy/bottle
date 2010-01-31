[TOC]

# Frequently Asked Questions

[beaker]: http://beaker.groovie.org/

## How to implement sessions?

There is no build in support for sessions because there is no *right*
way to do it. Depending on requirements and environment you could use [beaker][]
middleware with a fitting backend or implement it yourself.

Here is an example for beaker sessions with a file-based backend.

    #!Python
    import bottle
    from beaker.middleware import SessionMiddleware

    app = bottle.default_app()
    session_opts = {
        'session.type': 'file',
        'session.cookie_expires': 300,
        'session.data_dir': './data',
        'session.auto': True
    }
    app = SessionMiddleware(app, session_opts)

    @bottle.route('/test')
    def test():
      s = bottle.request.environ.get('beaker.session')
      s['test'] = s.get('test',0) + 1
      s.save()
      return 'Test counter: %d' % s['test']

    bottle.run(app=app)



## How to use a debugging middleware?

Bottle catches all Exceptions raised in your app code, so your WSGI server won't crash. If you need exceptions to propagate to a debugging middleware, you can turn off this behaviour.

    #!Python
    import bottle
    app = bottle.default_app() # or bottle.app() since 0.7
    app.catchall = False
    myapp = DebuggingMiddleware(app)
    bottle.run(app=myapp)

Now, bottle only catches its own exceptions (`HTTPError`, `HTTPResponse` and `BottleException`) and your middleware can handle the rest.




## How to call a WSGI app from within bottle

This is not the recommend way (you should use a middleware in front of bottle to do this) but you can call other WSGI applications from within your bottle app and let bottle act as a pseudo-middleware. Here is an example:

    #!Python
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
                response.header.append(key, value) # or .add_header() with bottle < 0.7
      return app(new_environ, start_response)

Again, this is not the recommend way to implement subprojects. It is only here because many people asked for this and to show how bottle maps to WSGI.

## How to ignore tailing slashes?

Bottle does not ignore tailing slashes by default. 
To handle URLs like `/example` and `/example/` the same, 
you could add two `@route` decorators

    #!Python
    @route('/test')
    @route('/test/')
    def test(): pass

or use regular expressions in dynamic routes

    #!Python
    @route('/test/?')
    def test(): pass

or add a WSGI middleware to strips tailing '/' from URLs

    #!Python
    class StripPathMiddleware(object):
      def __init__(self, app):
        self.app = app
      def __call__(self, e, h):
        e['PATH_INFO'] = e['PATH_INFO'].rstrip('/')
        return self.app(e,h)
    
    app = bottle.default_app()
    app = StripPathMiddleware(app)
    bottle.run(app=app)






## mod_python and "Template Not Found"?

Bottle searches in "./" and "./views/" for templates. In a mod_python
environment, the working directory ('.') depends on your Apache settings. You
should add an absolute path to the template search path

    #!Python
    bottle.TEMPLATE_PATH.insert(0,'/absolut/path/to/templates/')

or change the working directory

    #!Python
    os.chdir(os.path.dirname(__file__))

so bottle searches the right paths.

