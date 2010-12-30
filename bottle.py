# -*- coding: utf-8 -*-
"""
Bottle is a fast and simple micro-framework for small web applications. It
offers request dispatching (Routes) with url parameter support, templates,
a built-in HTTP Server and adapters for many third party WSGI/HTTP-server and
template engines - all in a single file and with no dependencies other than the
Python Standard Library.

Homepage and documentation: http://bottle.paws.de/

Copyright (c) 2010, Marcel Hellkamp.
License: MIT (see LICENSE.txt for details)
"""

from __future__ import with_statement

__author__ = 'Marcel Hellkamp'
__version__ = '0.9.dev'
__license__ = 'MIT'

import base64
import cgi
import email.utils
import functools
import hmac
import httplib
import itertools
import mimetypes
import os
import re
import subprocess
import sys
import tempfile
import thread
import threading
import time
import warnings

from Cookie import SimpleCookie
from tempfile import TemporaryFile
from traceback import format_exc
from urllib import quote as urlquote
from urlparse import urlunsplit, urljoin

try: from collections import MutableMapping as DictMixin
except ImportError: # pragma: no cover
    from UserDict import DictMixin

try: from urlparse import parse_qs
except ImportError: # pragma: no cover
    from cgi import parse_qs

try: import cPickle as pickle
except ImportError: # pragma: no cover
    import pickle

try: from json import dumps as json_dumps
except ImportError: # pragma: no cover
    try: from simplejson import dumps as json_dumps
    except ImportError: # pragma: no cover
        try: from django.utils.simplejson import dumps as json_dumps
        except ImportError: # pragma: no cover
            json_dumps = None

if sys.version_info >= (3,0,0): # pragma: no cover
    # See Request.POST
    from io import BytesIO
    from io import TextIOWrapper
    class NCTextIOWrapper(TextIOWrapper):
        ''' Garbage collecting an io.TextIOWrapper(buffer) instance closes the
            wrapped buffer. This subclass keeps it open. '''
        def close(self): pass
    def touni(x, enc='utf8'):
        """ Convert anything to unicode """
        return str(x, encoding=enc) if isinstance(x, bytes) else str(x)
else:
    from StringIO import StringIO as BytesIO
    bytes = str
    NCTextIOWrapper = None
    def touni(x, enc='utf8'):
        """ Convert anything to unicode """
        return x if isinstance(x, unicode) else unicode(str(x), encoding=enc)

def tob(data, enc='utf8'):
    """ Convert anything to bytes """
    return data.encode(enc) if isinstance(data, unicode) else bytes(data)

# Convert strings and unicode to native strings
if sys.version_info >= (3,0,0):
    tonat = touni
else:
    tonat = tob
tonat.__doc__ = """ Convert anything to native strings """


# Backward compatibility
def depr(message, critical=False):
    if critical: raise DeprecationWarning(message)
    warnings.warn(message, DeprecationWarning, stacklevel=3)


# Small helpers

def makelist(data):
    if isinstance(data, (tuple, list, set, dict)): return list(data)
    elif data: return [data]
    else: return []


class cached_property(object):
    """ Decorator to create properties that are computed only once per instance
        and then saved as normal attributes. Works for any new-style classes
        with a __dict__ (no slots). """
    def __init__(self, func, name=None, doc=None):
        self.__name__ = name or func.__name__
        self.__doc__ = doc or func.__doc__
        self.__module__ = func.__module__
        self.func = func
    def __get__(self, obj, type=None):
        if obj is None: return self
        value = obj.__dict__[self.__name__] = self.func(obj)
        return value



###############################################################################
# Exceptions and Events ########################################################
###############################################################################

class BottleException(Exception):
    """ A base class for exceptions used by bottle. """
    pass


class HTTPResponse(BottleException):
    """ Used to break execution and immediately finish the response """
    def __init__(self, output='', status=200, header=None):
        super(BottleException, self).__init__("HTTP Response %d" % status)
        self.status = int(status)
        self.output = output
        self.headers = HeaderDict(header) if header else None

    def apply(self, response):
        if self.headers:
            for key, value in self.headers.iterallitems():
                response.headers[key] = value
        response.status = self.status


class HTTPError(HTTPResponse):
    """ Used to generate an error page """
    def __init__(self, code=500, output='Unknown Error', exception=None, traceback=None, header=None):
        super(HTTPError, self).__init__(output, code, header)
        self.exception = exception
        self.traceback = traceback

    def __repr__(self):
        return template(ERROR_PAGE_TEMPLATE, e=self)






###############################################################################
# Routing ######################################################################
###############################################################################

class RouteError(BottleException):
    """ This is a base class for all routing related exceptions """


class RouteSyntaxError(RouteError):
    """ The route parser found something not supported by this router """


class RouteBuildError(RouteError):
    """ The route could not been built """


class Route(object):
    ''' Represents a single route and can parse the dynamic route syntax '''
    syntax = re.compile(r'(?<!\\):([a-zA-Z_][a-zA-Z_0-9]*)?(?:#(.*?)#)?')
    default = '[^/]+'

    def __init__(self, route, target=None, name=None, static=False):
        """ Create a Route. The route string may contain `:key`,
            `:key#regexp#` or `:#regexp#` tokens for each dynamic part of the
            route. These can be escaped with a backslash in front of the `:`
            and are completely ignored if static is true. A name may be used
            to refer to this route later (depends on Router)
        """
        self.route = route.replace('\\:',':')
        self.target = target
        self.name = name
        self.realroute = route.replace(':','\\:') if static else route
        self.tokens = self.syntax.split(self.realroute)

    def group_re(self):
        ''' Return a regexp pattern with named groups '''
        out = ''
        for i, part in enumerate(self.tokens):
            if i%3 == 0:   out += re.escape(part.replace('\:',':'))
            elif i%3 == 1: out += '(?P<%s>' % part if part else '(?:'
            else:          out += '%s)' % (part or self.default)
        return out
        
    def flat_re(self):
        ''' Return a regexp pattern with non-grouping parentheses '''
        rf = lambda m: m.group(0) if len(m.group(1)) % 2 else m.group(1) + '(?:'
        return re.sub(r'(\\*)(\(\?P<[^>]*>|\((?!\?))', rf, self.group_re())

    def format_str(self):
        ''' Return a format string with named fields. '''
        out, c = '', 0
        for i, part in enumerate(self.tokens):
            if i%3 == 0:  out += part.replace('\\:',':').replace('%','%%')
            elif i%3 == 1:
                if not part: part = 'anon%d' % c; c+=1
                out += '%%(%s)s' % part
        return out

    @property
    def static(self):
        return len(self.tokens) == 1

    def __repr__(self):
        return "<Route(%s) />" % repr(self.realroute)

    def __eq__(self, other):
        return (self.realroute) == (other.realroute)


class Router(object):
    ''' A route associates a string (e.g. URL) with an object (e.g. function)
        Some dynamic routes may extract parts of the string and provide them as
        a dictionary. This router matches a string against multiple routes and
        returns the associated object along with the extracted data.
    '''

    def __init__(self):
        self.routes  = []  # List of all installed routes
        self.named   = {}  # Cache for named routes and their format strings
        self.static  = {}  # Cache for static routes
        self.dynamic = []  # Search structure for dynamic routes
        self.compiled = False

    def add(self, route, target=None, **ka):
        """ Add a route->target pair or a :class:`Route` object to the Router.
            Return the Route object. See :class:`Route` for details.
        """
        if not isinstance(route, Route):
            route = Route(route, target, **ka)
        if self.get_route(route):
            return RouteError('Route %s is not uniqe.' % route)
        self.routes.append(route)
        self.compiled, self.named, self.static, self.dynamic = False, {}, {}, []
        return route

    def get_route(self, route, target=None, **ka):
        ''' Get a route from the router by specifying either the same
            parameters as in :meth:`add` or comparing to an instance of
            :class:`Route`. Note that not all parameters are considered by the
            compare function. '''
        if not isinstance(route, Route):
            route = Route(route, **ka)
        for known in self.routes:
            if route == known:
                return known
        return None

    def match(self, uri):
        ''' Match an URI and return a (target, urlargs) tuple '''
        if uri in self.static:
            return self.static[uri], {}
        for combined, subroutes in self.dynamic:
            match = combined.match(uri)
            if not match: continue
            target, args_re = subroutes[match.lastindex - 1]
            args = args_re.match(uri).groupdict() if args_re else {}
            return target, args
        if not self.compiled: # Late check to reduce overhead on hits
            self.compile() # Compile and try again.
            return self.match(uri)
        return None, {}

    def build(self, _name, **args):
        ''' Build an URI out of a named route and values for the wildcards. '''
        try:
            return self.named[_name] % args
        except KeyError, e:
            if not self.compiled: # Late check to reduce overhead on hits
                self.compile() # Compile and try again.
                return self.build(_name, **args)
            if _name not in self.named:
                raise RouteBuildError("No route found with name '%s'." % _name)
            raise RouteBuildError("Missing argument: %s." % e.args[0])

    def compile(self):
        ''' Build the search structures. Call this before actually using the
            router.'''
        self.named = {}
        self.static = {}
        self.dynamic = []
        for route in self.routes:
            if route.name:
                self.named[route.name] = route.format_str()
            if route.static:
                self.static[route.route] = route.target
                continue
            gpatt = route.group_re()
            fpatt = route.flat_re()
            try:
                gregexp = re.compile('^(%s)$' % gpatt) if '(?P' in gpatt else None
                combined = '%s|(^%s$)' % (self.dynamic[-1][0].pattern, fpatt)
                self.dynamic[-1] = (re.compile(combined), self.dynamic[-1][1])
                self.dynamic[-1][1].append((route.target, gregexp))
            except (AssertionError, IndexError), e: # AssertionError: Too many groups
                self.dynamic.append((re.compile('(^%s$)'%fpatt),
                                    [(route.target, gregexp)]))
            except re.error, e:
                raise RouteSyntaxError("Could not add Route: %s (%s)" % (route, e))
        self.compiled = True

    def __eq__(self, other):
        return self.routes == other.routes






