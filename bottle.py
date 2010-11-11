# -*- coding: utf-8 -*-
"""
Bottle is a fast and simple micro-framework for small web applications. It
offers request dispatching (Routes) with url parameter support, templates,
a built-in HTTP Server and adapters for many third party WSGI/HTTP-server and
template engines - all in a single file and with no dependencies other than the
Python Standard Library.

Homepage and documentation: http://bottle.paws.de/

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


Example
-------

This is an example::

    from bottle import route, run, request, response, static_file, abort
    
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
    def static(filename):
        return static_file(filename, root='/path/to/static/files/')
    
    run(host='localhost', port=8080)
"""

from __future__ import with_statement

__author__ = 'Marcel Hellkamp'
__version__ = '0.8.5'
__license__ = 'MIT'

import base64
import cgi
import email.utils
import functools
import hmac
import inspect
import itertools
import mimetypes
import os
import re
import subprocess
import sys
import thread
import threading
import time
import tokenize
import tempfile

from Cookie import SimpleCookie
from tempfile import TemporaryFile
from traceback import format_exc
from urllib import quote as urlquote
from urlparse import urlunsplit, urljoin

try:
    from collections import MutableMapping as DictMixin
except ImportError: # pragma: no cover
    from UserDict import DictMixin

try:
    from urlparse import parse_qs
except ImportError: # pragma: no cover
    from cgi import parse_qs

try:
    import cPickle as pickle
except ImportError: # pragma: no cover
    import pickle

try:
    try:
        from json import dumps as json_dumps
    except ImportError: # pragma: no cover
        from simplejson import dumps as json_dumps
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
    StringType = bytes
    def touni(x, enc='utf8'): # Convert anything to unicode (py3)
        return str(x, encoding=enc) if isinstance(x, bytes) else str(x)
else:
    from StringIO import StringIO as BytesIO
    from types import StringType
    NCTextIOWrapper = None
    def touni(x, enc='utf8'): # Convert anything to unicode (py2)
        return x if isinstance(x, unicode) else unicode(str(x), encoding=enc)

def tob(data, enc='utf8'): # Convert strings to bytes (py2 and py3)
    return data.encode(enc) if isinstance(data, unicode) else data

# Background compatibility
import warnings
def depr(message, critical=False):
    if critical: raise DeprecationWarning(message)
    warnings.warn(message, DeprecationWarning, stacklevel=3)






# Exceptions and Events

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
        return ''.join(ERROR_PAGE_TEMPLATE.render(e=self))






# Routing

class RouteError(BottleException):
    """ This is a base class for all routing related exceptions """


class RouteSyntaxError(RouteError):
    """ The route parser found something not supported by this router """


class RouteBuildError(RouteError):
    """ The route could not been build """


