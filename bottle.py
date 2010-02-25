# -*- coding: utf-8 -*-
"""
Bottle is a fast and simple micro-framework for small web applications. It
offers request dispatching (Routes) with url parameter support, templates,
a built-in HTTP Server and adapters for many third party WSGI/HTTP-server and
template engines - all in a single file and with no dependencies other than the
Python Standard Library.

Homepage and documentation: http://wiki.github.com/defnull/bottle

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

    from bottle import route, run, request, response, send_file, abort
    
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
    def static_file(filename):
        send_file(filename, root='/path/to/static/files/')
    
    run(host='localhost', port=8080)
"""
from __future__ import with_statement
__author__ = 'Marcel Hellkamp'
__version__ = '0.7.0a'
__license__ = 'MIT'

import types
import sys
import cgi
import mimetypes
import os
import os.path
from traceback import format_exc
import re
import random
import threading
import time
import warnings
import email.utils
from Cookie import SimpleCookie
import subprocess
import thread
from tempfile import TemporaryFile
import hmac
import base64
from urllib import quote as urlquote
from urlparse import urlunsplit, urljoin
import functools
import inspect

try:
  from collections import MutableMapping as DictMixin
except ImportError: # pragma: no cover
  from UserDict import DictMixin

if sys.version_info >= (3,0,0): # pragma: no cover
    # See Request.POST
    from io import BytesIO
    from io import TextIOWrapper
else:
    from StringIO import StringIO as BytesIO
    TextIOWrapper = None

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






# Exceptions and Events

class BottleException(Exception):
    """ A base class for exceptions used by bottle. """
    pass


class HTTPResponse(BottleException):
    """ Used to break execution and imediately finish the response """
    def __init__(self, output='', status=200, header=None):
        super(BottleException, self).__init__("HTTP Response %d" % status)
        self.status = int(status)
        self.output = output
        self.header = HeaderDict(header) if header else None

    def apply(self, response):
        if self.header:
            for key, value in self.header.iterallitems():
                response.header[key] = value
        response.status = self.status


class HTTPError(HTTPResponse):
    """ Used to generate an error page """
    def __init__(self, code=500, message='Unknown Error', exception=None, header=None):
        super(HTTPError, self).__init__(message, code, header)
        self.exception = exception

    def __str__(self):
        return ERROR_PAGE_TEMPLATE % {
            'status' : self.status,
            'url' : str(request.path),
            'error_name' : HTTP_CODES.get(self.status, 'Unknown').title(),
            'error_message' : str(self.output)
        }






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

    def __init__(self, route, target, name=None, static=False):
        """ Create a Route. The route string may contain `:key`,
            `:key#regexp#` or `:#regexp#` tokens for each dynamic part of the
            route. These can be escaped with a backslash infront of the `:`
            and are compleately ignored if static is true. A name may be used
            to refer to this route later (depends on Router)
        """
        self.route = route
        self.target = target
        self.name = name
        self._static = static
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
        return re.sub(r'\(\?P<[^>]*>|\((?!\?)', '(?:', self.group_re())

    def format_str(self):
        ''' Return a format string with named fields. '''
        if self.static:
            return self.route.replace('%','%%')
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
        if not self._static:
            for token, value in self.tokens():
                if token != 'TXT':
                    return True
        self._static = True
        return False

    def __repr__(self):
        return self.route

    def __eq__(self, other):
        return self.route == other.route\
           and self.static == other.static\
           and self.name == other.name\
           and self.target == other.target


class Router(object):
    ''' A route associates a string (e.g. URL) with an object (e.g. function)
        Some dynamic routes may extract parts of the string and provide them as
        a dictionary. This router matches a string against multiple routes and
        returns the associated object along with the extracted data.
    '''

    def __init__(self):
        self.routes = []     # List of all installed routes
        self.static = dict() # Cache for static routes
        self.dynamic = []    # Cache structure for dynamic routes
        self.named = dict()  # Cache for named routes and their format strings

    def add(self, *a, **ka):
        """ Adds a route->target pair or a Route object to the Router.
            See Route() for details.
        """
        route = a[0] if a and isinstance(a[0], Route) else Route(*a, **ka)
        self.routes.append(route)
        if route.name:
            self.named[route.name] = route.format_str()
        if route.static:
            self.static[route.route] = route.target
            return
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

    def match(self, uri):
        ''' Matches an URL and returns a (handler, target) tuple '''
        if uri in self.static:
            return self.static[uri], {}
        for combined, subroutes in self.dynamic:
            match = combined.match(uri)
            if not match: continue
            target, groups = subroutes[match.lastindex - 1]
            groups = groups.match(uri).groupdict() if groups else {}
            return target, groups
        return None, {}

    def build(self, route_name, **args):
        ''' Builds an URL out of a named route and some parameters.'''
        try:
            return self.named[route_name] % args
        except KeyError:
            raise RouteBuildError("No route found with name '%s'." % route_name)

    def __eq__(self, other):
        return self.routes == other.routes