###############################################################################
# Application Object ###########################################################
###############################################################################

class Bottle(object):
    """ WSGI application """

    def __init__(self, catchall=True, autojson=True, config=None):
        """ Create a new bottle instance.
            You usually don't do that. Use `bottle.app.push()` instead.
        """
        self.routes = Router()
        self.mounts = {}
        self.error_handler = {}
        self.catchall = catchall
        self.config = config or {}
        self.serve = True
        self.castfilter = []
        if autojson and json_dumps:
            self.add_filter(dict, dict2json)
        self.hooks = {'before_request': [], 'after_request': []}

    def optimize(self, *a, **ka):
        depr("Bottle.optimize() is obsolete.")

    def mount(self, app, script_path):
        ''' Mount a Bottle application to a specific URL prefix '''
        if not isinstance(app, Bottle):
            raise TypeError('Only Bottle instances are supported for now.')
        script_path = '/'.join(filter(None, script_path.split('/')))
        path_depth = script_path.count('/') + 1
        if not script_path:
            raise TypeError('Empty script_path. Perhaps you want a merge()?')
        for other in self.mounts:
            if other.startswith(script_path):
                raise TypeError('Conflict with existing mount: %s' % other)
        @self.route('/%s/:#.*#' % script_path, method="ANY")
        def mountpoint():
            request.path_shift(path_depth)
            return app.handle(request.path, request.method)
        self.mounts[script_path] = app

    def add_filter(self, ftype, func):
        ''' Register a new output filter. Whenever bottle hits a handler output
            matching `ftype`, `func` is applied to it. '''
        if not isinstance(ftype, type):
            raise TypeError("Expected type object, got %s" % type(ftype))
        self.castfilter = [(t, f) for (t, f) in self.castfilter if t != ftype]
        self.castfilter.append((ftype, func))
        self.castfilter.sort()

    def match_url(self, path, method='GET'):
        """ Find a callback bound to a path and a specific HTTP method.
            Return (callback, param) tuple or raise HTTPError.
            method: HEAD falls back to GET. All methods fall back to ANY.
        """
        path, method = path.strip().lstrip('/'), method.upper()
        callbacks, args = self.routes.match(path)
        if not callbacks:
            raise HTTPError(404, "Not found: " + path)
        if method in callbacks:
            return callbacks[method], args
        if method == 'HEAD' and 'GET' in callbacks:
            return callbacks['GET'], args
        if 'ANY' in callbacks:
            return callbacks['ANY'], args
        allow = [m for m in callbacks if m != 'ANY']
        if 'GET' in allow and 'HEAD' not in allow:
            allow.append('HEAD')
        raise HTTPError(405, "Method not allowed.",
                        header=[('Allow',",".join(allow))])

    def get_url(self, routename, **kargs):
        """ Return a string that matches a named route """
        scriptname = request.environ.get('SCRIPT_NAME', '').strip('/') + '/'
        location = self.routes.build(routename, **kargs).lstrip('/')
        return urljoin(urljoin('/', scriptname), location)

    def route(self, path=None, method='GET', no_hooks=False, decorate=None,
              template=None, template_opts={}, callback=None, **kargs):
        """ Decorator: Bind a callback function to a request path.

            :param path: The request path or a list of paths to listen to. See 
              :class:`Router` for syntax details. If no path is specified, it
              is automatically generated from the callback signature. See
              :func:`yieldroutes` for details.
            :param method: The HTTP method (POST, GET, ...) or a list of
              methods to listen to. (default: GET)
            :param decorate: A decorator or a list of decorators. These are
              applied to the callback in reverse order.
            :param no_hooks: If true, application hooks are not triggered
              by this route. (default: False)
            :param template: The template to use for this callback.
              (default: no template)
            :param template_opts: A dict with additional template parameters.
            :param static: If true, all paths are static even if they contain
              dynamic syntax tokens. (default: False)
            :param name: The name for this route. (default: None)
            :param callback: If set, the route decorator is directly applied
              to the callback and the callback is returned instead. This
              equals ``Bottle.route(...)(callback)``.
        """
        # @route can be used without any parameters
        if callable(path): path, callback = None, path
        # Build up the list of decorators
        decorators = makelist(decorate)
        if template:     decorators.insert(0, view(template, **template_opts))
        if not no_hooks: decorators.append(self._add_hook_wrapper)
        def wrapper(func):
            callback = func
            for decorator in reversed(decorators):
                callback = decorator(callback)
            functools.update_wrapper(callback, func)
            for route in makelist(path) or yieldroutes(func):
                for meth in makelist(method):
                    route = route.strip().lstrip('/')
                    meth = meth.strip().upper()
                    old = self.routes.get_route(route, **kargs)
                    if old:
                        old.target[meth] = callback
                    else:
                        self.routes.add(route, {meth: callback}, **kargs)
            return func
        return wrapper(callback) if callback else wrapper

    def _add_hook_wrapper(self, func):
        ''' Add hooks to a callable. See #84 '''
        @functools.wraps(func)
        def wrapper(*a, **ka):
            for hook in self.hooks['before_request']: hook()
            response.output = func(*a, **ka)
            for hook in self.hooks['after_request']: hook()
            return response.output
        return wrapper

    def get(self, path=None, method='GET', **kargs):
        """ Decorator: Bind a function to a GET request path.
            See :meth:'route' for details. """
        return self.route(path, method, **kargs)

    def post(self, path=None, method='POST', **kargs):
        """ Decorator: Bind a function to a POST request path.
            See :meth:'route' for details. """
        return self.route(path, method, **kargs)

    def put(self, path=None, method='PUT', **kargs):
        """ Decorator: Bind a function to a PUT request path.
            See :meth:'route' for details. """
        return self.route(path, method, **kargs)

    def delete(self, path=None, method='DELETE', **kargs):
        """ Decorator: Bind a function to a DELETE request path.
            See :meth:'route' for details. """
        return self.route(path, method, **kargs)

    def error(self, code=500):
        """ Decorator: Register an output handler for a HTTP error code"""
        def wrapper(handler):
            self.error_handler[int(code)] = handler
            return handler
        return wrapper

    def hook(self, name):
        """ Return a decorator that adds a callback to the specified hook. """
        def wrapper(func):
            self.add_hook(name, func)
            return func
        return wrapper

    def add_hook(self, name, func):
        ''' Add a callback from a hook. '''
        if name not in self.hooks:
            raise ValueError("Unknown hook name %s" % name)
        if name in ('after_request'):
            self.hooks[name].insert(0, func)
        else:
            self.hooks[name].append(func)

    def remove_hook(self, name, func):
        ''' Remove a callback from a hook. '''
        if name not in self.hooks:
            raise ValueError("Unknown hook name %s" % name)
        self.hooks[name].remove(func)

    def handle(self, url, method):
        """ Execute the handler bound to the specified url and method and return
        its output. If catchall is true, exceptions are catched and returned as
        HTTPError(500) objects. """
        if not self.serve:
            return HTTPError(503, "Server stopped")
        try:
            handler, args = self.match_url(url, method)
            return handler(**args)
        except HTTPResponse, e:
            return e
        except Exception, e:
            if isinstance(e, (KeyboardInterrupt, SystemExit, MemoryError))\
            or not self.catchall:
                raise
            return HTTPError(500, 'Unhandled exception', e, format_exc(10))

    def _cast(self, out, request, response, peek=None):
        """ Try to convert the parameter into something WSGI compatible and set
        correct HTTP headers when possible.
        Support: False, str, unicode, dict, HTTPResponse, HTTPError, file-like,
        iterable of strings and iterable of unicodes
        """
        # Filtered types (recursive, because they may return anything)
        for testtype, filterfunc in self.castfilter:
            if isinstance(out, testtype):
                return self._cast(filterfunc(out), request, response)

        # Empty output is done here
        if not out:
            response.headers['Content-Length'] = 0
            return []
        # Join lists of byte or unicode strings. Mixed lists are NOT supported
        if isinstance(out, (tuple, list))\
        and isinstance(out[0], (bytes, unicode)):
            out = out[0][0:0].join(out) # b'abc'[0:0] -> b''
        # Encode unicode strings
        if isinstance(out, unicode):
            out = out.encode(response.charset)
        # Byte Strings are just returned
        if isinstance(out, bytes):
            response.headers['Content-Length'] = str(len(out))
            return [out]
        # HTTPError or HTTPException (recursive, because they may wrap anything)
        if isinstance(out, HTTPError):
            out.apply(response)
            return self._cast(self.error_handler.get(out.status, repr)(out), request, response)
        if isinstance(out, HTTPResponse):
            out.apply(response)
            return self._cast(out.output, request, response)

        # File-like objects.
        if hasattr(out, 'read'):
            if 'wsgi.file_wrapper' in request.environ:
                return request.environ['wsgi.file_wrapper'](out)
            elif hasattr(out, 'close') or not hasattr(out, '__iter__'):
                return WSGIFileWrapper(out)

        # Handle Iterables. We peek into them to detect their inner type.
        try:
            out = iter(out)
            first = out.next()
            while not first:
                first = out.next()
        except StopIteration:
            return self._cast('', request, response)
        except HTTPResponse, e:
            first = e
        except Exception, e:
            first = HTTPError(500, 'Unhandled exception', e, format_exc(10))
            if isinstance(e, (KeyboardInterrupt, SystemExit, MemoryError))\
            or not self.catchall:
                raise
        # These are the inner types allowed in iterator or generator objects.
        if isinstance(first, HTTPResponse):
            return self._cast(first, request, response)
        if isinstance(first, bytes):
            return itertools.chain([first], out)
        if isinstance(first, unicode):
            return itertools.imap(lambda x: x.encode(response.charset),
                                  itertools.chain([first], out))
        return self._cast(HTTPError(500, 'Unsupported response type: %s'\
                                         % type(first)), request, response)

    def wsgi(self, environ, start_response):
        """ The bottle WSGI-interface. """
        try:
            environ['bottle.app'] = self
            request.bind(environ)
            response.bind()
            out = self.handle(request.path, request.method)
            out = self._cast(out, request, response)
            # rfc2616 section 4.3
            if response.status in (100, 101, 204, 304) or request.method == 'HEAD':
                if hasattr(out, 'close'): out.close()
                out = []
            status = '%d %s' % (response.status, HTTP_CODES[response.status])
            start_response(status, response.headerlist)
            return out
        except (KeyboardInterrupt, SystemExit, MemoryError):
            raise
        except Exception, e:
            if not self.catchall: raise
            err = '<h1>Critical error while processing request: %s</h1>' \
                  % environ.get('PATH_INFO', '/')
            if DEBUG:
                err += '<h2>Error:</h2>\n<pre>%s</pre>\n' % repr(e)
                err += '<h2>Traceback:</h2>\n<pre>%s</pre>\n' % format_exc(10)
            environ['wsgi.errors'].write(err) #TODO: wsgi.error should not get html
            start_response('500 INTERNAL SERVER ERROR', [('Content-Type', 'text/html')])
            return [tob(err)]
        
    def __call__(self, environ, start_response):
        return self.wsgi(environ, start_response)