class Route(object):
    ''' Represents a single route and can parse the dynamic route syntax '''
    syntax = re.compile(r'(.*?)(?<!\\):([a-zA-Z_]+)?(?:#(.*?)#)?')
    default = '[^/]+'

    def __init__(self, route, target=None, name=None, static=False):
        """ Create a Route. The route string may contain `:key`,
            `:key#regexp#` or `:#regexp#` tokens for each dynamic part of the
            route. These can be escaped with a backslash infront of the `:`
            and are compleately ignored if static is true. A name may be used
            to refer to this route later (depends on Router)
        """
        self.route = route
        self.target = target
        self.name = name
        if static:
            self.route = self.route.replace(':','\\:')
        self._tokens = None

    def tokens(self):
        """ Return a list of (type, value) tokens. """
        if not self._tokens:
            self._tokens = list(self.tokenise(self.route))
        return self._tokens

    @classmethod
    def tokenise(cls, route):
        ''' Split a string into an iterator of (type, value) tokens. '''
        match = None
        for match in cls.syntax.finditer(route):
            pre, name, rex = match.groups()
            if pre: yield ('TXT', pre.replace('\\:',':'))
            if rex and name: yield ('VAR', (rex, name))
            elif name: yield ('VAR', (cls.default, name))
            elif rex: yield ('ANON', rex)
        if not match:
            yield ('TXT', route.replace('\\:',':'))
        elif match.end() < len(route):
            yield ('TXT', route[match.end():].replace('\\:',':'))

    def group_re(self):
        ''' Return a regexp pattern with named groups '''
        out = ''
        for token, data in self.tokens():
            if   token == 'TXT':  out += re.escape(data)
            elif token == 'VAR':  out += '(?P<%s>%s)' % (data[1], data[0])
            elif token == 'ANON': out += '(?:%s)' % data
        return out

    def flat_re(self):
        ''' Return a regexp pattern with non-grouping parentheses '''
        rf = lambda m: m.group(0) if len(m.group(1)) % 2 else m.group(1) + '(?:'
        return re.sub(r'(\\*)(\(\?P<[^>]*>|\((?!\?))', rf, self.group_re())

    def format_str(self):
        ''' Return a format string with named fields. '''
        out, i = '', 0
        for token, value in self.tokens():
            if token == 'TXT': out += value.replace('%','%%')
            elif token == 'ANON': out += '%%(anon%d)s' % i; i+=1
            elif token == 'VAR': out += '%%(%s)s' % value[1]
        return out

    @property
    def static(self):
        return not self.is_dynamic()

    def is_dynamic(self):
        ''' Return true if the route contains dynamic parts '''
        for token, value in self.tokens():
            if token != 'TXT':
                return True
        return False

    def __repr__(self):
        return "<Route(%s) />" % repr(self.route)

    def __eq__(self, other):
        return self.route == other.route

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

    def add(self, route, target=None, **ka):
        """ Add a route->target pair or a :class:`Route` object to the Router.
            Return the Route object. See :class:`Route` for details.
        """
        if not isinstance(route, Route):
            route = Route(route, target, **ka)
        if self.get_route(route):
            return RouteError('Route %s is not uniqe.' % route)
        self.routes.append(route)
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
        return None, {}

    def build(self, _name, **args):
        ''' Build an URI out of a named route and values for te wildcards. '''
        try:
            return self.named[_name] % args
        except KeyError:
            raise RouteBuildError("No route found with name '%s'." % _name)

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
                self.dynamic.append((re.compile('(^%s$)'%fpatt),[(route.target, gregexp)]))
            except re.error, e:
                raise RouteSyntaxError("Could not add Route: %s (%s)" % (route, e))

    def __eq__(self, other):
        return self.routes == other.routes