# WSGI abstraction: Request and response management

class Bottle(object):
    """ WSGI application """

    def __init__(self, catchall=True, autojson=True, path = ''):
        """ Create a new bottle instance.
            You usually don't have to do that. Use `bottle.app.push()` instead
        """
        self.routes = Router()
        self.default_route = None
        self.error_handler = {}
        self.jsondump = json_dumps if autojson and json_dumps else False
        self.catchall = catchall
        self.config = dict()
        self.serve = True

    def match_url(self, path, method='GET'):
        """ Find a callback bound to a path and a specific HTTP method.
            Return (callback, param) tuple or (None, {}).
            method: HEAD falls back to GET. HEAD and GET fall back to ALL.
        """
        path = path.strip().lstrip('/')
        handler, param = self.routes.match(method + ';' + path)
        if handler: return handler, param
        if method == 'HEAD':
            handler, param = self.routes.match('GET;' + path)
            if handler: return handler, param
        handler, param = self.routes.match('ANY;' + path)
        if handler: return handler, param
        return self.default_route, {}

    def get_url(self, routename, **kargs):
        """ Return a string that matches a named route """
        return '/' + self.routes.build(routename, **kargs).split(';', 1)[1]

    def route(self, path=None, method='GET', **kargs):
        """ Decorator: Bind a function to a GET request path.

            If the path parameter is None, the signature (name, args) of the
            decorated function is used to generate the path. See yieldroutes()
            for details.

            The method parameter (default: GET) specifies the HTTP request
            method to listen to. 
        """
        method = method.upper()
        def wrapper(handler):
            paths = [] if path is None else [path.strip().lstrip('/')]
            if not paths: # Lets generate the path automatically 
                paths = yieldroutes(handler)
            for p in paths:
                self.routes.add(method+';'+p, handler, **kargs)
            return handler
        return wrapper

    def default(self):
        """ Decorator: Add a default handler for undefined routes """
        def wrapper(handler):
            self.default_route = handler
            return handler
        return wrapper

    def error(self, code=500):
        """ Decorator: Registrer an output handler for a HTTP error code"""
        def wrapper(handler):
            self.error_handler[int(code)] = handler
            return handler
        return wrapper

    def handle(self, url, method, catchall=True):
        """ Handle a single request. Return handler output, HTTPResponse or
        HTTPError. If catchall is true, all exceptions thrown within a
        handler function are catched and returned as HTTPError(500).
        """
        if not self.serve:
            return HTTPError(503, "Server stopped")

        handler, args = self.match_url(request.path, request.method)
        if not handler:
            return HTTPError(404, "Not found")

        try:
            return handler(**args)
        except HTTPResponse, e:
            return e
        except (KeyboardInterrupt, SystemExit, MemoryError):
            raise
        except Exception, e:
            if not self.catchall:
                raise
            err = "Unhandled Exception: %s\n" % (repr(e))
            if DEBUG:
                err += '\n\nTraceback:\n' + format_exc(10)
            request.environ['wsgi.errors'].write(err)
            return HTTPError(500, err, e)

    def _cast(self, out):
        """ Try to cast the input into something WSGI compatible. Correct
        HTTP header and status codes when possible. Clear output on HEAD
        requests.
        Support: False, str, unicode, list(unicode), file, dict, list(dict),
        HTTPResponse and HTTPError
        """
        if isinstance(out, HTTPResponse):
            out.apply(response)
            if isinstance(out, HTTPError):
                out = self.error_handler.get(out.status, str)(out)
            else:
                out = out.output
        if not out:
            response.header['Content-Length'] = '0'
            return []
        if isinstance(out, types.StringType):
            out = [out]
        elif isinstance(out, unicode):
            out = [out.encode(response.charset)]
        elif isinstance(out, list) and isinstance(out[0], unicode):
            out = map(lambda x: x.encode(response.charset), out)
        elif hasattr(out, 'read'):
            out = request.environ.get('wsgi.file_wrapper',
                  lambda x: iter(lambda: x.read(8192), ''))(out)
        elif self.jsondump and isinstance(out, dict)\
          or self.jsondump and isinstance(out, list) and isinstance(out[0], dict):
                out = [self.jsondump(out)]
                response.content_type = 'application/json'
        if isinstance(out, list) and len(out) == 1:
            response.header['Content-Length'] = str(len(out[0]))
        if response.status in (100, 101, 204, 304) or request.method == 'HEAD':
            out = [] # rfc2616 section 4.3
        if not hasattr(out, '__iter__'):
            raise TypeError('Request handler for route "%s" returned [%s] '
                'which is not iterable.' % (request.path, type(out).__name__))
        return out

    def __call__(self, environ, start_response):
        """ The bottle WSGI-interface. """
        try:
            request.bind(environ, self)
            response.bind(self)
            out = self.handle(request.path, request.method)
            out = self._cast(out)
            status = '%d %s' % (response.status, HTTP_CODES[response.status])
            start_response(status, response.wsgiheader())
            return out
        except (KeyboardInterrupt, SystemExit, MemoryError):
            raise
        except Exception, e:
            if not self.catchall:
                raise
            err = '<h1>Critial error while processing request: %s</h1>' \
                  % environ.get('PATH_INFO', '/')
            if DEBUG:
                err += '<h2>Error:</h2>\n<pre>%s</pre>\n' % repr(e)
                err += '<h2>Traceback:</h2>\n<pre>%s</pre>\n' % format_exc(10)
            environ['wsgi.errors'].write(err) #TODO: wsgi.error should not get html
            start_response('500 INTERNAL SERVER ERROR', [])
            return [err]