###############################################################################
# HTTP and WSGI Tools ##########################################################
###############################################################################

class Request(threading.local, DictMixin):
    """ Represents a single HTTP request using thread-local attributes.
        The Request object wraps a WSGI environment and can be used as such.
    """
    def __init__(self, environ=None):
        """ Create a new Request instance.
        
            You usually don't do this but use the global `bottle.request`
            instance instead.
        """
        self.bind(environ or {},)

    def bind(self, environ):
        """ Bind a new WSGI environment.
            
            This is done automatically for the global `bottle.request`
            instance on every request.
        """
        self.environ = environ
        # These attributes are used anyway, so it is ok to compute them here
        self.path = '/' + environ.get('PATH_INFO', '/').lstrip('/')
        self.method = environ.get('REQUEST_METHOD', 'GET').upper()

    @property
    def _environ(self):
        depr("Request._environ renamed to Request.environ")
        return self.environ

    def copy(self):
        ''' Returns a copy of self '''
        return Request(self.environ.copy())

    def path_shift(self, shift=1):
        ''' Shift path fragments from PATH_INFO to SCRIPT_NAME and vice versa.

           :param shift: The number of path fragments to shift. May be negative
                         to change the shift direction. (default: 1)
        '''
        script_name = self.environ.get('SCRIPT_NAME','/')
        self['SCRIPT_NAME'], self.path = path_shift(script_name, self.path, shift)
        self['PATH_INFO'] = self.path

    def __getitem__(self, key): return self.environ[key]
    def __delitem__(self, key): self[key] = ""; del(self.environ[key])
    def __iter__(self): return iter(self.environ)
    def __len__(self): return len(self.environ)
    def keys(self): return self.environ.keys()
    def __setitem__(self, key, value):
        """ Shortcut for Request.environ.__setitem__ """
        self.environ[key] = value
        todelete = []
        if key in ('PATH_INFO','REQUEST_METHOD'):
            self.bind(self.environ)
        elif key == 'wsgi.input': todelete = ('body','forms','files','params')
        elif key == 'QUERY_STRING': todelete = ('get','params')
        elif key.startswith('HTTP_'): todelete = ('headers', 'cookies')
        for key in todelete:
            if 'bottle.' + key in self.environ:
                del self.environ['bottle.' + key]

    @property
    def query_string(self):
        """ The part of the URL following the '?'. """
        return self.environ.get('QUERY_STRING', '')

    @property
    def fullpath(self):
        """ Request path including SCRIPT_NAME (if present). """
        return self.environ.get('SCRIPT_NAME', '').rstrip('/') + self.path

    @property
    def url(self):
        """ Full URL as requested by the client (computed).

            This value is constructed out of different environment variables
            and includes scheme, host, port, scriptname, path and query string. 
        """
        scheme = self.environ.get('wsgi.url_scheme', 'http')
        host   = self.environ.get('HTTP_X_FORWARDED_HOST')
        host   = host or self.environ.get('HTTP_HOST', None)
        if not host:
            host = self.environ.get('SERVER_NAME')
            port = self.environ.get('SERVER_PORT', '80')
            if (scheme, port) not in (('https','443'), ('http','80')):
                host += ':' + port
        parts = (scheme, host, urlquote(self.fullpath), self.query_string, '')
        return urlunsplit(parts)

    @property
    def content_length(self):
        """ Content-Length header as an integer, -1 if not specified """
        return int(self.environ.get('CONTENT_LENGTH', '') or -1)

    @property
    def header(self):
        depr("The Request.header property was renamed to Request.headers")
        return self.headers

    @property
    def headers(self):
        ''' Request HTTP Headers stored in a dict-like object.

            This dictionary uses case-insensitive keys and native strings as
            keys and values. See :class:`WSGIHeaderDict` for details.
        '''
        if 'bottle.headers' not in self.environ:
            self.environ['bottle.headers'] = WSGIHeaderDict(self.environ)
        return self.environ['bottle.headers']

    @property
    def GET(self):
        """ The QUERY_STRING parsed into an instance of :class:`MultiDict`.

            If you expect more than one value for a key, use ``.getall(key)`` on
            this dictionary to get a list of all values. Otherwise, only the
            first value is returned.
        """
        if 'bottle.get' not in self.environ:
            data = parse_qs(self.query_string, keep_blank_values=True)
            get = self.environ['bottle.get'] = MultiDict()
            for key, values in data.iteritems():
                for value in values:
                    get[key] = value
        return self.environ['bottle.get']

    @property
    def POST(self):
        """ The combined values from :attr:`forms` and :attr:`files`. Values are
            either strings (form values) or instances of
            :class:`cgi.FieldStorage` (file uploads).

            If you expect more than one value for a key, use ``.getall(key)`` on
            this dictionary to get a list of all values. Otherwise, only the
            first value is returned.
        """
        if 'bottle.post' not in self.environ:
            self.environ['bottle.post'] = MultiDict()
            self.environ['bottle.forms'] = MultiDict()
            self.environ['bottle.files'] = MultiDict()
            safe_env = {'QUERY_STRING':''} # Build a safe environment for cgi
            for key in ('REQUEST_METHOD', 'CONTENT_TYPE', 'CONTENT_LENGTH'):
                if key in self.environ: safe_env[key] = self.environ[key]
            if NCTextIOWrapper:
                fb = NCTextIOWrapper(self.body, encoding='ISO-8859-1', newline='\n')
                # TODO: Content-Length may be wrong now. Does cgi.FieldStorage
                # use it at all? I think not, because all tests pass.
            else:
                fb = self.body
            data = cgi.FieldStorage(fp=fb, environ=safe_env, keep_blank_values=True)
            for item in data.list or []:
                if item.filename:
                    self.environ['bottle.post'][item.name] = item
                    self.environ['bottle.files'][item.name] = item
                else:
                    self.environ['bottle.post'][item.name] = item.value
                    self.environ['bottle.forms'][item.name] = item.value
        return self.environ['bottle.post']

    @property
    def forms(self):
        """ POST form values parsed into an instance of :class:`MultiDict`.

            This property contains form values parsed from an `url-encoded`
            or `multipart/form-data` encoded POST request bidy. The values are
            native strings.

            If you expect more than one value for a key, use ``.getall(key)`` on
            this dictionary to get a list of all values. Otherwise, only the
            first value is returned.
        """
        if 'bottle.forms' not in self.environ: self.POST
        return self.environ['bottle.forms']

    @property
    def files(self):
        """ File uploads parsed into an instance of :class:`MultiDict`.

            This property contains file uploads parsed from an
            `multipart/form-data` encoded POST request body. The values are
            instances of :class:`cgi.FieldStorage`.

            If you expect more than one value for a key, use ``.getall(key)`` on
            this dictionary to get a list of all values. Otherwise, only the
            first value is returned.
        """
        if 'bottle.files' not in self.environ: self.POST
        return self.environ['bottle.files']
        
    @property
    def params(self):
        """ A combined :class:`MultiDict` with values from :attr:`forms` and
            :attr:`GET`. File-uploads are not included. """
        if 'bottle.params' not in self.environ:
            self.environ['bottle.params'] = MultiDict(self.GET)
            self.environ['bottle.params'].update(dict(self.forms))
        return self.environ['bottle.params']

    @property
    def body(self):
        """ The HTTP request body as a seekable file-like object.

            This property returns a copy of the `wsgi.input` stream and should
            be used instead of `environ['wsgi.input']`.
         """
        if 'bottle.body' not in self.environ:
            maxread = max(0, self.content_length)
            stream = self.environ['wsgi.input']
            body = BytesIO() if maxread < MEMFILE_MAX else TemporaryFile(mode='w+b')
            while maxread > 0:
                part = stream.read(min(maxread, MEMFILE_MAX))
                if not part: #TODO: Wrong content_length. Error? Do nothing?
                    break
                body.write(part)
                maxread -= len(part)
            self.environ['wsgi.input'] = body
            self.environ['bottle.body'] = body
        self.environ['bottle.body'].seek(0)
        return self.environ['bottle.body']

    @property
    def auth(self): #TODO: Tests and docs. Add support for digest. namedtuple?
        """ HTTP authorization data as a (user, passwd) tuple. (experimental)

            This implementation currently only supports basic auth and returns
            None on errors.
        """
        return parse_auth(self.headers.get('Authorization',''))

    @property
    def COOKIES(self):
        """ Cookies parsed into a dictionary. Secure cookies are NOT decoded
            automatically. See :meth:`get_cookie` for details.
        """
        if 'bottle.cookies' not in self.environ:
            raw_dict = SimpleCookie(self.headers.get('Cookie',''))
            self.environ['bottle.cookies'] = {}
            for cookie in raw_dict.itervalues():
                self.environ['bottle.cookies'][cookie.key] = cookie.value
        return self.environ['bottle.cookies']

    def get_cookie(self, key, secret=None):
        """ Return the content of a cookie. To read a `Secure Cookies`, use the
            same `secret` as used to create the cookie (see
            :meth:`Response.set_cookie`). If anything goes wrong, None is
            returned.
        """
        value = self.COOKIES.get(key)
        if secret and value:
            dec = cookie_decode(value, secret) # (key, value) tuple or None
            return dec[1] if dec and dec[0] == key else None
        return value or None

    @property
    def is_ajax(self):
        ''' True if the request was generated using XMLHttpRequest '''
        #TODO: write tests
        return self.header.get('X-Requested-With') == 'XMLHttpRequest'



