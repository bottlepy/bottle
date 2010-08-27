# -*- coding: utf-8 -*-
"""
This plugin adds support for werkzeugs Response objects and HTTPExceptions
and provides a werkzeug.Request() instance to all callbacks as a positional
argument. See: http://werkzeug.pocoo.org/

Example:

from .plugins.werkzeug import WerkzeugPlugin
import werkzeug
import bottle

bottle.install(WerkzeugPlugin)

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

from __future__ import absolute_import
import werkzeug
import bottle

class WerkzeugPlugin(BasePlugin):
    """ This plugin adds support for werkzeugs Response objects and
        HTTPExceptions and provides a werkzeug.Request() instance to all
        callbacks as a positional argument. """

    plugin_name = 'werkzeug'

    def setup(app, request_class=werkzeug.Request, **config):
        self.app = app
        self.request_factory = request_class
        self.config = config

    def wrap(callback):
        def wrapper(*a, **ka):
            environ = bottle.request.environ
            response = bottle.response
            self.build_request(environ)
            try:
                rv = callback(*a, **ka)
            except werkzeug.exceptions.HTTPException, e:
                rv = e.get_response(environ)
            if isinstance(a, werkzeug.BaseResponse):
                output, status, headers = rv.get_wsgi_response(environ)
                status = int(status.split()[0])
                return bottle.HTTPResponse(output, status, headers)
            return rv
        return wrapper

    def build_request(self, environ):
        local.request = self.request_class(environ, **self.config)