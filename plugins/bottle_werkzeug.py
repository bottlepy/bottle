# -*- coding: utf-8 -*-
"""
This plugin adds support for werkzeugs Response objects and HTTPExceptions
and provides a werkzeug.Request() instance to all callbacks as a positional
argument. See: http://werkzeug.pocoo.org/

Example:

import werkzeug
import bottle

bottle.install('werkzeug')

@bottle.route('/hello/:name')
def say_hello(request, name):
    greet = {'en':'Hello', 'de':'Hallo', 'fr':'Bonjour'}
    language = request.accept_language.best_match(greet.keys())
    if language:
        return werkzeug.Response('%s %s!' % (greet[language], name))
    else:
        raise werkzeug.exceptions.NotAcceptable()

"""


__autor__ = "Marcel Hellkamp"
__version__ = '0.1'
__licence__ = 'MIT'

import werkzeug
import bottle

class WerkzeugPlugin(bottle.BasePlugin):
    """ This plugin adds support for werkzeugs Response objects and
        HTTPExceptions and provides a werkzeug.Request() instance to all
        callbacks as a positional argument. """

    plugin_name = 'werkzeug'

    def setup(self, app, request_class=werkzeug.Request, **config):
        self.app = app
        self.request_factory = request_class
        self.config = config

    def wrap(self, callback):
        def wrapper(*a, **ka):
            environ = bottle.request.environ
            response = bottle.response
            a.insert(0, self.build_request(environ))
            try:
                rv = callback(*a, **ka)
            except werkzeug.exceptions.HTTPException, e:
                rv = e.get_response(environ)
            if isinstance(rv, werkzeug.BaseResponse):
                rv = bottle.HTTPResponse(rv.iter_encoded(), rv.status_code, rv.header_list)
            return rv
        return wrapper

    def build_request(self, environ):
        return self.request_factory(environ, **self.config)