class Response(threading.local):
    """ Represents a single HTTP response using thread-local attributes.
    """

    def __init__(self):
        self.bind()

    def bind(self):
        """ Resets the Response object to its factory defaults. """
        self._COOKIES = None
        self.status = 200
        self.headers = HeaderDict()
        self.content_type = 'text/html; charset=UTF-8'

    @property
    def header(self):
        depr("Response.header renamed to Response.headers")
        return self.headers

    def copy(self):
        ''' Returns a copy of self. '''
        copy = Response()
        copy.status = self.status
        copy.headers = self.headers.copy()
        copy.content_type = self.content_type
        return copy

    def wsgiheader(self):
        ''' Returns a wsgi conform list of header/value pairs. '''
        for c in self.COOKIES.values():
            if c.OutputString() not in self.headers.getall('Set-Cookie'):
                self.headers.append('Set-Cookie', c.OutputString())
        # rfc2616 section 10.2.3, 10.3.5
        if self.status in (204, 304) and 'content-type' in self.headers:
            del self.headers['content-type']
        if self.status == 304:
            for h in ('allow', 'content-encoding', 'content-language',
                      'content-length', 'content-md5', 'content-range',
                      'content-type', 'last-modified'): # + c-location, expires?
                if h in self.headers:
                     del self.headers[h]
        return list(self.headers.iterallitems())
    headerlist = property(wsgiheader)

    @property
    def charset(self):
        """ Return the charset specified in the content-type header.
        
            This defaults to `UTF-8`.
        """
        if 'charset=' in self.content_type:
            return self.content_type.split('charset=')[-1].split(';')[0].strip()
        return 'UTF-8'

    @property
    def COOKIES(self):
        """ A dict-like SimpleCookie instance. Use :meth:`set_cookie` instead. """
        if not self._COOKIES:
            self._COOKIES = SimpleCookie()
        return self._COOKIES

    def set_cookie(self, key, value, secret=None, **kargs):
        ''' Add a cookie. If the `secret` parameter is set, this creates a
            `Secure Cookie` (described below).

            :param key: the name of the cookie.
            :param value: the value of the cookie.
            :param secret: required for secure cookies. (default: None)
            :param max_age: maximum age in seconds. (default: None)
            :param expires: a datetime object or UNIX timestamp. (defaut: None)
            :param domain: the domain that is allowed to read the cookie.
              (default: current domain)
            :param path: limits the cookie to a given path (default: /)

            If neither `expires` nor `max_age` are set (default), the cookie
            lasts only as long as the browser is not closed.

            Secure cookies may store any pickle-able object and are
            cryptographically signed to prevent manipulation. Keep in mind that
            cookies are limited to 4kb in most browsers.
            
            Warning: Secure cookies are not encrypted (the client can still see
            the content) and not copy-protected (the client can restore an old
            cookie). The main intention is to make pickling and unpickling
            save, not to store secret information at client side.
        '''
        if secret:
            value = touni(cookie_encode((key, value), secret))
        elif not isinstance(value, basestring):
            raise TypeError('Secret missing for non-string Cookie.')

        self.COOKIES[key] = value
        for k, v in kargs.iteritems():
            self.COOKIES[key][k.replace('_', '-')] = v

    def delete_cookie(self, key, **kwargs):
        ''' Delete a cookie. Be sure to use the same `domain` and `path`
            parameters as used to create the cookie. '''
        kwargs['max_age'] = -1
        kwargs['expires'] = 0
        self.set_cookie(key, '', **kwargs)

    def get_content_type(self):
        """ Current 'Content-Type' header. """
        return self.headers['Content-Type']

    def set_content_type(self, value):
        self.headers['Content-Type'] = value

    content_type = property(get_content_type, set_content_type, None,
                            get_content_type.__doc__)






###############################################################################
# Common Utilities #############################################################
###############################################################################

class MultiDict(DictMixin):
    """ A dict that remembers old values for each key """
    # collections.MutableMapping would be better for Python >= 2.6
    def __init__(self, *a, **k):
        self.dict = dict()
        for k, v in dict(*a, **k).iteritems():
            self[k] = v

    def __len__(self): return len(self.dict)
    def __iter__(self): return iter(self.dict)
    def __contains__(self, key): return key in self.dict
    def __delitem__(self, key): del self.dict[key]
    def keys(self): return self.dict.keys()
    def __getitem__(self, key): return self.get(key, KeyError, -1)
    def __setitem__(self, key, value): self.append(key, value)

    def append(self, key, value): self.dict.setdefault(key, []).append(value)
    def replace(self, key, value): self.dict[key] = [value]
    def getall(self, key): return self.dict.get(key) or []

    def get(self, key, default=None, index=-1):
        if key not in self.dict and default != KeyError:
            return [default][index]
        return self.dict[key][index]

    def iterallitems(self):
        for key, values in self.dict.iteritems():
            for value in values:
                yield key, value


class HeaderDict(MultiDict):
    """ Same as :class:`MultiDict`, but title()s the keys and overwrites by default. """
    def __contains__(self, key): return MultiDict.__contains__(self, self.httpkey(key))
    def __getitem__(self, key): return MultiDict.__getitem__(self, self.httpkey(key))
    def __delitem__(self, key): return MultiDict.__delitem__(self, self.httpkey(key))
    def __setitem__(self, key, value): self.replace(key, value)
    def get(self, key, default=None, index=-1): return MultiDict.get(self, self.httpkey(key), default, index)
    def append(self, key, value): return MultiDict.append(self, self.httpkey(key), str(value))
    def replace(self, key, value): return MultiDict.replace(self, self.httpkey(key), str(value))
    def getall(self, key): return MultiDict.getall(self, self.httpkey(key))
    def httpkey(self, key): return str(key).replace('_','-').title()


class WSGIHeaderDict(DictMixin):
    ''' This dict-like class wraps a WSGI environ dict and provides convenient
        access to HTTP_* fields. Keys and values are native strings
        (2.x bytes or 3.x unicode) and keys are case-insensitive. If the WSGI
        environment contains non-native string values, these are de- or encoded
        using a lossless 'latin1' character set.

        The API will remain stable even on changes to the relevant PEPs.
        Currently PEP 333, 444 and 3333 are supported. (PEP 444 is the only one
        that uses non-native strings.)
     '''

    def __init__(self, environ):
        self.environ = environ

    def _ekey(self, key): # Translate header field name to environ key.
        return 'HTTP_' + key.replace('-','_').upper()

    def raw(self, key, default=None):
        ''' Return the header value as is (may be bytes or unicode). '''
        return self.environ.get(self._ekey(key), default)

    def __getitem__(self, key):
        return tonat(self.environ[self._ekey(key)], 'latin1')

    def __setitem__(self, key, value):
        raise TypeError("%s is read-only." % self.__class__)

    def __delitem__(self, key):
        raise TypeError("%s is read-only." % self.__class__)

    def __iter__(self):
        for key in self.environ:
            if key[:5] == 'HTTP_':
                yield key[5:].replace('_', '-').title()

    def keys(self): return list(self)
    def __len__(self): return len(list(self))
    def __contains__(self, key): return self._ekey(key) in self.environ





class AppStack(list):
    """ A stack implementation. """

    def __call__(self):
        """ Return the current default app. """
        return self[-1]

    def push(self, value=None):
        """ Add a new Bottle instance to the stack """
        if not isinstance(value, Bottle):
            value = Bottle()
        self.append(value)
        return value

class WSGIFileWrapper(object):

   def __init__(self, fp, buffer_size=1024*64):
       self.fp, self.buffer_size = fp, buffer_size
       for attr in ('fileno', 'close', 'read', 'readlines'):
           if hasattr(fp, attr): setattr(self, attr, getattr(fp, attr))

   def __iter__(self):
       read, buff = self.fp.read, self.buffer_size
       while True:
           part = read(buff)
           if not part: break
           yield part






###############################################################################
# Application Helper ###########################################################
###############################################################################

