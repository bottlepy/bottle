# -*- coding: utf-8 -*-
"""
This plugin adds support for :class:`werkzeug.Response`, all kinds of
:exc:`werkzeug.HTTPException` and provides a thread-local instance of
:class:`werkzeug.Request`. It basically turns Bottle into Flask.

The plugin instance doubles as a werkzeug module object, so you don't need to
import werkzeug in your application.

For werkzeug library documentation, see: http://werkzeug.pocoo.org/

Example::

    import bottle
    from bottle.ext.werkzeug import WerkzeugPlugin

    app = bottle.Bottle()
    werkzeug = app.install(WerkzeugPlugin())
    wrequest = werkzueg.request # For the lazy.

    @app.route('/hello/:name')
    def say_hello(name):
        greet = {'en':'Hello', 'de':'Hallo', 'fr':'Bonjour'}
        language = wrequest.accept_languages.best_match(greet.keys())
        if language:
            return werkzeug.Response('%s %s!' % (greet[language], name))
        else:
            raise werkzeug.exceptions.NotAcceptable()

"""


__autor__ = "Marcel Hellkamp"
__version__ = '0.1'
__license__ = 'MIT'

import werkzeug
from werkzeug import *
import bottle

class WerkzeugPlugin(object):
    """ This plugin adds support for :class:`werkzeug.Response`, all kinds of
        :module:`werkzeug.exceptions` and provides a thread-local instance of
        :class:`werkzeug.Request`. It basically turns Bottle into Flask. """

    name = 'werkzeug'

    def __init__(self, request_class=werkzeug.Request, **config):
        self.request_factory = request_class
        self.config = config
        self.app = None

    def setup(self, app):
        self.app = app

    def apply(self, callback, context):
        def wrapper(*a, **ka):
            environ = bottle.request.environ
            bottle.local.werkzueg_request = self.request_factory(environ, **self.config)
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