# WSGI abstraction: Application, Request and Response objects

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

    def route(self, path=None, method='GET', **kargs):
        """ Decorator: bind a function to a GET request path.

            If the path parameter is None, the signature of the decorated
            function is used to generate the paths. See yieldroutes()
            for details.

            The method parameter (default: GET) specifies the HTTP request
            method to listen to. You can specify a list of methods too. 
        """
        def wrapper(callback):
            routes = [path] if path else yieldroutes(callback)
            methods = method.split(';') if isinstance(method, str) else method
            for r in routes:
                for m in methods:
                    r, m = r.strip().lstrip('/'), m.strip().upper()
                    old = self.routes.get_route(r, **kargs)
                    if old:
                        old.target[m] = callback
                    else:
                        self.routes.add(r, {m: callback}, **kargs)
                        self.routes.compile()
            return callback
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
        """ Decorator: Registrer an output handler for a HTTP error code"""
        def wrapper(handler):
            self.error_handler[int(code)] = handler
            return handler
        return wrapper

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
        and isinstance(out[0], (StringType, unicode)):
            out = out[0][0:0].join(out) # b'abc'[0:0] -> b''
        # Encode unicode strings
        if isinstance(out, unicode):
            out = out.encode(response.charset)
        # Byte Strings are just returned
        if isinstance(out, StringType):
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
        if isinstance(first, StringType):
            return itertools.chain([first], out)
        if isinstance(first, unicode):
            return itertools.imap(lambda x: x.encode(response.charset),
                                  itertools.chain([first], out))
        return self._cast(HTTPError(500, 'Unsupported response type: %s'\
                                         % type(first)), request, response)

    def __call__(self, environ, start_response):
        """ The bottle WSGI-interface. """
        try:
            environ['bottle.app'] = self
            request.bind(environ)
            response.bind(self)
            out = self.handle(request.path, request.method)
            out = self._cast(out, request, response)
            # rfc2616 section 4.3
            if response.status in (100, 101, 204, 304) or request.method == 'HEAD':
                out = []
            status = '%d %s' % (response.status, HTTP_CODES[response.status])
            start_response(status, response.headerlist)
            return out
        except (KeyboardInterrupt, SystemExit, MemoryError):
            raise
        except Exception, e:
            if not self.catchall:
                raise
            err = '<h1>Critical error while processing request: %s</h1>' \
                  % environ.get('PATH_INFO', '/')
            if DEBUG:
                err += '<h2>Error:</h2>\n<pre>%s</pre>\n' % repr(e)
                err += '<h2>Traceback:</h2>\n<pre>%s</pre>\n' % format_exc(10)
            environ['wsgi.errors'].write(err) #TODO: wsgi.error should not get html
            start_response('500 INTERNAL SERVER ERROR', [('Content-Type', 'text/html')])
            return [tob(err)]