def dict2json(d):
    response.content_type = 'application/json'
    return json_dumps(d)


def abort(code=500, text='Unknown Error: Application stopped.'):
    """ Aborts execution and causes a HTTP error. """
    raise HTTPError(code, text)


def redirect(url, code=303):
    """ Aborts execution and causes a 303 redirect """
    scriptname = request.environ.get('SCRIPT_NAME', '').rstrip('/') + '/'
    location = urljoin(request.url, urljoin(scriptname, url))
    raise HTTPResponse("", status=code, header=dict(Location=location))


def send_file(*a, **k): #BC 0.6.4
    """ Raises the output of static_file(). (deprecated) """
    raise static_file(*a, **k)


def static_file(filename, root, guessmime=True, mimetype=None, download=False):
    """ Opens a file in a safe way and returns a HTTPError object with status
        code 200, 305, 401 or 404. Sets Content-Type, Content-Length and
        Last-Modified header. Obeys If-Modified-Since header and HEAD requests.
    """
    root = os.path.abspath(root) + os.sep
    filename = os.path.abspath(os.path.join(root, filename.strip('/\\')))
    header = dict()

    if not filename.startswith(root):
        return HTTPError(403, "Access denied.")
    if not os.path.exists(filename) or not os.path.isfile(filename):
        return HTTPError(404, "File does not exist.")
    if not os.access(filename, os.R_OK):
        return HTTPError(403, "You do not have permission to access this file.")

    if not mimetype and guessmime:
        header['Content-Type'] = mimetypes.guess_type(filename)[0]
    else:
        header['Content-Type'] = mimetype if mimetype else 'text/plain'

    if download == True:
        download = os.path.basename(filename)
    if download:
        header['Content-Disposition'] = 'attachment; filename="%s"' % download

    stats = os.stat(filename)
    lm = time.strftime("%a, %d %b %Y %H:%M:%S GMT", time.gmtime(stats.st_mtime))
    header['Last-Modified'] = lm
    ims = request.environ.get('HTTP_IF_MODIFIED_SINCE')
    if ims:
        ims = ims.split(";")[0].strip() # IE sends "<date>; length=146"
        ims = parse_date(ims)
        if ims is not None and ims >= int(stats.st_mtime):
            header['Date'] = time.strftime("%a, %d %b %Y %H:%M:%S GMT", time.gmtime())
            return HTTPResponse(status=304, header=header)
    header['Content-Length'] = stats.st_size
    if request.method == 'HEAD':
        return HTTPResponse('', header=header)
    else:
        return HTTPResponse(open(filename, 'rb'), header=header)






###############################################################################
# HTTP Utilities and MISC (TODO) ###############################################
###############################################################################

def debug(mode=True):
    """ Change the debug level.
    There is only one debug level supported at the moment."""
    global DEBUG
    DEBUG = bool(mode)


def parse_date(ims):
    """ Parse rfc1123, rfc850 and asctime timestamps and return UTC epoch. """
    try:
        ts = email.utils.parsedate_tz(ims)
        return time.mktime(ts[:8] + (0,)) - (ts[9] or 0) - time.timezone
    except (TypeError, ValueError, IndexError, OverflowError):
        return None


def parse_auth(header):
    """ Parse rfc2617 HTTP authentication header string (basic) and return (user,pass) tuple or None"""
    try:
        method, data = header.split(None, 1)
        if method.lower() == 'basic':
            name, pwd = base64.b64decode(data).split(':', 1)
            return name, pwd
    except (KeyError, ValueError, TypeError):
        return None


def _lscmp(a, b):
    ''' Compares two strings in a cryptographically save way:
        Runtime is not affected by a common prefix. '''
    return not sum(0 if x==y else 1 for x, y in zip(a, b)) and len(a) == len(b)


def cookie_encode(data, key):
    ''' Encode and sign a pickle-able object. Return a (byte) string '''
    msg = base64.b64encode(pickle.dumps(data, -1))
    sig = base64.b64encode(hmac.new(key, msg).digest())
    return tob('!') + sig + tob('?') + msg


def cookie_decode(data, key):
    ''' Verify and decode an encoded string. Return an object or None.'''
    data = tob(data)
    if cookie_is_encoded(data):
        sig, msg = data.split(tob('?'), 1)
        if _lscmp(sig[1:], base64.b64encode(hmac.new(key, msg).digest())):
            return pickle.loads(base64.b64decode(msg))
    return None


def cookie_is_encoded(data):
    ''' Return True if the argument looks like a encoded cookie.'''
    return bool(data.startswith(tob('!')) and tob('?') in data)


def yieldroutes(func):
    """ Return a generator for routes that match the signature (name, args) 
    of the func parameter. This may yield more than one route if the function
    takes optional keyword arguments. The output is best described by example::
    
        a()         -> '/a'
        b(x, y)     -> '/b/:x/:y'
        c(x, y=5)   -> '/c/:x' and '/c/:x/:y'
        d(x=5, y=6) -> '/d' and '/d/:x' and '/d/:x/:y'
    """
    import inspect # Expensive module. Only import if necessary.
    path = func.__name__.replace('__','/').lstrip('/')
    spec = inspect.getargspec(func)
    argc = len(spec[0]) - len(spec[3] or [])
    path += ('/:%s' * argc) % tuple(spec[0][:argc])
    yield path
    for arg in spec[0][argc:]:
        path += '/:%s' % arg
        yield path

def path_shift(script_name, path_info, shift=1):
    ''' Shift path fragments from PATH_INFO to SCRIPT_NAME and vice versa.

        :return: The modified paths.
        :param script_name: The SCRIPT_NAME path.
        :param script_name: The PATH_INFO path.
        :param shift: The number of path fragments to shift. May be negative to
          change the shift direction. (default: 1)
    '''
    if shift == 0: return script_name, path_info
    pathlist = path_info.strip('/').split('/')
    scriptlist = script_name.strip('/').split('/')
    if pathlist and pathlist[0] == '': pathlist = []
    if scriptlist and scriptlist[0] == '': scriptlist = []
    if shift > 0 and shift <= len(pathlist):
        moved = pathlist[:shift]
        scriptlist = scriptlist + moved
        pathlist = pathlist[shift:]
    elif shift < 0 and shift >= -len(scriptlist):
        moved = scriptlist[shift:]
        pathlist = moved + pathlist
        scriptlist = scriptlist[:shift]
    else:
        empty = 'SCRIPT_NAME' if shift < 0 else 'PATH_INFO'
        raise AssertionError("Cannot shift. Nothing left from %s" % empty)
    new_script_name = '/' + '/'.join(scriptlist)
    new_path_info = '/' + '/'.join(pathlist)
    if path_info.endswith('/') and pathlist: new_path_info += '/'
    return new_script_name, new_path_info



# Decorators
#TODO: Replace default_app() with app()

def validate(**vkargs):
    """
    Validates and manipulates keyword arguments by user defined callables.
    Handles ValueError and missing arguments by raising HTTPError(403).
    """
    def decorator(func):
        def wrapper(**kargs):
            for key, value in vkargs.iteritems():
                if key not in kargs:
                    abort(403, 'Missing parameter: %s' % key)
                try:
                    kargs[key] = value(kargs[key])
                except ValueError:
                    abort(403, 'Wrong parameter format for: %s' % key)
            return func(**kargs)
        return wrapper
    return decorator

def auth_basic(check, realm="private", text="Access denied"):
    ''' Callback decorator to require HTTP auth (basic).
        TODO: Add route(check_auth=...) parameter. '''
    def decorator(func):
      def wrapper(*a, **ka):
        user, password = request.auth or (None, None)
        if user is None or not check(user, password):
          response.headers['WWW-Authenticate'] = 'Basic realm="%s"' % realm
          return HTTPError(401, text)
        return func(*a, **ka)
      return wrapper
    return decorator 


def make_default_app_wrapper(name):
    ''' Return a callable that relays calls to the current default app. '''
    @functools.wraps(getattr(Bottle, name))
    def wrapper(*a, **ka):
        return getattr(app(), name)(*a, **ka)
    return wrapper

for name in 'route get post put delete error mount hook'.split():
    globals()[name] = make_default_app_wrapper(name)
url = make_default_app_wrapper('get_url')
del name

def default():
    depr("The default() decorator is deprecated. Use @error(404) instead.")
    return error(404)






###############################################################################
# Server Adapter ###############################################################
###############################################################################

class ServerAdapter(object):
    quiet = False
    def __init__(self, host='127.0.0.1', port=8080, **config):
        self.options = config
        self.host = host
        self.port = int(port)

    def run(self, handler): # pragma: no cover
        pass
        
    def __repr__(self):
        args = ', '.join(['%s=%s'%(k,repr(v)) for k, v in self.options.items()])
        return "%s(%s)" % (self.__class__.__name__, args)


class CGIServer(ServerAdapter):
    quiet = True
    def run(self, handler): # pragma: no cover
        from wsgiref.handlers import CGIHandler
        CGIHandler().run(handler) # Just ignore host and port here


class FlupFCGIServer(ServerAdapter):
    def run(self, handler): # pragma: no cover
        import flup.server.fcgi
        kwargs = {'bindAddress':(self.host, self.port)}
        kwargs.update(self.options) # allow to override bindAddress and others
        flup.server.fcgi.WSGIServer(handler, **kwargs).run()


class WSGIRefServer(ServerAdapter):
    def run(self, handler): # pragma: no cover
        from wsgiref.simple_server import make_server, WSGIRequestHandler
        if self.quiet:
            class QuietHandler(WSGIRequestHandler):
                def log_request(*args, **kw): pass
            self.options['handler_class'] = QuietHandler
        srv = make_server(self.host, self.port, handler, **self.options)
        srv.serve_forever()


