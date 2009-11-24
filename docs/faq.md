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
        'session.data_dir': './data'
    }
    app = SessionMiddleware(app, session_opts)

    @bottle.route('/test')
    def test():
      s = bottle.request.environ.get('beaker.session')
      s['test'] = s.get('test',0) + 1
      return 'Test counter: %d' % s['test']

    bottle.run(app=app)






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