class Request(threading.local, DictMixin):
    """ Represents a single HTTP request using thread-local attributes.
        The Resquest object wrapps a WSGI environment and can be used as such.
    """
    def __init__(self, environ=None, app=None):
        """ Create a new Request instance.
        
            You usually don't do this but use the global `bottle.request`
            instance instead.
         """
        self.bind(environ or {}, app)

    def bind(self, environ, app=None):
        """ Bind a new WSGI enviroment and clear out all previously computed
            attributes.
            
            This is done automatically for the global `bottle.request`
            instance on every request.
        """
        if isinstance(environ, Request): # Recycle already parsed content
            for key in self.__dict__: #TODO: Test this
                setattr(self, key, getattr(environ, key))
            self.app = app
            return
        self._GET = self._POST = self._GETPOST = self._COOKIES = None
        self._body = self._header = None
        self.environ = environ
        self.app = app
        # These attributes are used anyway, so it is ok to compute them here
        self.path = environ.get('PATH_INFO', '/')
        if not self.path.startswith('/'):
            self.path = '/' + self.path
        self.method = environ.get('REQUEST_METHOD', 'GET').upper()

    def __getitem__(self, key):
        """ Shortcut for Request.environ.__getitem__ """
        return self.environ[key]

    def __setitem__(self, key, value):
        """ Shortcut for Request.environ.__setitem__ """
        self.environ[key] = value

    def keys(self):
        """ Shortcut for Request.environ.keys() """
        return self.environ.keys()

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
        host   = self.environ.get('HTTP_HOST', None)
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
        if self._header is None:
            self._header = HeaderDict()
            for key, value in self.environ.iteritems():
                if key.startswith('HTTP_'):
                    key = key[5:].replace('_','-').title()
                    self._header[key] = value
        return self._header

    @property
    def GET(self):
        """ The QUERY_STRING parsed into a MultiDict.

            Keys and values are strings. Multiple values per key are possible.
            See MultiDict for details.
        """
        if self._GET is None:
            data = parse_qs(self.query_string, keep_blank_values=True)
            self._GET = MultiDict()
            for key, values in data.iteritems():
                for value in values:
                    self._GET[key] = value
        return self._GET

    @property
    def POST(self):
        """ The HTTP POST body parsed into a MultiDict.

            This supports urlencoded and multipart POST requests. Multipart
            is commonly used for file uploads and may result in some of the
            values beeing cgi.FieldStorage objects instead of strings.

            Multiple values per key are possible. See MultiDict for details.
        """
        if self._POST is None:
            save_env = dict() # Build a save environment for cgi
            for key in ('REQUEST_METHOD', 'CONTENT_TYPE', 'CONTENT_LENGTH'):
                if key in self.environ:
                    save_env[key] = self.environ[key]
            save_env['QUERY_STRING'] = '' # Without this, sys.argv is called!
            if TextIOWrapper:
                fb = TextIOWrapper(self.body, encoding='ISO-8859-1')
            else:
                fb = self.body
            data = cgi.FieldStorage(fp=fb, environ=save_env)
            self._POST = MultiDict()
            for item in data.list:
                self._POST[item.name] = item if item.filename else item.value
        return self._POST

    @property
    def params(self):
        """ A combined MultiDict with POST and GET parameters. """
        if self._GETPOST is None:
            self._GETPOST = MultiDict(self.GET)
            self._GETPOST.update(dict(self.POST))
        return self._GETPOST

    @property
    def body(self):
        """ The HTTP request body as a seekable buffer object.
        
            This property returns a copy of the `wsgi.input` stream and should
            be used instead of `environ['wsgi.input']`.
         """
        if self._body is None:
            maxread = max(0, self.content_length)
            stream = self.environ['wsgi.input']
            self._body = BytesIO() if maxread < MEMFILE_MAX else TemporaryFile(mode='w+b')
            while maxread > 0:
                part = stream.read(min(maxread, MEMFILE_MAX))
                if not part: #TODO: Wrong content_length. Error? Do nothing?
                    break
                self._body.write(part)
                maxread -= len(part)
            self.environ['wsgi.input'] = self._body
        self._body.seek(0)
        return self._body

    @property
    def auth(self): #TODO: Tests and docs. Add support for digest. namedtuple?
        """ HTTP authorisation data as a (user, passwd) tuple. (experimental)
        
            This implementation currently only supports basic auth and returns
            None on errors.
        """
        return parse_auth(self.environ.get('HTTP_AUTHORIZATION'))

    @property
    def COOKIES(self):
        """ Cookie information parsed into a dictionary.
        
            Secure cookies are NOT decoded automatically. See
            Request.get_cookie() for details.
        """
        if self._COOKIES is None:
            raw_dict = SimpleCookie(self.environ.get('HTTP_COOKIE',''))
            self._COOKIES = {}
            for cookie in raw_dict.itervalues():
                self._COOKIES[cookie.key] = cookie.value
        return self._COOKIES

    def get_cookie(self, *args):
        """ Return the (decoded) value of a cookie. """
        value = self.COOKIES.get(*args)
        sec = self.app.config['securecookie.key']
        dec = cookie_decode(value, sec)
        return dec or value