class CherryPyServer(ServerAdapter):
    def run(self, handler): # pragma: no cover
        from cherrypy import wsgiserver
        server = wsgiserver.CherryPyWSGIServer((self.host, self.port), handler)
        server.start()


class PasteServer(ServerAdapter):
    def run(self, handler): # pragma: no cover
        from paste import httpserver
        if not self.quiet:
            from paste.translogger import TransLogger
            handler = TransLogger(handler)
        httpserver.serve(handler, host=self.host, port=str(self.port),
                         **self.options)
                         
class MeinheldServer(ServerAdapter):
    def run(self, handler):
        from meinheld import server
        server.listen((self.host, self.port))
        server.run(handler)

class FapwsServer(ServerAdapter):
    """ Extremely fast webserver using libev. See http://www.fapws.org/ """
    def run(self, handler): # pragma: no cover
        import fapws._evwsgi as evwsgi
        from fapws import base, config
        port = self.port
        if float(config.SERVER_IDENT[-2:]) > 0.4:
            # fapws3 silently changed its API in 0.5
            port = str(port)
        evwsgi.start(self.host, port)
        # fapws3 never releases the GIL. Complain upstream. I tried. No luck.
        if 'BOTTLE_CHILD' in os.environ and not self.quiet:
            print "WARNING: Auto-reloading does not work with Fapws3."
            print "         (Fapws3 breaks python thread support)"
        evwsgi.set_base_module(base)
        def app(environ, start_response):
            environ['wsgi.multiprocess'] = False
            return handler(environ, start_response)
        evwsgi.wsgi_cb(('', app))
        evwsgi.run()


class TornadoServer(ServerAdapter):
    """ The super hyped asynchronous server by facebook. Untested. """
    def run(self, handler): # pragma: no cover
        import tornado.wsgi
        import tornado.httpserver
        import tornado.ioloop
        container = tornado.wsgi.WSGIContainer(handler)
        server = tornado.httpserver.HTTPServer(container)
        server.listen(port=self.port)
        tornado.ioloop.IOLoop.instance().start()


class AppEngineServer(ServerAdapter):
    """ Adapter for Google App Engine. """
    quiet = True
    def run(self, handler):
        from google.appengine.ext.webapp import util
        util.run_wsgi_app(handler)


class TwistedServer(ServerAdapter):
    """ Untested. """
    def run(self, handler):
        from twisted.web import server, wsgi
        from twisted.python.threadpool import ThreadPool
        from twisted.internet import reactor
        thread_pool = ThreadPool()
        thread_pool.start()
        reactor.addSystemEventTrigger('after', 'shutdown', thread_pool.stop)
        factory = server.Site(wsgi.WSGIResource(reactor, thread_pool, handler))
        reactor.listenTCP(self.port, factory, interface=self.host)
        reactor.run()


class DieselServer(ServerAdapter):
    """ Untested. """
    def run(self, handler):
        from diesel.protocols.wsgi import WSGIApplication
        app = WSGIApplication(handler, port=self.port)
        app.run()


class GeventServer(ServerAdapter):
    """ Untested. """
    def run(self, handler):
        from gevent import wsgi
        #from gevent.hub import getcurrent
        #self.set_context_ident(getcurrent, weakref=True) # see contextlocal
        wsgi.WSGIServer((self.host, self.port), handler).serve_forever()


class GunicornServer(ServerAdapter):
    """ Untested. """
    def run(self, handler):
        from gunicorn.arbiter import Arbiter
        from gunicorn.config import Config
        handler.cfg = Config({'bind': "%s:%d" % (self.host, self.port), 'workers': 4})
        arbiter = Arbiter(handler)
        arbiter.run()


class EventletServer(ServerAdapter):
    """ Untested """
    def run(self, handler):
        from eventlet import wsgi, listen
        wsgi.server(listen((self.host, self.port)), handler)


class RocketServer(ServerAdapter):
    """ Untested. As requested in issue 63
        https://github.com/defnull/bottle/issues/#issue/63 """
    def run(self, handler):
        from rocket import Rocket
        server = Rocket((self.host, self.port), 'wsgi', { 'wsgi_app' : handler })
        server.start()

class BjoernServer(ServerAdapter):
    """ Screamingly fast server written in C: https://github.com/jonashaag/bjoern """
    def run(self, handler):
        from bjoern import run
        run(handler, self.host, self.port)


class AutoServer(ServerAdapter):
    """ Untested. """
    adapters = [PasteServer, CherryPyServer, TwistedServer, WSGIRefServer]
    def run(self, handler):
        for sa in self.adapters:
            try:
                return sa(self.host, self.port, **self.options).run(handler)
            except ImportError:
                pass


server_names = {
    'cgi': CGIServer,
    'flup': FlupFCGIServer,
    'wsgiref': WSGIRefServer,
    'cherrypy': CherryPyServer,
    'paste': PasteServer,
    'fapws3': FapwsServer,
    'tornado': TornadoServer,
    'gae': AppEngineServer,
    'twisted': TwistedServer,
    'diesel': DieselServer,
    'meinheld': MeinheldServer,
    'gunicorn': GunicornServer,
    'eventlet': EventletServer,
    'gevent': GeventServer,
    'rocket': RocketServer,
    'bjoern' : BjoernServer,
    'auto': AutoServer,
}






###############################################################################
# Application Control ##########################################################
###############################################################################


def _load(target, **kwargs):
    """ Fetch something from a module. The exact behaviour depends on the the
        target string:

        If the target is a valid python import path (e.g. `package.module`), 
        the rightmost part is returned as a module object.
        If the target contains a colon (e.g. `package.module:var`) the module
        variable specified after the colon is returned.
        If the part after the colon contains any non-alphanumeric characters
        (e.g. `package.module:function(argument)`) the result of the expression
        is returned. The exec namespace is updated with the keyword arguments
        provided to this function.
        
        Example::
        >>> _load('bottle')
        <module 'bottle' from 'bottle.py'>
        >>> _load('bottle:Bottle')
        <class 'bottle.Bottle'>
        >>> _load('bottle:cookie_encode(v, secret)', v='foo', secret='bar')
        '!F+hN4dQxaDJ4QxxaZ+Z3jw==?gAJVA2Zvb3EBLg=='

    """
    module, target = target.split(":", 1) if ':' in target else (target, None)
    if module not in sys.modules:
        __import__(module)
    if not target:
        return sys.modules[module]
    if target.isalnum():
        return getattr(sys.modules[module], target)
    package_name = module.split('.')[0]
    kwargs[package_name] = sys.modules[package_name]
    return eval('%s.%s' % (module, target), kwargs)

def load_app(target):
    """ Load a bottle application based on a target string and return the
        application object.

        If the target is an import path (e.g. package.module), the application
        stack is used to isolate the routes defined in that module.
        If the target contains a colon (e.g. package.module:myapp) the
        module variable specified after the colon is returned instead.
    """
    tmp = app.push() # Create a new "default application"
    rv = _load(target) # Import the target module
    app.remove(tmp) # Remove the temporary added default application
    return rv if isinstance(rv, Bottle) else tmp


def run(app=None, server='wsgiref', host='127.0.0.1', port=8080,
        interval=1, reloader=False, quiet=False, **kargs):
    """ Start a server instance. This method blocks until the server terminates.

        :param app: WSGI application or target string supported by
               :func:`load_app`. (default: :func:`default_app`)
        :param server: Server adapter to use. See :data:`server_names` keys
               for valid names or pass a :class:`ServerAdapter` subclass.
               (default: `wsgiref`)
        :param host: Server address to bind to. Pass ``0.0.0.0`` to listens on
               all interfaces including the external one. (default: 127.0.0.1)
        :param port: Server port to bind to. Values below 1024 require root
               privileges. (default: 8080)
        :param reloader: Start auto-reloading server? (default: False)
        :param interval: Auto-reloader interval in seconds (default: 1)
        :param quiet: Suppress output to stdout and stderr? (default: False)
        :param options: Options passed to the server adapter.
     """
    app = app or default_app()
    if isinstance(app, basestring):
        app = load_app(app)
    if isinstance(server, basestring):
        server = server_names.get(server)
    if isinstance(server, type):
        server = server(host=host, port=port, **kargs)
    if not isinstance(server, ServerAdapter):
        raise RuntimeError("Server must be a subclass of ServerAdapter")
    server.quiet = server.quiet or quiet
    if not server.quiet and not os.environ.get('BOTTLE_CHILD'):
        print "Bottle server starting up (using %s)..." % repr(server)
        print "Listening on http://%s:%d/" % (server.host, server.port)
        print "Use Ctrl-C to quit."
        print
    try:
        if reloader:
            interval = min(interval, 1)
            if os.environ.get('BOTTLE_CHILD'):
                _reloader_child(server, app, interval)
            else:
                _reloader_observer(server, app, interval)
        else:
            server.run(app)
    except KeyboardInterrupt:
        pass
    if not server.quiet and not os.environ.get('BOTTLE_CHILD'):
        print "Shutting down..."


class FileCheckerThread(threading.Thread):
    ''' Thread that periodically checks for changed module files. '''

    def __init__(self, lockfile, interval):
        threading.Thread.__init__(self)
        self.lockfile, self.interval = lockfile, interval
        #1: lockfile to old; 2: lockfile missing
        #3: module file changed; 5: external exit
        self.status = 0

    def run(self):
        exists = os.path.exists
        mtime = lambda path: os.stat(path).st_mtime
        files = dict()
        for module in sys.modules.values():
            path = getattr(module, '__file__', '')
            if path[-4:] in ('.pyo', '.pyc'): path = path[:-1]
            if path and exists(path): files[path] = mtime(path)
        while not self.status:
            for path, lmtime in files.iteritems():
                if not exists(path) or mtime(path) > lmtime:
                    self.status = 3
            if not exists(self.lockfile):
                self.status = 2
            elif mtime(self.lockfile) < time.time() - self.interval - 5:
                self.status = 1
            if not self.status:
                time.sleep(self.interval)
        if self.status != 5:
            thread.interrupt_main()