class Request(threading.local, DictMixin):
    """ Represents a single HTTP request using thread-local attributes.
        The Request object wraps a WSGI environment and can be used as such.
    """
    def __init__(self, environ=None, config=None):
        """ Create a new Request instance.
        
            You usually don't do this but use the global `bottle.request`
            instance instead.
        """
        self.bind(environ or {}, config)

    def bind(self, environ, config=None):
        """ Bind a new WSGI enviroment.
            
            This is done automatically for the global `bottle.request`
            instance on every request.
        """
        self.environ = environ
        self.config = config or {}
        # These attributes are used anyway, so it is ok to compute them here
        self.path = '/' + environ.get('PATH_INFO', '/').lstrip('/')
        self.method = environ.get('REQUEST_METHOD', 'GET').upper()

    @property
    def _environ(self):
        depr("Request._environ renamed to Request.environ")
        return self.environ

    def copy(self):
        ''' Returns a copy of self '''
        return Request(self.environ.copy(), self.config)
        
    def path_shift(self, shift=1):
        ''' Shift path fragments from PATH_INFO to SCRIPT_NAME and vice versa.

          :param shift: The number of path fragments to shift. May be negative to
            change the shift direction. (default: 1)
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
            self.bind(self.environ, self.config)
        elif key == 'wsgi.input': todelete = ('body','forms','files','params')
        elif key == 'QUERY_STRING': todelete = ('get','params')
        elif key.startswith('HTTP_'): todelete = ('headers', 'cookies')
        for key in todelete:
            if 'bottle.' + key in self.environ:
                del self.environ['bottle.' + key]

    @property
    def query_string(self):
        """ The content of the QUERY_STRING environment variable. """
        return self.environ.get('QUERY_STRING', '')

    @property
    def fullpath(self):
        """ Request path including SCRIPT_NAME (if present) """
        return self.environ.get('SCRIPT_NAME', '').rstrip('/') + self.path

    @property
    def url(self):
        """ Full URL as requested by the client (computed).

            This value is constructed out of different environment variables
            and includes scheme, host, port, scriptname, path and query string. 
        """
        scheme = self.environ.get('wsgi.url_scheme', 'http')
        host   = self.environ.get('HTTP_X_FORWARDED_HOST', self.environ.get('HTTP_HOST', None))
        if not host:
            host = self.environ.get('SERVER_NAME')
            port = self.environ.get('SERVER_PORT', '80')
            if scheme + port not in ('https443', 'http80'):
                host += ':' + port
        parts = (scheme, host, urlquote(self.fullpath), self.query_string, '')
        return urlunsplit(parts)

    @property
    def content_length(self):
        """ Content-Length header as an integer, -1 if not specified """
        return int(self.environ.get('CONTENT_LENGTH','') or -1)

    @property
    def header(self):
        ''' :class:`HeaderDict` filled with request headers.

            HeaderDict keys are case insensitive str.title()d 
        '''
        if 'bottle.headers' not in self.environ:
            header = self.environ['bottle.headers'] = HeaderDict()
            for key, value in self.environ.iteritems():
                if key.startswith('HTTP_'):
                    key = key[5:].replace('_','-').title()
                    header[key] = value
        return self.environ['bottle.headers']

    @property
    def GET(self):
        """ The QUERY_STRING parsed into a MultiDict.

            Keys and values are strings. Multiple values per key are possible.
            See MultiDict for details.
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
        """ Property: The HTTP POST body parsed into a MultiDict.

            This supports urlencoded and multipart POST requests. Multipart
            is commonly used for file uploads and may result in some of the
            values being cgi.FieldStorage objects instead of strings.

            Multiple values per key are possible. See MultiDict for details.
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
        """ Property: HTTP POST form data parsed into a MultiDict. """
        if 'bottle.forms' not in self.environ: self.POST
        return self.environ['bottle.forms']

    @property
    def files(self):
        """ Property: HTTP POST file uploads parsed into a MultiDict. """
        if 'bottle.files' not in self.environ: self.POST
        return self.environ['bottle.files']
        
    @property
    def params(self):
        """ A combined MultiDict with POST and GET parameters. """
        if 'bottle.params' not in self.environ:
            self.environ['bottle.params'] = MultiDict(self.GET)
            self.environ['bottle.params'].update(dict(self.forms))
        return self.environ['bottle.params']

    @property
    def body(self):
        """ The HTTP request body as a seekable buffer object.
        
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
        """ HTTP authorisation data as a (user, passwd) tuple. (experimental)
        
            This implementation currently only supports basic auth and returns
            None on errors.
        """
        return parse_auth(self.environ.get('HTTP_AUTHORIZATION',''))

    @property
    def COOKIES(self):
        """ Cookie information parsed into a dictionary.
        
            Secure cookies are NOT decoded automatically. See
            Request.get_cookie() for details.
        """
        if 'bottle.cookies' not in self.environ:
            raw_dict = SimpleCookie(self.environ.get('HTTP_COOKIE',''))
            self.environ['bottle.cookies'] = {}
            for cookie in raw_dict.itervalues():
                self.environ['bottle.cookies'][cookie.key] = cookie.value
        return self.environ['bottle.cookies']

    def get_cookie(self, name, secret=None):
        """ Return the (decoded) value of a cookie. """
        value = self.COOKIES.get(name)
        dec = cookie_decode(value, secret) if secret else None
        return dec or value

    @property
    def is_ajax(self):
        ''' True if the request was generated using XMLHttpRequest '''
        #TODO: write tests
        return self.header.get('X-Requested-With') == 'XMLHttpRequest'



class Response(threading.local):
    """ Represents a single HTTP response using thread-local attributes.
    """

    def __init__(self, config=None):
        self.bind(config)

    def bind(self, config=None):
        """ Resets the Response object to its factory defaults. """
        self._COOKIES = None
        self.status = 200
        self.headers = HeaderDict()
        self.content_type = 'text/html; charset=UTF-8'
        self.config = config or {}

    @property
    def header(self):
        depr("Response.header renamed to Response.headers")
        return self.headers

    def copy(self):
        ''' Returns a copy of self '''
        copy = Response(self.config)
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
        """ A dict-like SimpleCookie instance. Use Response.set_cookie() instead. """
        if not self._COOKIES:
            self._COOKIES = SimpleCookie()
        return self._COOKIES

    def set_cookie(self, key, value, secret=None, **kargs):
        """ Add a new cookie with various options.
        
        If the cookie value is not a string, a secure cookie is created.
        
        Possible options are:
            expires, path, comment, domain, max_age, secure, version, httponly
            See http://de.wikipedia.org/wiki/HTTP-Cookie#Aufbau for details
        """
        if not isinstance(value, basestring):
            if not secret:
                raise TypeError('Cookies must be strings when secret is not set')
            value = cookie_encode(value, secret).decode('ascii') #2to3 hack
        self.COOKIES[key] = value
        for k, v in kargs.iteritems():
            self.COOKIES[key][k.replace('_', '-')] = v

    def get_content_type(self):
        """ Current 'Content-Type' header. """
        return self.headers['Content-Type']

    def set_content_type(self, value):
        self.headers['Content-Type'] = value

    content_type = property(get_content_type, set_content_type, None,
                            get_content_type.__doc__)






# Data Structures

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



# Module level functions

# Output filter

def dict2json(d):
    response.content_type = 'application/json'
    return json_dumps(d)


def abort(code=500, text='Unknown Error: Appliction stopped.'):
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






# Utilities

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
    except (TypeError, ValueError, IndexError):
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
    ''' Encode and sign a pickle-able object. Return a string '''
    msg = base64.b64encode(pickle.dumps(data, -1))
    sig = base64.b64encode(hmac.new(key, msg).digest())
    return tob('!') + sig + tob('?') + msg


def cookie_decode(data, key):
    ''' Verify and decode an encoded string. Return an object or None'''
    data = tob(data)
    if cookie_is_encoded(data):
        sig, msg = data.split(tob('?'), 1)
        if _lscmp(sig[1:], base64.b64encode(hmac.new(key, msg).digest())):
            return pickle.loads(base64.b64decode(msg))
    return None


def cookie_is_encoded(data):
    ''' Return True if the argument looks like a encoded cookie.'''
    return bool(data.startswith(tob('!')) and tob('?') in data)


def tonativefunc(enc='utf-8'):
    ''' Returns a function that turns everything into 'native' strings using enc '''
    if sys.version_info >= (3,0,0):
        return lambda x: x.decode(enc) if isinstance(x, bytes) else str(x)
    return lambda x: x.encode(enc) if isinstance(x, unicode) else str(x)


def yieldroutes(func):
    """ Return a generator for routes that match the signature (name, args) 
    of the func parameter. This may yield more than one route if the function
    takes optional keyword arguments. The output is best described by example:
      a()         -> '/a'
      b(x, y)     -> '/b/:x/:y'
      c(x, y=5)   -> '/c/:x' and '/c/:x/:y'
      d(x=5, y=6) -> '/d' and '/d/:x' and '/d/:x/:y'
    """
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
          change ths shift direction. (default: 1)
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


route  = functools.wraps(Bottle.route)(lambda *a, **ka: app().route(*a, **ka))
get    = functools.wraps(Bottle.get)(lambda *a, **ka: app().get(*a, **ka))
post   = functools.wraps(Bottle.post)(lambda *a, **ka: app().post(*a, **ka))
put    = functools.wraps(Bottle.put)(lambda *a, **ka: app().put(*a, **ka))
delete = functools.wraps(Bottle.delete)(lambda *a, **ka: app().delete(*a, **ka))
error  = functools.wraps(Bottle.error)(lambda *a, **ka: app().error(*a, **ka))
url    = functools.wraps(Bottle.get_url)(lambda *a, **ka: app().get_url(*a, **ka))
mount  = functools.wraps(Bottle.mount)(lambda *a, **ka: app().mount(*a, **ka))

def default():
    depr("The default() decorator is deprecated. Use @error(404) instead.")
    return error(404)






# Server adapter

class ServerAdapter(object):
    quiet = False

    def __init__(self, host='127.0.0.1', port=8080, **kargs):
        self.options = kargs
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
        flup.server.fcgi.WSGIServer(handler, bindAddress=(self.host, self.port)).run()


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
        from paste.translogger import TransLogger
        app = TransLogger(handler)
        httpserver.serve(app, host=self.host, port=str(self.port), **self.options)


class FapwsServer(ServerAdapter):
    """
    Extremly fast webserver using libev.
    See http://william-os4y.livejournal.com/
    """
    def run(self, handler): # pragma: no cover
        import fapws._evwsgi as evwsgi
        from fapws import base
        evwsgi.start(self.host, self.port)
        evwsgi.set_base_module(base)
        def app(environ, start_response):
            environ['wsgi.multiprocess'] = False
            return handler(environ, start_response)
        evwsgi.wsgi_cb(('',app))
        evwsgi.run()


class TornadoServer(ServerAdapter):
    """ Untested. As described here:
        http://github.com/facebook/tornado/blob/master/tornado/wsgi.py#L187 """
    def run(self, handler): # pragma: no cover
        import tornado.wsgi
        import tornado.httpserver
        import tornado.ioloop
        container = tornado.wsgi.WSGIContainer(handler)
        server = tornado.httpserver.HTTPServer(container)
        server.listen(port=self.port)
        tornado.ioloop.IOLoop.instance().start()


class AppEngineServer(ServerAdapter):
    """ Untested. """
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


class GunicornServer(ServerAdapter):
    """ Untested. """
    def run(self, handler):
        import gunicorn.arbiter
        gunicorn.arbiter.Arbiter((self.host, self.port), 4, handler).run()
    

class EventletServer(ServerAdapter):
    """ Untested """
    def run(self, handler):
        from eventlet import wsgi, listen
        wsgi.server(listen((self.host, self.port)), handler)


class RocketServer(ServerAdapter):
    """ Untested. As requested in issue 63
        http://github.com/defnull/bottle/issues/#issue/63 """
    def run(self, handler):
        from rocket import Rocket
        server = Rocket((self.host, self.port), 'wsgi', { 'wsgi_app' : handler })
        server.start()
            
        
class AutoServer(ServerAdapter):
    """ Untested. """
    adapters = [CherryPyServer, PasteServer, TwistedServer, WSGIRefServer]
    def run(self, handler):
        for sa in self.adapters:
            try:
                return sa(self.host, self.port, **self.options).run(handler)
            except ImportError:
                pass


def run(app=None, server=WSGIRefServer, host='127.0.0.1', port=8080,
        interval=1, reloader=False, quiet=False, **kargs):
    """ Runs bottle as a web server. """
    app = app if app else default_app()
    # Instantiate server, if it is a class instead of an instance
    if isinstance(server, type):
        server = server(host=host, port=port, **kargs)
    if not isinstance(server, ServerAdapter):
        raise RuntimeError("Server must be a subclass of WSGIAdapter")
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
    except KeyboardInterrupt: pass
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
            try:
                path = inspect.getsourcefile(module)
                if path and exists(path): files[path] = mtime(path)
            except TypeError: pass
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
    except KeyboardInterrupt, e: pass
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
    except KeyboardInterrupt: pass
    if os.path.exists(lockfile): os.unlink(lockfile)



# Templates

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

    def render(self, **args):
        """ Render the template with the specified local variables and return
        a single byte or unicode string. If it is a byte string, the encoding
        must match self.encoding. This method must be thread-safe!
        """
        raise NotImplementedError


class MakoTemplate(BaseTemplate):
    def prepare(self, **options):
        from mako.template import Template
        from mako.lookup import TemplateLookup
        options.update({'input_encoding':self.encoding})
        #TODO: This is a hack... http://github.com/defnull/bottle/issues#issue/8
        mylookup = TemplateLookup(directories=['.']+self.lookup, **options)
        if self.source:
            self.tpl = Template(self.source, lookup=mylookup)
        else: #mako cannot guess extentions. We can, but only at top level...
            name = self.name
            if not os.path.splitext(name)[1]:
                name += os.path.splitext(self.filename)[1]
            self.tpl = mylookup.get_template(name)

    def render(self, **args):
        _defaults = self.defaults.copy()
        _defaults.update(args)
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

    def render(self, **args):
        self.context.vars.update(self.defaults)
        self.context.vars.update(args)
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

    def render(self, **args):
        _defaults = self.defaults.copy()
        _defaults.update(args)
        return self.tpl.render(**_defaults).encode("utf-8")

    def loader(self, name):
        fname = self.search(name, self.lookup)
        if fname:
            with open(fname, "rb") as f:
                return f.read().decode(self.encoding)


class SimpleTemplate(BaseTemplate):
    blocks = ('if','elif','else','try','except','finally','for','while','with','def','class')
    dedent_blocks = ('elif', 'else', 'except', 'finally')

    def prepare(self, escape_func=cgi.escape, noescape=False):
        self.cache = {}
        if self.source:
            self.code = self.translate(self.source)
            self.co = compile(self.code, '<string>', 'exec')
        else:
            self.code = self.translate(open(self.filename).read())
            self.co = compile(self.code, self.filename, 'exec')
        enc = self.encoding
        self._str = lambda x: touni(x, enc)
        self._escape = lambda x: escape_func(touni(x, enc))
        if noescape:
            self._str, self._escape = self._escape, self._str

    def translate(self, template):
        stack = [] # Current Code indentation
        lineno = 0 # Current line of code
        ptrbuffer = [] # Buffer for printable strings and token tuple instances
        codebuffer = [] # Buffer for generated python code
        touni = functools.partial(unicode, encoding=self.encoding)
        multiline = dedent = False

        def yield_tokens(line):
            for i, part in enumerate(re.split(r'\{\{(.*?)\}\}', line)):
                if i % 2:
                    if part.startswith('!'): yield 'RAW', part[1:]
                    else: yield 'CMD', part
                else: yield 'TXT', part

        def split_comment(codeline):
            """ Removes comments from a line of code. """
            line = codeline.splitlines()[0]
            try:
                tokens = list(tokenize.generate_tokens(iter(line).next))
            except tokenize.TokenError:
                return line.rsplit('#',1) if '#' in line else (line, '')
            for token in tokens:
                if token[0] == tokenize.COMMENT:
                    start, end = token[2][1], token[3][1]
                    return codeline[:start] + codeline[end:], codeline[start:end]
            return line, ''

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
                cline = split_comment(line)[0].strip()
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

    def subtemplate(self, _name, _stdout, **args):
        if _name not in self.cache:
            self.cache[_name] = self.__class__(name=_name, lookup=self.lookup)
        return self.cache[_name].execute(_stdout, **args)

    def execute(self, _stdout, **args):
        env = self.defaults.copy()
        env.update({'_stdout': _stdout, '_printlist': _stdout.extend,
               '_include': self.subtemplate, '_str': self._str,
               '_escape': self._escape})
        env.update(args)
        eval(self.co, env)
        if '_rebase' in env:
            subtpl, rargs = env['_rebase']
            subtpl = self.__class__(name=subtpl, lookup=self.lookup)
            rargs['_base'] = _stdout[:] #copy stdout
            del _stdout[:] # clear stdout
            return subtpl.execute(_stdout, **rargs)
        return env

    def render(self, **args):
        """ Render the template using keyword arguments as local variables. """
        stdout = []
        self.execute(stdout, **args)
        return ''.join(stdout)


def template(tpl, template_adapter=SimpleTemplate, **kwargs):
    '''
    Get a rendered template as a string iterator.
    You can use a name, a filename or a template string as first parameter.
    '''
    if tpl not in TEMPLATES or DEBUG:
        settings = kwargs.get('template_settings',{})
        lookup = kwargs.get('template_lookup', TEMPLATE_PATH)
        if isinstance(tpl, template_adapter):
            TEMPLATES[tpl] = tpl
            if settings: TEMPLATES[tpl].prepare(**settings)
        elif "\n" in tpl or "{" in tpl or "%" in tpl or '$' in tpl:
            TEMPLATES[tpl] = template_adapter(source=tpl, lookup=lookup, **settings)
        else:
            TEMPLATES[tpl] = template_adapter(name=tpl, lookup=lookup, **settings)
    if not TEMPLATES[tpl]:
        abort(500, 'Template (%s) not found' % tpl)
    return TEMPLATES[tpl].render(**kwargs)

mako_template = functools.partial(template, template_adapter=MakoTemplate)
cheetah_template = functools.partial(template, template_adapter=CheetahTemplate)
jinja2_template = functools.partial(template, template_adapter=Jinja2Template)

def view(tpl_name, **defaults):
    ''' Decorator: renders a template for a handler.
        The handler can control its behavior like that:

          - return a dict of template vars to fill out the template
          - return something other than a dict and the view decorator will not
            process the template, but return the handler result as is.
            This includes returning a HTTPResponse(dict) to get,
            for instance, JSON with autojson or other castfilters
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