class Response(threading.local):
    """ Represents a single HTTP response using thread-local attributes.
    """

    def bind(self, app):
        """ Resets the Response object to its factory defaults. """
        self._COOKIES = None
        self.status = 200
        self.header = HeaderDict()
        self.content_type = 'text/html; charset=UTF-8'
        self.error = None
        self.app = app

    def wsgiheader(self):
        ''' Returns a wsgi conform list of header/value pairs. '''
        for c in self.COOKIES.values():
            if c.OutputString() not in self.header.getall('Set-Cookie'):
                self.header.append('Set-Cookie', c.OutputString())
        return list(self.header.iterallitems())

    @property
    def charset(self):
        """ Return the charset specified tin the content-type header.
        
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

    def set_cookie(self, key, value, **kargs):
        """ Add a new cookie with various options.
        
        If the cookie value is not a string, a secure cookie is created.
        
        Possible options are:
            expires, path, comment, domain, max_age, secure, version, httponly
            See http://de.wikipedia.org/wiki/HTTP-Cookie#Aufbau for details
        """
        if not isinstance(value, basestring):
            sec = self.app.config['securecookie.key']
            value = cookie_encode(value, sec).decode('ascii') #2to3 hack
        self.COOKIES[key] = value
        for k, v in kargs.iteritems():
            self.COOKIES[key][k.replace('_', '-')] = v

    def get_content_type(self):
        """ Current 'Content-Type' header. """
        return self.header['Content-Type']

    def set_content_type(self, value):
        self.header['Content-Type'] = value

    content_type = property(get_content_type, set_content_type, None,
                            get_content_type.__doc__)






# Data Structures

class BaseController(object):
    _singleton = None
    def __new__(cls, *a, **k):
        if not cls._singleton:
            cls._singleton = object.__new__(cls, *a, **k)
        return cls._singleton


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
    def __contains__(self, key): return MultiDict.__contains__(self, key.title())
    def __getitem__(self, key): return MultiDict.__getitem__(self, key.title())
    def __delitem__(self, key): return MultiDict.__delitem__(self, key.title())
    def __setitem__(self, key, value): self.replace(key, value)
    def append(self, key, value): return MultiDict.append(self, key.title(), str(value))
    def replace(self, key, value): return MultiDict.replace(self, key.title(), str(value))
    def getall(self, key): return MultiDict.getall(self, key.title())

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




# Module level functions

# BC: 0.6.4 and needed for run()
app = default_app = AppStack([Bottle()])


def abort(code=500, text='Unknown Error: Appliction stopped.'):
    """ Aborts execution and causes a HTTP error. """
    raise HTTPError(code, text)


def redirect(url, code=303):
    """ Aborts execution and causes a 303 redirect """
    scriptname = request.environ.get('SCRIPT_NAME', '').rstrip('/') + '/'
    location = urljoin(request.url, urljoin(scriptname, url))
    raise HTTPResponse("", status=code, header=dict(Location=location))


def send_file(*a, **k): #BC 0.6.4
    """ Raises the output of static_file() """
    raise static_file(*a, **k)


def static_file(filename, root, guessmime=True, mimetype=None, download=False):
    """ Opens a file in a save way and returns a HTTPError object with status
        code 200, 305, 401 or 404. Sets Content-Type, Content-Length and
        Last-Modified header. Obeys If-Modified-Since header and HEAD requests.
    """
    root = os.path.abspath(root) + os.sep
    filename = os.path.abspath(os.path.join(root, filename.strip('/\\')))
    header = dict()

    if not filename.startswith(root):
        return HTTPError(401, "Access denied.")
    if not os.path.exists(filename) or not os.path.isfile(filename):
        return HTTPError(404, "File does not exist.")
    if not os.access(filename, os.R_OK):
        return HTTPError(401, "You do not have permission to access this file.")

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
        if ims is not None and ims >= stats.st_mtime:
           return HTTPResponse("Not modified", status=304, header=header)
    header['Content-Length'] = stats.st_size
    if request.method == 'HEAD':
        return HTTPResponse('', header=header)
    else:
        return HTTPResponse(open(filename, 'rb'), header=header)






# Utilities

def url(routename, **kargs):
    """ Return a named route filled with arguments """
    return app().get_url(routename, **kargs)


def parse_date(ims):
    """ Parses rfc1123, rfc850 and asctime timestamps and returns UTC epoch. """
    try:
        ts = email.utils.parsedate_tz(ims)
        return time.mktime(ts[:8] + (0,)) - (ts[9] or 0) - time.timezone
    except (TypeError, ValueError, IndexError):
        return None


def parse_auth(header):
    try:
        method, data = header.split(None, 1)
        if method.lower() == 'basic':
            name, pwd = base64.b64decode(data).split(':', 1)
            return name, pwd
    except (KeyError, ValueError, TypeError), a:
        return None


def cookie_encode(data, key):
    ''' Encode and sign a pickle-able object. Return a string '''
    msg = base64.b64encode(pickle.dumps(data, -1))
    sig = base64.b64encode(hmac.new(key, msg).digest())
    return u'!'.encode('ascii') + sig + u'?'.encode('ascii') + msg #2to3 hack


def cookie_decode(data, key):
    ''' Verify and decode an encoded string. Return an object or None'''
    if isinstance(data, unicode): data = data.encode('ascii') #2to3 hack
    if cookie_is_encoded(data):
        sig, msg = data.split(u'?'.encode('ascii'),1) #2to3 hack
        if sig[1:] == base64.b64encode(hmac.new(key, msg).digest()):
           return pickle.loads(base64.b64decode(msg))
    return None


def cookie_is_encoded(data):
    ''' Verify and decode an encoded string. Return an object or None'''
    return bool(data.startswith(u'!'.encode('ascii')) and u'?'.encode('ascii') in data) #2to3 hack


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
                except ValueError, e:
                    abort(403, 'Wrong parameter format for: %s' % key)
            return func(**kargs)
        return wrapper
    return decorator


def route(*a, **ka):
    """ Decorator: Bind a route to a callback.
        The method parameter (default: GET) specifies the HTTP request
        method to listen to """
    return app().route(*a, **ka)

get = functools.partial(route, method='GET')
get.__doc__ = route.__doc__

post = functools.partial(route, method='POST')
post.__doc__ = route.__doc__.replace('GET','POST')

put = functools.partial(route, method='PUT')
put.__doc__ = route.__doc__.replace('GET','PUT')

delete = functools.partial(route, method='DELETE')
delete.__doc__ = route.__doc__.replace('GET','DELETE')

def default():
    """
    Decorator for request handler. Same as app().default(handler).
    """
    return app().default()


def error(code=500):
    """
    Decorator for error handler. Same as app().error(code, handler).
    """
    return app().error(code)






# Server adapter

class ServerAdapter(object):
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
    def run(self, handler): # pragma: no cover
        from wsgiref.handlers import CGIHandler
        CGIHandler().run(handler) # Just ignore host and port here


class FlupFCGIServer(ServerAdapter):
    def run(self, handler): # pragma: no cover
       import flup.server.fcgi
       flup.server.fcgi.WSGIServer(handler, bindAddress=(self.host, self.port)).run()


class WSGIRefServer(ServerAdapter):
    def run(self, handler): # pragma: no cover
        from wsgiref.simple_server import make_server
        srv = make_server(self.host, self.port, handler)
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
    def run(self, handler):
        from google.appengine.ext.webapp import util
        util.run_wsgi_app(handler)


class TwistedServer(ServerAdapter):
    """ Untested. """
    def run(self, handler):
        import twisted.web.wsgi
        import twisted.internet
        resource = twisted.web.wsgi.WSGIResource(twisted.internet.reactor,
                   twisted.internet.reactor.getThreadPool(), handler)
        site = server.Site(resource)
        twisted.internet.reactor.listenTCP(self.port, self.host)
        twisted.internet.reactor.run()


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


class AutoServer(ServerAdapter):
    """ Untested. """
    adapters = [FapwsServer, CherryPyServer, PasteServer,
                TwistedServer, GunicornServer, WSGIRefServer]
    def run(self, handler):
        for sa in self.adapters:
            try:
                return sa(self.host, self.port, **self.options).run()
            except ImportError:
                pass


def run(app=None, server=AutoServer, host='127.0.0.1', port=8080,
        interval=1, reloader=False, **kargs):
    """ Runs bottle as a web server. """
    app = app if app else default_app()
    quiet = bool(kargs.get('quiet', False))
    # Instantiate server, if it is a class instead of an instance
    if isinstance(server, type):
        server = server(host=host, port=port, **kargs)
    if not isinstance(server, ServerAdapter):
        raise RuntimeError("Server must be a subclass of WSGIAdapter")
    if not quiet and isinstance(server, ServerAdapter): # pragma: no cover
        if not reloader or os.environ.get('BOTTLE_CHILD') == 'true':
            print "Bottle server starting up (using %s)..." % repr(server)
            print "Listening on http://%s:%d/" % (server.host, server.port)
            print "Use Ctrl-C to quit."
            print
        else:
            print "Bottle auto reloader starting up..."
    try:
        if reloader and interval:
            reloader_run(server, app, interval)
        else:
            server.run(app)
    except KeyboardInterrupt:
        if not quiet: # pragma: no cover
            print "Shutting Down..."


#TODO: If the parent process is killed (with SIGTERM) the childs survive...
def reloader_run(server, app, interval):
    if os.environ.get('BOTTLE_CHILD') == 'true':
        # We are a child process
        files = dict()
        for module in sys.modules.values():
            file_path = getattr(module, '__file__', None)
            if file_path and os.path.isfile(file_path):
                file_split = os.path.splitext(file_path)
                if file_split[1] in ('.py', '.pyc', '.pyo'):
                    file_path = file_split[0] + '.py'
                    files[file_path] = os.stat(file_path).st_mtime
        thread.start_new_thread(server.run, (app,))
        while True:
            time.sleep(interval)
            for file_path, file_mtime in files.iteritems():
                if not os.path.exists(file_path):
                    print "File changed: %s (deleted)" % file_path
                elif os.stat(file_path).st_mtime > file_mtime:
                    print "File changed: %s (modified)" % file_path
                else: continue
                print "Restarting..."
                app.serve = False
                time.sleep(interval) # be nice and wait for running requests
                sys.exit(3)
    while True:
        args = [sys.executable] + sys.argv
        environ = os.environ.copy()
        environ['BOTTLE_CHILD'] = 'true'
        exit_status = subprocess.call(args, env=environ)
        if exit_status != 3:
            sys.exit(exit_status)






# Templates

class TemplateError(HTTPError):
    def __init__(self, message):
        HTTPError.__init__(self, 500, message)


class BaseTemplate(object):
    """ Base class and minimal API for template adapters """
    extentions = ['tpl','html','thtml','stpl']

    def __init__(self, source=None, name=None, lookup=[], encoding='utf8'):
        """ Create a new template.
        If the source parameter (str or buffer) is missing, the name argument
        is used to guess a template filename. Subclasses can assume that
        either self.source or self.filename is set. Both are strings.
        The lookup-argument works similar to sys.path for templates.
        The encoding parameter is used to decode byte strings or files.
        """
        self.name = name
        self.source = source.read() if hasattr(source, 'read') else source
        self.filename = None
        self.lookup = map(os.path.abspath, lookup)
        self.encoding = encoding
        if not self.source and self.name:
            self.filename = self.search(self.name, self.lookup)
            if not self.filename:
                raise TemplateError('Template %s not found.' % repr(name))
        if not self.source and not self.filename:
            raise TemplateError('No template specified.')
        self.prepare()

    @classmethod
    def search(cls, name, lookup=[]):
        """ Search name in all directiries specified in lookup.
        First without, then with common extentions. Return first hit. """
        if os.path.isfile(name): return name
        for spath in lookup:
            fname = os.path.join(spath, name)
            if os.path.isfile(fname):
                return fname
            for ext in cls.extentions:
                if os.path.isfile('%s.%s' % (fname, ext)):
                    return '%s.%s' % (fname, ext)

    def prepare(self):
        """ Run preparatios (parsing, caching, ...).
        It should be possible to call this again to refresh a template.
        """
        raise NotImplementedError

    def render(self, **args):
        """ Render the template with the specified local variables and return
        a single byte or unicode string. If it is a byte string, the encoding
        must match self.encoding. This method must be thread save!
        """
        raise NotImplementedError


class MakoTemplate(BaseTemplate):
    default_filters=None
    global_variables={}

    def prepare(self):
        from mako.template import Template
        from mako.lookup import TemplateLookup
        #TODO: This is a hack... http://github.com/defnull/bottle/issues#issue/8
        options = dict(input_encoding=self.encoding, default_filters=MakoTemplate.default_filters)
        mylookup = TemplateLookup(directories=['.']+self.lookup, **options)
        if self.source:
            self.tpl = Template(self.source, lookup=mylookup)
        else: #mako cannot guess extentions. We can, but only at top level...
            name = self.name
            if not os.path.splitext(name)[1]:
                name += os.path.splitext(self.filename)[1]
            self.tpl = mylookup.get_template(name)

    def render(self, **args):
        _defaults = MakoTemplate.global_variables.copy()
        _defaults.update(args)
        return self.tpl.render(**_defaults)


class CheetahTemplate(BaseTemplate):
    def prepare(self):
        from Cheetah.Template import Template
        self.context = threading.local()
        self.context.vars = {}
        if self.source:
            self.tpl = Template(source=self.source, searchList=[self.context.vars])
        else:
            self.tpl = Template(file=self.filename, searchList=[self.context.vars])

    def render(self, **args):
        self.context.vars.update(args)
        out = str(self.tpl)
        self.context.vars.clear()
        return [out]


class Jinja2Template(BaseTemplate):
    env = None # hopefully, a Jinja environment is actually thread-safe

    def prepare(self):
        if not self.env:
            from jinja2 import Environment, FunctionLoader
            self.env = Environment(line_statement_prefix="#", loader=FunctionLoader(self.loader))
        if self.source:
            self.tpl = self.env.from_string(self.source)
        else:
            self.tpl = self.env.get_template(self.filename)

    def render(self, **args):
        return self.tpl.render(**args).encode("utf-8")

    def loader(self, name):
        fname = self.search(name, self.lookup)
        if fname:
            with open(fname) as f:
                return f.read().decode(self.encoding)


class SimpleTemplate(BaseTemplate):
    re_python = re.compile(r'^\s*%\s*(?:(if|elif|else|try|except|finally|for|'
                            'while|with|def|class)|(include|rebase)|(end)|(.*))')
    re_inline = re.compile(r'\{\{(.*?)\}\}')
    dedent_keywords = ('elif', 'else', 'except', 'finally')

    def prepare(self):
        if self.source:
            code = self.translate(self.source)
            self.co = compile(code, '<string>', 'exec')
        else:
            code = self.translate(open(self.filename).read())
            self.co = compile(code, self.filename, 'exec')

    def translate(self, template):
        indent = 0
        strbuffer = []
        code = []
        self.includes = dict()
        class PyStmt(str):
            def __repr__(self): return 'str(' + self + ')'
        def flush(allow_nobreak=False):
            if len(strbuffer):
                if allow_nobreak and strbuffer[-1].endswith("\\\\\n"):
                    strbuffer[-1]=strbuffer[-1][:-3]
                code.append(' ' * indent + "_stdout.append(%s)" % repr(''.join(strbuffer)))
                code.append((' ' * indent + '\n') * len(strbuffer)) # to preserve line numbers
                del strbuffer[:]
        def cadd(line): code.append(" " * indent + line.strip() + '\n')
        for line in template.splitlines(True):
            m = self.re_python.match(line)
            if m:
                flush(allow_nobreak=True)
                keyword, subtpl, end, statement = m.groups()
                if keyword:
                    if keyword in self.dedent_keywords:
                        indent -= 1
                    cadd(line[m.start(1):])
                    indent += 1
                elif subtpl:
                    tmp = line[m.end(2):].strip().split(None, 1)
                    if not tmp:
                      cadd("_stdout.extend(_base)")
                    else:
                      name = tmp[0]
                      args = tmp[1:] and tmp[1] or ''
                      if name not in self.includes:
                        self.includes[name] = SimpleTemplate(name=name, lookup=self.lookup)
                      if subtpl == 'include':
                        cadd("_ = _includes[%s].execute(_stdout, %s)"
                             % (repr(name), args))
                      else:
                        cadd("_tpl['_rebase'] = (_includes[%s], dict(%s))"
                             % (repr(name), args))
                elif end:
                    indent -= 1
                    cadd('#' + line[m.start(3):])
                elif statement:
                    cadd(line[m.start(4):])
            else:
                splits = self.re_inline.split(line) # text, (expr, text)*
                if len(splits) == 1:
                    strbuffer.append(line)
                else:
                    flush()
                    for i in range(1, len(splits), 2):
                        splits[i] = PyStmt(splits[i])
                    splits = [x for x in splits if bool(x)]
                    cadd("_stdout.extend(%s)" % repr(splits))
        flush()
        return ''.join(code)

    def execute(self, stdout, **args):
        args['_stdout'] = stdout
        args['_includes'] = self.includes
        args['_tpl'] = args
        eval(self.co, args)
        if '_rebase' in args:
            subtpl, args = args['_rebase']
            args['_base'] = stdout[:] #copy stdout
            del stdout[:] # clear stdout
            return subtpl.execute(stdout, **args)
        return args

    def render(self, **args):
        """ Render the template using keyword arguments as local variables. """
        stdout = []
        self.execute(stdout, **args)
        return stdout


def template(tpl, template_adapter=SimpleTemplate, **args):
    '''
    Get a rendered template as a string iterator.
    You can use a name, a filename or a template string as first parameter.
    '''
    lookup = args.get('template_lookup', TEMPLATE_PATH)
    if tpl not in TEMPLATES or DEBUG:
        if "\n" in tpl or "{" in tpl or "%" in tpl or '$' in tpl:
            TEMPLATES[tpl] = template_adapter(source=tpl, lookup=lookup)
        else:
            TEMPLATES[tpl] = template_adapter(name=tpl, lookup=lookup)
    if not TEMPLATES[tpl]:
        abort(500, 'Template (%s) not found' % tpl)
    args['abort'] = abort
    args['request'] = request
    args['response'] = response
    return TEMPLATES[tpl].render(**args)

mako_template = functools.partial(template, template_adapter=MakoTemplate)
cheetah_template = functools.partial(template, template_adapter=CheetahTemplate)
jinja2_template = functools.partial(template, template_adapter=Jinja2Template)

def view(tpl_name, **defaults):
    ''' Decorator: Rendes a template for a handler.
        Return a dict of template vars to fill out the template.
    '''
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kargs):
            tplvars = dict(defaults)
            tplvars.update(func(*args, **kargs))
            return template(tpl_name, **tplvars)
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


ERROR_PAGE_TEMPLATE = """<!DOCTYPE HTML PUBLIC "-//IETF//DTD HTML 2.0//EN">
<html>
    <head>
        <title>Error %(status)d: %(error_name)s</title>
    </head>
    <body>
        <h1>Error %(status)d: %(error_name)s</h1>
        <p>Sorry, the requested URL <tt>%(url)s</tt> caused an error:</p>
        <pre>
            %(error_message)s
        </pre>
    </body>
</html>
"""
""" The HTML template used for error messages """

request = Request()
""" Whenever a page is requested, the :class:`Bottle` WSGI handler stores
metadata about the current request into this instance of :class:`Request`.
It is thread-save and can be accessed from within handler functions. """

response = Response()
""" The :class:`Bottle` WSGI handler uses metasata assigned to this instance
of :class:`Response` to generate the WSGI response. """

local = threading.local()

#TODO: Global and app local configuration (debug, defaults, ...) is a mess

def debug(mode=True):
    """ Change the debug level.
    There is only one debug level supported at the moment."""
    global DEBUG
    DEBUG = bool(mode)