def _reloader_child(server, app, interval):
    ''' Start the server and check for modified files in a background thread.
        As soon as an update is detected, KeyboardInterrupt is thrown in
        the main thread to exit the server loop. The process exists with status
        code 3 to request a reload by the observer process. If the lockfile
        is not modified in 2*interval second or missing, we assume that the
        observer process died and exit with status code 1 or 2.
    '''
    lockfile = os.environ.get('BOTTLE_LOCKFILE')
    bgcheck = FileCheckerThread(lockfile, interval)
    try:
        bgcheck.start()
        server.run(app)
    except KeyboardInterrupt:
        pass
    bgcheck.status, status = 5, bgcheck.status
    bgcheck.join() # bgcheck.status == 5 --> silent exit
    if status: sys.exit(status)


def _reloader_observer(server, app, interval):
    ''' Start a child process with identical commandline arguments and restart
        it as long as it exists with status code 3. Also create a lockfile and
        touch it (update mtime) every interval seconds.
    '''
    fd, lockfile = tempfile.mkstemp(prefix='bottle-reloader.', suffix='.lock')
    os.close(fd) # We only need this file to exist. We never write to it
    try:
        while os.path.exists(lockfile):
            args = [sys.executable] + sys.argv
            environ = os.environ.copy()
            environ['BOTTLE_CHILD'] = 'true'
            environ['BOTTLE_LOCKFILE'] = lockfile
            p = subprocess.Popen(args, env=environ)
            while p.poll() is None: # Busy wait...
                os.utime(lockfile, None) # I am alive!
                time.sleep(interval)
            if p.poll() != 3:
                if os.path.exists(lockfile): os.unlink(lockfile)
                sys.exit(p.poll())
            elif not server.quiet:
                print "Reloading server..."
    except KeyboardInterrupt:
        pass
    if os.path.exists(lockfile): os.unlink(lockfile)






###############################################################################
# Template Adapters ############################################################
###############################################################################

class TemplateError(HTTPError):
    def __init__(self, message):
        HTTPError.__init__(self, 500, message)


class BaseTemplate(object):
    """ Base class and minimal API for template adapters """
    extentions = ['tpl','html','thtml','stpl']
    settings = {} #used in prepare()
    defaults = {} #used in render()

    def __init__(self, source=None, name=None, lookup=[], encoding='utf8', **settings):
        """ Create a new template.
        If the source parameter (str or buffer) is missing, the name argument
        is used to guess a template filename. Subclasses can assume that
        self.source and/or self.filename are set. Both are strings.
        The lookup, encoding and settings parameters are stored as instance
        variables.
        The lookup parameter stores a list containing directory paths.
        The encoding parameter should be used to decode byte strings or files.
        The settings parameter contains a dict for engine-specific settings.
        """
        self.name = name
        self.source = source.read() if hasattr(source, 'read') else source
        self.filename = source.filename if hasattr(source, 'filename') else None
        self.lookup = map(os.path.abspath, lookup)
        self.encoding = encoding
        self.settings = self.settings.copy() # Copy from class variable
        self.settings.update(settings) # Apply 
        if not self.source and self.name:
            self.filename = self.search(self.name, self.lookup)
            if not self.filename:
                raise TemplateError('Template %s not found.' % repr(name))
        if not self.source and not self.filename:
            raise TemplateError('No template specified.')
        self.prepare(**self.settings)

    @classmethod
    def search(cls, name, lookup=[]):
        """ Search name in all directories specified in lookup.
        First without, then with common extensions. Return first hit. """
        if os.path.isfile(name): return name
        for spath in lookup:
            fname = os.path.join(spath, name)
            if os.path.isfile(fname):
                return fname
            for ext in cls.extentions:
                if os.path.isfile('%s.%s' % (fname, ext)):
                    return '%s.%s' % (fname, ext)

    @classmethod
    def global_config(cls, key, *args):
        ''' This reads or sets the global settings stored in class.settings. '''
        if args:
            cls.settings[key] = args[0]
        else:
            return cls.settings[key]

    def prepare(self, **options):
        """ Run preparations (parsing, caching, ...).
        It should be possible to call this again to refresh a template or to
        update settings.
        """
        raise NotImplementedError

    def render(self, *args, **kwargs):
        """ Render the template with the specified local variables and return
        a single byte or unicode string. If it is a byte string, the encoding
        must match self.encoding. This method must be thread-safe!
        Local variables may be provided in dictionaries (*args)
        or directly, as keywords (**kwargs).
        """
        raise NotImplementedError


class MakoTemplate(BaseTemplate):
    def prepare(self, **options):
        from mako.template import Template
        from mako.lookup import TemplateLookup
        options.update({'input_encoding':self.encoding})
        #TODO: This is a hack... https://github.com/defnull/bottle/issues#issue/8
        mylookup = TemplateLookup(directories=['.']+self.lookup, **options)
        if self.source:
            self.tpl = Template(self.source, lookup=mylookup)
        else: #mako cannot guess extentions. We can, but only at top level...
            name = self.name
            if not os.path.splitext(name)[1]:
                name += os.path.splitext(self.filename)[1]
            self.tpl = mylookup.get_template(name)

    def render(self, *args, **kwargs):
        for dictarg in args: kwargs.update(dictarg)
        _defaults = self.defaults.copy()
        _defaults.update(kwargs)
        return self.tpl.render(**_defaults)


class CheetahTemplate(BaseTemplate):
    def prepare(self, **options):
        from Cheetah.Template import Template
        self.context = threading.local()
        self.context.vars = {}
        options['searchList'] = [self.context.vars]
        if self.source:
            self.tpl = Template(source=self.source, **options)
        else:
            self.tpl = Template(file=self.filename, **options)

    def render(self, *args, **kwargs):
        for dictarg in args: kwargs.update(dictarg)
        self.context.vars.update(self.defaults)
        self.context.vars.update(kwargs)
        out = str(self.tpl)
        self.context.vars.clear()
        return [out]


class Jinja2Template(BaseTemplate):
    def prepare(self, filters=None, tests=None, **kwargs):
        from jinja2 import Environment, FunctionLoader
        if 'prefix' in kwargs: # TODO: to be removed after a while
            raise RuntimeError('The keyword argument `prefix` has been removed. '
                'Use the full jinja2 environment name line_statement_prefix instead.')
        self.env = Environment(loader=FunctionLoader(self.loader), **kwargs)
        if filters: self.env.filters.update(filters)
        if tests: self.env.tests.update(tests)
        if self.source:
            self.tpl = self.env.from_string(self.source)
        else:
            self.tpl = self.env.get_template(self.filename)

    def render(self, *args, **kwargs):
        for dictarg in args: kwargs.update(dictarg)
        _defaults = self.defaults.copy()
        _defaults.update(kwargs)
        return self.tpl.render(**_defaults).encode("utf-8")

    def loader(self, name):
        fname = self.search(name, self.lookup)
        if fname:
            with open(fname, "rb") as f:
                return f.read().decode(self.encoding)

class SimpleTALTemplate(BaseTemplate):
    ''' Untested! '''
    def prepare(self, **options):
        from simpletal import simpleTAL
        # TODO: add option to load METAL files during render
        if self.source:
            self.tpl = simpleTAL.compileHTMLTemplate(self.source)
        else:
            with open(self.filename, 'rb') as fp:
                self.tpl = simpleTAL.compileHTMLTemplate(tonat(fp.read()))

    def render(self, *args, **kwargs):
        from simpletal import simpleTALES
        from StringIO import StringIO
        for dictarg in args: kwargs.update(dictarg)
        # TODO: maybe reuse a context instead of always creating one
        context = simpleTALES.Context()
        for k,v in self.defaults.items():
            context.addGlobal(k, v)
        for k,v in kwargs.items():
            context.addGlobal(k, v)
        output = StringIO()
        self.tpl.expand(context, output)
        return output.getvalue()