# Modul initialization and configuration

TEMPLATE_PATH = ['./', './views/']
TEMPLATES = {}
DEBUG = False
MEMFILE_MAX = 1024*100
HTTP_CODES = {
    100: 'CONTINUE',
    101: 'SWITCHING PROTOCOLS',
    200: 'OK',
    201: 'CREATED',
    202: 'ACCEPTED',
    203: 'NON-AUTHORITATIVE INFORMATION',
    204: 'NO CONTENT',
    205: 'RESET CONTENT',
    206: 'PARTIAL CONTENT',
    300: 'MULTIPLE CHOICES',
    301: 'MOVED PERMANENTLY',
    302: 'FOUND',
    303: 'SEE OTHER',
    304: 'NOT MODIFIED',
    305: 'USE PROXY',
    306: 'RESERVED',
    307: 'TEMPORARY REDIRECT',
    400: 'BAD REQUEST',
    401: 'UNAUTHORIZED',
    402: 'PAYMENT REQUIRED',
    403: 'FORBIDDEN',
    404: 'NOT FOUND',
    405: 'METHOD NOT ALLOWED',
    406: 'NOT ACCEPTABLE',
    407: 'PROXY AUTHENTICATION REQUIRED',
    408: 'REQUEST TIMEOUT',
    409: 'CONFLICT',
    410: 'GONE',
    411: 'LENGTH REQUIRED',
    412: 'PRECONDITION FAILED',
    413: 'REQUEST ENTITY TOO LARGE',
    414: 'REQUEST-URI TOO LONG',
    415: 'UNSUPPORTED MEDIA TYPE',
    416: 'REQUESTED RANGE NOT SATISFIABLE',
    417: 'EXPECTATION FAILED',
    500: 'INTERNAL SERVER ERROR',
    501: 'NOT IMPLEMENTED',
    502: 'BAD GATEWAY',
    503: 'SERVICE UNAVAILABLE',
    504: 'GATEWAY TIMEOUT',
    505: 'HTTP VERSION NOT SUPPORTED',
}
""" A dict of known HTTP error and status codes """



ERROR_PAGE_TEMPLATE = SimpleTemplate("""
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
""")
""" The HTML template used for error messages """

request = Request()
""" Whenever a page is requested, the :class:`Bottle` WSGI handler stores
metadata about the current request into this instance of :class:`Request`.
It is thread-safe and can be accessed from within handler functions. """

response = Response()
""" The :class:`Bottle` WSGI handler uses metadata assigned to this instance
of :class:`Response` to generate the WSGI response. """

local = threading.local()
""" Thread-local namespace. Not used by Bottle, but could get handy """

# Initialize app stack (create first empty Bottle app)
# BC: 0.6.4 and needed for run()
app = default_app = AppStack()
app.push()
