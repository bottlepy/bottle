"""
This plugin adds support for :class:`werkzeug.Response`, all kinds of
:exc:`werkzeug.exceptions` and provides a thread-local instance of
:class:`werkzeug.Request`. It basically turns Bottle into Flask.

The plugin instance doubles as a werkzeug module object, so you don't need to
import werkzeug in your application.

For werkzeug library documentation, see: http://werkzeug.pocoo.org/

Example::

    import bottle

    app = bottle.Bottle()
    werkzeug = bottle.ext.werkzeug.Plugin()
    app.install(werkzeug)

    req = werkzueg.request # For the lazy.

    @app.route('/hello/:name')
    def say_hello(name):
        greet = {'en':'Hello', 'de':'Hallo', 'fr':'Bonjour'}
        language = req.accept_languages.best_match(greet.keys())
        if language:
            return werkzeug.Response('%s %s!' % (greet[language], name))
        else:
            raise werkzeug.exceptions.NotAcceptable()

"""


__autor__ = "Marcel Hellkamp"
__version__ = '0.1'
__license__ = 'MIT'

### CUT HERE (see setup.py)

import werkzeug
from werkzeug import *
import bottle


class WerkzeugDebugger(DebuggedApplication):
    """ A subclass of :class:`werkzeug.debug.DebuggedApplication` that obeys the
        :data:`bottle.DEBUG` setting. """

    def __call__(self, environ, start_response):
        if bottle.DEBUG:
            return DebuggedApplication.__call__(self, environ, start_response)
        return self.app(environ, start_response)


class WerkzeugPlugin(object):
    """ This plugin adds support for :class:`werkzeug.Response`, all kinds of
        :module:`werkzeug.exceptions` and provides a thread-local instance of
        :class:`werkzeug.Request`. It basically turns Bottle into Flask. """

    name = 'werkzeug'
    api  = 2

    def __init__(self, evalex=False, request_class=werkzeug.Request,
                       debugger_class=WerkzeugDebugger):
        self.request_class = request_class
        self.debugger_class = debugger_class
        self.evalex=evalex
        self.app = None

    def setup(self, app):
        self.app = app
        if self.debugger_class:
            app.wsgi = self.debugger_class(app.wsgi, evalex=self.evalex)
            app.catchall = False

    def apply(self, callback, route):
        def wrapper(*a, **ka):
            environ = bottle.request.environ
            bottle.local.werkzueg_request = self.request_class(environ)
            try:
                rv = callback(*a, **ka)
            except werkzeug.exceptions.HTTPException, e:
                rv = e.get_response(environ)
            if isinstance(rv, werkzeug.BaseResponse):
                rv = bottle.HTTPResponse(rv.iter_encoded(), rv.status_code, rv.header_list)
            return rv
        return wrapper

    @property
    def request(self):
        ''' Return a local proxy to the current :class:`werkzeug.Request`
            instance.'''
        return werkzeug.LocalProxy(lambda: bottle.local.werkzueg_request)

    def __getattr__(self, name):
        ''' Convenient access to werkzeug module contents. '''
        return getattr(werkzeug, name)


Plugin = WerkzeugPlugin