class SimpleTemplate(BaseTemplate):
    blocks = ('if','elif','else','try','except','finally','for','while','with','def','class')
    dedent_blocks = ('elif', 'else', 'except', 'finally')
    re_pytokens = None

    def prepare(self, escape_func=cgi.escape, noescape=False):
        self.cache = {}
        enc = self.encoding
        self._str = lambda x: touni(x, enc)
        self._escape = lambda x: escape_func(touni(x, enc))
        if noescape:
            self._str, self._escape = self._escape, self._str

    @classmethod
    def split_comment(cls, code):
        """ Removes comments (#...) from python code. """
        if '#' not in code: return code
        if not cls.re_pytokens:
            #: This matches comments and all kinds of quoted strings but does
            #: NOT match comments (#...) within quoted strings. (trust me)
            cls.re_pytokens = re.compile(r'''
              (''(?!')|""(?!")|'{6}|"{6}    # Empty strings (all 4 types)
               |'(?:[^\\']|\\.)+?'          # Single quotes (')
               |"(?:[^\\"]|\\.)+?"          # Double quotes (")
               |'{3}(?:[^\\]|\\.|\n)+?'{3}  # Triple-quoted strings (')
               |"{3}(?:[^\\]|\\.|\n)+?"{3}  # Triple-quoted strings (")
               |\#.*                        # Comments
              )''', re.VERBOSE)
        #: Remove comments only (leave quoted strings as they are)
        subf = lambda m: '' if m.group(0)[0]=='#' else m.group(0)
        return re.sub(cls.re_pytokens, subf, code)

    @cached_property
    def co(self):
        return compile(self.code, self.filename or '<string>', 'exec')

    @cached_property
    def code(self):
        stack = [] # Current Code indentation
        lineno = 0 # Current line of code
        ptrbuffer = [] # Buffer for printable strings and token tuple instances
        codebuffer = [] # Buffer for generated python code
        multiline = dedent = oneline = False
        template = self.source if self.source else open(self.filename).read()

        def yield_tokens(line):
            for i, part in enumerate(re.split(r'\{\{(.*?)\}\}', line)):
                if i % 2:
                    if part.startswith('!'): yield 'RAW', part[1:]
                    else: yield 'CMD', part
                else: yield 'TXT', part

        def flush(): # Flush the ptrbuffer
            if not ptrbuffer: return
            cline = ''
            for line in ptrbuffer:
                for token, value in line:
                    if token == 'TXT': cline += repr(value)
                    elif token == 'RAW': cline += '_str(%s)' % value
                    elif token == 'CMD': cline += '_escape(%s)' % value
                    cline +=  ', '
                cline = cline[:-2] + '\\\n'
            cline = cline[:-2]
            if cline[:-1].endswith('\\\\\\\\\\n'):
                cline = cline[:-7] + cline[-1] # 'nobr\\\\\n' --> 'nobr'
            cline = '_printlist([' + cline + '])'
            del ptrbuffer[:] # Do this before calling code() again
            code(cline)

        def code(stmt):
            for line in stmt.splitlines():
                codebuffer.append('  ' * len(stack) + line.strip())

        for line in template.splitlines(True):
            lineno += 1
            line = line if isinstance(line, unicode)\
                        else unicode(line, encoding=self.encoding)
            if lineno <= 2:
                m = re.search(r"%.*coding[:=]\s*([-\w\.]+)", line)
                if m: self.encoding = m.group(1)
                if m: line = line.replace('coding','coding (removed)')
            if line.strip()[:2].count('%') == 1:
                line = line.split('%',1)[1].lstrip() # Full line following the %
                cline = self.split_comment(line).strip()
                cmd = re.split(r'[^a-zA-Z0-9_]', cline)[0]
                flush() ##encodig (TODO: why?)
                if cmd in self.blocks or multiline:
                    cmd = multiline or cmd
                    dedent = cmd in self.dedent_blocks # "else:"
                    if dedent and not oneline and not multiline:
                        cmd = stack.pop()
                    code(line)
                    oneline = not cline.endswith(':') # "if 1: pass"
                    multiline = cmd if cline.endswith('\\') else False
                    if not oneline and not multiline:
                        stack.append(cmd)
                elif cmd == 'end' and stack:
                    code('#end(%s) %s' % (stack.pop(), line.strip()[3:]))
                elif cmd == 'include':
                    p = cline.split(None, 2)[1:]
                    if len(p) == 2:
                        code("_=_include(%s, _stdout, %s)" % (repr(p[0]), p[1]))
                    elif p:
                        code("_=_include(%s, _stdout)" % repr(p[0]))
                    else: # Empty %include -> reverse of %rebase
                        code("_printlist(_base)")
                elif cmd == 'rebase':
                    p = cline.split(None, 2)[1:]
                    if len(p) == 2:
                        code("globals()['_rebase']=(%s, dict(%s))" % (repr(p[0]), p[1]))
                    elif p:
                        code("globals()['_rebase']=(%s, {})" % repr(p[0]))
                else:
                    code(line)
            else: # Line starting with text (not '%') or '%%' (escaped)
                if line.strip().startswith('%%'):
                    line = line.replace('%%', '%', 1)
                ptrbuffer.append(yield_tokens(line))
        flush()
        return '\n'.join(codebuffer) + '\n'

    def subtemplate(self, _name, _stdout, *args, **kwargs):
        for dictarg in args: kwargs.update(dictarg)
        if _name not in self.cache:
            self.cache[_name] = self.__class__(name=_name, lookup=self.lookup)
        return self.cache[_name].execute(_stdout, kwargs)

    def execute(self, _stdout, *args, **kwargs):
        for dictarg in args: kwargs.update(dictarg)
        env = self.defaults.copy()
        env.update({'_stdout': _stdout, '_printlist': _stdout.extend,
               '_include': self.subtemplate, '_str': self._str,
               '_escape': self._escape})
        env.update(kwargs)
        eval(self.co, env)
        if '_rebase' in env:
            subtpl, rargs = env['_rebase']
            subtpl = self.__class__(name=subtpl, lookup=self.lookup)
            rargs['_base'] = _stdout[:] #copy stdout
            del _stdout[:] # clear stdout
            return subtpl.execute(_stdout, rargs)
        return env

    def render(self, *args, **kwargs):
        """ Render the template using keyword arguments as local variables. """
        for dictarg in args: kwargs.update(dictarg)
        stdout = []
        self.execute(stdout, kwargs)
        return ''.join(stdout)


def template(*args, **kwargs):
    '''
    Get a rendered template as a string iterator.
    You can use a name, a filename or a template string as first parameter.
    Template rendering arguments can be passed as dictionaries
    or directly (as keyword arguments).
    '''
    tpl = args[0] if args else None
    template_adapter = kwargs.pop('template_adapter', SimpleTemplate)
    if tpl not in TEMPLATES or DEBUG:
        settings = kwargs.pop('template_settings', {})
        lookup = kwargs.pop('template_lookup', TEMPLATE_PATH)
        if isinstance(tpl, template_adapter):
            TEMPLATES[tpl] = tpl
            if settings: TEMPLATES[tpl].prepare(**settings)
        elif "\n" in tpl or "{" in tpl or "%" in tpl or '$' in tpl:
            TEMPLATES[tpl] = template_adapter(source=tpl, lookup=lookup, **settings)
        else:
            TEMPLATES[tpl] = template_adapter(name=tpl, lookup=lookup, **settings)
    if not TEMPLATES[tpl]:
        abort(500, 'Template (%s) not found' % tpl)
    for dictarg in args[1:]: kwargs.update(dictarg)
    return TEMPLATES[tpl].render(kwargs)

mako_template = functools.partial(template, template_adapter=MakoTemplate)
cheetah_template = functools.partial(template, template_adapter=CheetahTemplate)
jinja2_template = functools.partial(template, template_adapter=Jinja2Template)
simpletal_template = functools.partial(template, template_adapter=SimpleTALTemplate)

def view(tpl_name, **defaults):
    ''' Decorator: renders a template for a handler.
        The handler can control its behavior like that:

          - return a dict of template vars to fill out the template
          - return something other than a dict and the view decorator will not
            process the template, but return the handler result as is.
            This includes returning a HTTPResponse(dict) to get,
            for instance, JSON with autojson or other castfilters.
    '''
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            if isinstance(result, (dict, DictMixin)):
                tplvars = defaults.copy()
                tplvars.update(result)
                return template(tpl_name, **tplvars)
            return result
        return wrapper
    return decorator

mako_view = functools.partial(view, template_adapter=MakoTemplate)
cheetah_view = functools.partial(view, template_adapter=CheetahTemplate)
jinja2_view = functools.partial(view, template_adapter=Jinja2Template)
simpletal_view = functools.partial(view, template_adapter=SimpleTALTemplate)





###############################################################################
# Constants and Globals ########################################################
###############################################################################

TEMPLATE_PATH = ['./', './views/']
TEMPLATES = {}
DEBUG = False
MEMFILE_MAX = 1024*100

#: A dict to map HTTP status codes (e.g. 404) to phrases (e.g. 'Not Found')
HTTP_CODES = httplib.responses
HTTP_CODES[418] = "I'm a teapot" # RFC 2324

#: The default template used for error pages. Override with @error()
ERROR_PAGE_TEMPLATE = """
%try:
    %from bottle import DEBUG, HTTP_CODES, request
    %status_name = HTTP_CODES.get(e.status, 'Unknown').title()
    <!DOCTYPE HTML PUBLIC "-//IETF//DTD HTML 2.0//EN">
    <html>
        <head>
            <title>Error {{e.status}}: {{status_name}}</title>
            <style type="text/css">
              html {background-color: #eee; font-family: sans;}
              body {background-color: #fff; border: 1px solid #ddd; padding: 15px; margin: 15px;}
              pre {background-color: #eee; border: 1px solid #ddd; padding: 5px;}
            </style>
        </head>
        <body>
            <h1>Error {{e.status}}: {{status_name}}</h1>
            <p>Sorry, the requested URL <tt>{{request.url}}</tt> caused an error:</p>
            <pre>{{str(e.output)}}</pre>
            %if DEBUG and e.exception:
              <h2>Exception:</h2>
              <pre>{{repr(e.exception)}}</pre>
            %end
            %if DEBUG and e.traceback:
              <h2>Traceback:</h2>
              <pre>{{e.traceback}}</pre>
            %end
        </body>
    </html>
%except ImportError:
    <b>ImportError:</b> Could not generate the error page. Please add bottle to sys.path
%end
"""

#: A thread-save instance of :class:`Request` representing the `current` request.
request = Request()

#: A thread-save instance of :class:`Response` used to build the HTTP response.
response = Response()

#: A thread-save namepsace. Not used by Bottle.
local = threading.local()

# Initialize app stack (create first empty Bottle app)
# BC: 0.6.4 and needed for run()
app = default_app = AppStack()
app.push()
