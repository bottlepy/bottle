# -*- coding: utf-8 -*-
"""
Bottle is a fast and simple mirco-framework for small web-applications. It
offers request dispatching (Routes) with url parameter support, Templates,
key/value Databases, a build-in HTTP Server? and adapters for many third party
WSGI/HTTP-server and template engines. All in a single file and with no
dependencies other than the Python Standard Library.

Homepage and documentation: http://wiki.github.com/defnull/bottle

Special thanks to Stefan Matthias Aust [http://github.com/sma]
  for his contribution to SimpelTemplate

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

__author__ = 'Marcel Hellkamp'
__version__ = '0.5.1'
__license__ = 'MIT'

import sys
import cgi
import mimetypes
import os
import os.path
import traceback
import re
import random
import threading
import time
from wsgiref.headers import Headers as HeaderWrapper

if (2,6) <= sys.version_info < (3,0):
    from Cookie import SimpleCookie
    from urlparse import parse_qs
    import cPickle as pickle
    import anydbm as dbm
elif (3,0) <= sys.version_info:
    from http.cookies import SimpleCookie
    from urllib.parse import parse_qs
    import pickle
    import dbm
else:
    raise NotImplementedError("Sorry, you need at least Python 2.6 or Python 3.x to use bottle.")






# Exceptions and Events

class BottleException(Exception):
    """ A base class for exceptions used by bottle."""
    pass


class HTTPError(BottleException):
    """ A way to break the execution and instantly jump to an error handler. """
    def __init__(self, status, text):
        self.output = text
        self.http_status = int(status)

    def __str__(self):
        return self.output


class BreakTheBottle(BottleException):
    """ Not an exception, but a straight jump out of the controller code.
    
    Causes the Bottle to instantly call start_response() and return the
    content of output """
    def __init__(self, output):
        self.output = output
        
        




# WSGI abstraction: Request and response management


_default_app = None
def default_app():
    global _default_app
    if not _default_app:
        _default_app = Bottle()
    return _default_app



class Bottle(object):

    def __init__(self):
        self.simple_routes = {}
        self.regexp_routes = {}
        self.error_handler = {}
        self.optimize = False
        self.debug = False

    def match_url(self, url, method='GET'):
        """Returns the first matching handler and a parameter dict or (None, None) """
        url = url.strip().lstrip("/ ")
        # Search for static routes first
        route = self.simple_routes.get(method,{}).get(url,None)
        if route:
            return (route, {})
        
        # Now search regexp routes
        routes = self.regexp_routes.get(method,[])
        for i in range(len(routes)):
            match = routes[i][0].match(url)
            if match:
                handler = routes[i][1]
                if i > 0 and self.optimize and random.random() <= 0.001:
                    routes[i-1], routes[i] = routes[i], routes[i-1]
                return (handler, match.groupdict())
        return (None, None)

    def add_route(self, route, handler, method='GET', simple=False):
        """ Adds a new route to the route mappings. """
        method = method.strip().upper()
        route = route.strip().lstrip('$^/ ').rstrip('$^ ')
        if re.match(r'^(\w+/)*\w*$', route) or simple:
            self.simple_routes.setdefault(method, {})[route] = handler
        else:
            route = re.sub(r':([a-zA-Z_]+)(?P<uniq>[^\w/])(?P<re>.+?)(?P=uniq)',r'(?P<\1>\g<re>)',route)
            route = re.sub(r':([a-zA-Z_]+)',r'(?P<\1>[^/]+)', route)
            route = re.compile('^%s$' % route)
            self.regexp_routes.setdefault(method, []).append([route, handler])

    def route(self, url, **kargs):
        """ Decorator for request handler. Same as add_route(url, handler, **kargs)."""
        def wrapper(handler):
            self.add_route(url, handler, **kargs)
            return handler
        return wrapper

    def set_error_handler(self, code, handler):
        """ Adds a new error handler. """
        code = int(code)
        self.error_handler[code] = handler

    def error(self, code=500):
        """ Decorator for error handler. Same as set_error_handler(code, handler)."""
        def wrapper(handler):
            self.set_error_handler(code, handler)
            return handler
        return wrapper
        
    def handle_error(self, exception):
        response.status = getattr(exception, 'http_status', 500)
        try:
            output = self.error_handler.get(response.status, error_default)(exception)
        except:
            output = "Exception within error handler!"
        if response.status == 500:
            request._environ['wsgi.errors'].write("Error (500) on '%s': %s\n" % (request.path, exception))
        return output

    def __call__(self, environ, start_response):
        """ The bottle WSGI-interface ."""
        request.bind(environ)
        response.bind()
        try:
            handler, args = self.match_url(request.path, request.method)
            if not handler:
                raise HTTPError(404, "Not found")
            output = handler(**args)
        except BreakTheBottle as e:
            output = e.output
        except Exception as e:
            output = self.handle_error(e)

        db.close()
        status = '%d %s' % (response.status, HTTP_CODES[response.status])
        start_response(status, response.wsgiheaders())

        if hasattr(output, 'read'):
            if 'wsgi.file_wrapper' in environ:
                return environ['wsgi.file_wrapper'](output)
            else:
                return iter(lambda: fileoutput.read(8192), '')
        elif isinstance(output, str):
            return [output]
        else:
            return output






class Request(threading.local):
    """ Represents a single request using thread-local namespace. """

    def bind(self, environ):
        """ Binds the enviroment of the current request to this request handler """
        self._environ = environ
        self._GET = None
        self._POST = None
        self._GETPOST = None
        self._COOKIES = None
        self.path = self._environ.get('PATH_INFO', '/').strip()
        if not self.path.startswith('/'):
            self.path = '/' + self.path

    @property
    def method(self):
        ''' Returns the request method (GET,POST,PUT,DELETE,...) '''
        return self._environ.get('REQUEST_METHOD', 'GET').upper()

    @property
    def query_string(self):
        ''' Content of QUERY_STRING '''
        return self._environ.get('QUERY_STRING', '')

    @property
    def input_length(self):
        ''' Content of CONTENT_LENGTH '''
        try:
            return int(self._environ.get('CONTENT_LENGTH', '0'))
        except ValueError:
            return 0

    @property
    def GET(self):
        """Returns a dict with GET parameters."""
        if self._GET is None:
            raw_dict = parse_qs(self.query_string, keep_blank_values=1)
            self._GET = {}
            for key, value in raw_dict.items():
                if len(value) == 1:
                    self._GET[key] = value[0]
                else:
                    self._GET[key] = value
        return self._GET

    @property
    def POST(self):
        """Returns a dict with parsed POST data."""
        if self._POST is None:
            raw_data = cgi.FieldStorage(fp=self._environ['wsgi.input'], environ=self._environ)
            self._POST = {}
            if raw_data:
                for key in raw_data:
                    if isinstance(raw_data[key], list):
                        self._POST[key] = [v.value for v in raw_data[key]]
                    elif raw_data[key].filename:
                        self._POST[key] = raw_data[key]
                    else:
                        self._POST[key] = raw_data[key].value
        return self._POST

    @property
    def params(self):
        ''' Returns a mix of GET and POST data. POST overwrites GET '''
        if self._GETPOST is None:
            self._GETPOST = dict(self.GET)
            self._GETPOST.update(dict(self.POST))
        return self._GETPOST

    @property
    def COOKIES(self):
        """Returns a dict with COOKIES."""
        if self._COOKIES is None:
            raw_dict = SimpleCookie(self._environ.get('HTTP_COOKIE',''))
            self._COOKIES = {}
            for cookie in raw_dict.values():
                self._COOKIES[cookie.key] = cookie.value
        return self._COOKIES


class Response(threading.local):
    """ Represents a single response using thread-local namespace. """

    def bind(self):
        """ Clears old data and creates a brand new Response object """
        self._COOKIES = None
        self.status = 200
        self.header_list = []
        self.header = HeaderWrapper(self.header_list)
        self.content_type = 'text/html'
        self.error = None

    def wsgiheaders(self):
        ''' Returns a wsgi conform list of header/value pairs '''
        for c in self.COOKIES.values():
            self.header.add_header('Set-Cookie', c.OutputString())
        return [(h.title(), v) for h, v in self.header_list]

    @property
    def COOKIES(self):
        if not self._COOKIES:
            self._COOKIES = SimpleCookie()
        return self._COOKIES

    def set_cookie(self, key, value, **kargs):
        """ Sets a Cookie. Optional settings: expires, path, comment, domain, max-age, secure, version, httponly """
        self.COOKIES[key] = value
        for k in kargs:
            self.COOKIES[key][k] = kargs[k]

    def get_content_type(self):
        '''Gives access to the 'Content-Type' header and defaults to 'text/html'.'''
        return self.header['Content-Type']
        
    def set_content_type(self, value):
        self.header['Content-Type'] = value
        
    content_type = property(get_content_type, set_content_type, None, get_content_type.__doc__)


def abort(code=500, text='Unknown Error: Appliction stopped.'):
    """ Aborts execution and causes a HTTP error. """
    raise HTTPError(code, text)


def redirect(url, code=307):
    """ Aborts execution and causes a 307 redirect """
    response.status = code
    response.header['Location'] = url
    raise BreakTheBottle("")


def send_file(filename, root, guessmime = True, mimetype = 'text/plain'):
    """ Aborts execution and sends a static files as response. """
    root = os.path.abspath(root) + '/'
    filename = os.path.normpath(filename).strip('/')
    filename = os.path.join(root, filename)
    
    if not filename.startswith(root):
        abort(401, "Access denied.")
    if not os.path.exists(filename) or not os.path.isfile(filename):
        abort(404, "File does not exist.")
    if not os.access(filename, os.R_OK):
        abort(401, "You do not have permission to access this file.")

    if guessmime:
        guess = mimetypes.guess_type(filename)[0]
        if guess:
            response.content_type = guess
        elif mimetype:
            response.content_type = mimetype
    elif mimetype:
        response.content_type = mimetype

    stats = os.stat(filename)
    # TODO: HTTP_IF_MODIFIED_SINCE -> 304 (Thu, 02 Jul 2009 23:16:31 CEST)
    if 'Content-Length' not in response.header:
        response.header['Content-Length'] = stats.st_size
    if 'Last-Modified' not in response.header:
        ts = time.gmtime(stats.st_mtime)
        ts = time.strftime("%a, %d %b %Y %H:%M:%S +0000", ts)
        response.header['Last-Modified'] = ts

    raise BreakTheBottle(open(filename, 'r'))






# Decorators

def validate(**vkargs):
    ''' Validates and manipulates keyword arguments by user defined callables 
    and handles ValueError and missing arguments by raising HTTPError(403) '''
    def decorator(func):
        def wrapper(**kargs):
            for key in vkargs:
                if key not in kargs:
                    abort(403, 'Missing parameter: %s' % key)
                try:
                    kargs[key] = vkargs[key](kargs[key])
                except ValueError as e:
                    abort(403, 'Wrong parameter format for: %s' % key)
            return func(**kargs)
        return wrapper
    return decorator


def route(url, **kargs):
    """ Decorator for request handler. Same as add_route(url, handler, **kargs)."""
    return default_app().route(url, **kargs)


def error(code=500):
    """ Decorator for error handler. Same as set_error_handler(code, handler)."""
    return default_app().error(code)






# Server adapter

class ServerAdapter(object):
    def __init__(self, host='127.0.0.1', port=8080, **kargs):
        self.host = host
        self.port = int(port)
        self.options = kargs

    def __repr__(self):
        return "%s (%s:%d)" % (self.__class__.__name__, self.host, self.port)

    def run(self, handler):
        pass


class WSGIRefServer(ServerAdapter):
    def run(self, handler):
        from wsgiref.simple_server import make_server
        srv = make_server(self.host, self.port, handler)
        srv.serve_forever()


class CherryPyServer(ServerAdapter):
    def run(self, handler):
        from cherrypy import wsgiserver
        server = wsgiserver.CherryPyWSGIServer((self.host, self.port), handler)
        server.start()


class FlupServer(ServerAdapter):
    def run(self, handler):
       from flup.server.fcgi import WSGIServer
       WSGIServer(handler, bindAddress=(self.host, self.port)).run()


class PasteServer(ServerAdapter):
    def run(self, handler):
        from paste import httpserver
        from paste.translogger import TransLogger
        app = TransLogger(handler)
        httpserver.serve(app, host=self.host, port=str(self.port))


class FapwsServer(ServerAdapter):
    """ Extreamly fast Webserver using libev (see http://william-os4y.livejournal.com/)
        Experimental ... """
    def run(self, handler):
        import fapws._evwsgi as evwsgi
        from fapws import base
        import sys
        evwsgi.start(self.host, self.port)
        evwsgi.set_base_module(base)
        def app(environ, start_response):
            environ['wsgi.multiprocess'] = False
            return handler(environ, start_response)
        evwsgi.wsgi_cb(('',app))
        evwsgi.run()


def run(app=None, server=WSGIRefServer, host='127.0.0.1', port=8080, optinmize = False, **kargs):
    """ Runs bottle as a web server, using Python's built-in wsgiref implementation by default.
    
    You may choose between WSGIRefServer, CherryPyServer, FlupServer and
    PasteServer or write your own server adapter.
    """
    if not app:
        app = default_app()
    
    OPTIMIZER = bool(optinmize)
    quiet = bool('quiet' in kargs and kargs['quiet'])

    # Instanciate server, if it is a class instead of an instance
    if isinstance(server, type) and issubclass(server, ServerAdapter):
        server = server(host=host, port=port, **kargs)

    if not isinstance(server, ServerAdapter):
        raise RuntimeError("Server must be a subclass of ServerAdapter")

    if not quiet:
        print('Bottle server starting up (using %s)...' % repr(server))
        print('Listening on http://%s:%d/' % (server.host, server.port))
        print('Use Ctrl-C to quit.')
        print('')

    try:
        server.run(app)
    except KeyboardInterrupt:
        print("Shuting down...")






# Templates


class BaseTemplate(object):
    def __init__(self, template='', filename='<template>'):
        self.source = filename
        if self.source != '<template>':
            fp = open(filename)
            template = fp.read()
            fp.close()
        self.parse(template)

    def parse(self, template): raise NotImplementedError
    def render(self, **args): raise NotImplementedError
    
    @classmethod
    def find(cls, name):
        for path in TEMPLATE_PATH:
            if os.path.isfile(path % name):
                return cls(filename = path % name)
        return None


class MakoTemplate(BaseTemplate):
    def parse(self, template):
        from mako.template import Template
        self.tpl = Template(template)
 
    def render(self, **args):
        return self.tpl.render(**args)


class SimpleTemplate(BaseTemplate):

    re_python = re.compile(r'^\s*%\s*(?:(if|elif|else|try|except|finally|for|while|with|def|class)|(include)|(end)|(.*))')
    re_inline = re.compile(r'\{\{(.*?)\}\}')
    dedent_keywords = ('elif', 'else', 'except', 'finally')

    def translate(self, template):
        indent = 0
        strbuffer = []
        code = []
        self.subtemplates = {}
        class PyStmt(str):
            def __repr__(self): return 'str(' + self + ')'
        def flush(allow_nobreak=False):
            if len(strbuffer):
                if allow_nobreak and strbuffer[-1].endswith("\\\\\n"):
                    strbuffer[-1]=strbuffer[-1][:-3]
                code.append(" " * indent + "stdout.append(%s)" % repr(''.join(strbuffer)))
                code.append((" " * indent + "\n") * len(strbuffer)) # to preserve line numbers 
                del strbuffer[:]
        for line in template.splitlines(True):
            m = self.re_python.match(line)
            if m:
                flush(allow_nobreak=True)
                keyword, include, end, statement = m.groups()
                if keyword:
                    if keyword in self.dedent_keywords:
                        indent -= 1
                    code.append(" " * indent + line[m.start(1):])
                    indent += 1
                elif include:
                    tmp = line[m.end(2):].strip().split(None, 1)
                    name = tmp[0]
                    args = tmp[1:] and tmp[1] or ''
                    self.subtemplates[name] = SimpleTemplate.find(name)
                    code.append(" " * indent + "stdout.append(_subtemplates[%s].render(%s))\n" % (repr(name), args))
                elif end:
                    indent -= 1
                    code.append(" " * indent + '#' + line[m.start(3):])
                elif statement:
                    code.append(" " * indent + line[m.start(4):])
            else:
                splits = self.re_inline.split(line) # text, (expr, text)*
                if len(splits) == 1:
                    strbuffer.append(line)
                else:
                    flush()
                    for i in range(1, len(splits), 2):
                        splits[i] = PyStmt(splits[i])
                    splits = [x for x in splits if bool(x)]
                    code.append(" " * indent + "stdout.extend(%s)\n" % repr(splits))
        flush()
        return ''.join(code)

    def parse(self, template):
        code = self.translate(template)
        self.co = compile(code, self.source, 'exec')

    def render(self, **args):
        ''' Returns the rendered template using keyword arguments as local variables. '''
        args['stdout'] = []
        args['_subtemplates'] = self.subtemplates
        eval(self.co, args)
        return ''.join(args['stdout'])


def template(template, template_adapter=SimpleTemplate, **args):
    ''' Returns a string from a template '''
    if template not in TEMPLATES:
        if template.find("\n") == -1 and template.find("{") == -1 and template.find("%") == -1:
            TEMPLATES[template] = template_adapter.find(template)
        else:
            TEMPLATES[template] = template_adapter(template)
    if not TEMPLATES[template]:
        abort(500, 'Template not found')
    args['abort'] = abort
    args['request'] = request
    args['response'] = response
    return TEMPLATES[template].render(**args)


def mako_template(template_name, **args):
    return template(template_name, template_adapter=MakoTemplate, **args)






# Database

class BottleBucket(object):
    '''Memory-caching wrapper around anydbm'''
    def __init__(self, name):
        self.__dict__['name'] = name
        self.__dict__['db'] = dbm.open(DB_PATH + '/%s.db' % name, 'c')
        self.__dict__['mmap'] = {}
            
    def __getitem__(self, key):
        if key not in self.mmap:
            self.mmap[key] = pickle.loads(self.db[key])
        return self.mmap[key]
    
    def __setitem__(self, key, value):
        self.mmap[key] = value
    
    def __delitem__(self, key):
        if key in self.mmap:
            del self.mmap[key]
        del self.db[key]

    def __getattr__(self, key):
        try: return self[key]
        except KeyError: raise AttributeError(key)

    def __setattr__(self, key, value):
        self[key] = value

    def __delattr__(self, key):
        try: del self[key]
        except KeyError: raise AttributeError(key)

    def __iter__(self):
        return iter(self.ukeys())
    
    def __contains__(self, key):
        return key in self.ukeys()
  
    def __len__(self):
        return len(self.ukeys())

    def keys(self):
        return list(self.ukeys())

    def ukeys(self):
      return set(self.db.keys()) | set(self.mmap.keys())

    def save(self):
        self.close()
        self.__init__(self.name)
    
    def close(self):
        for key in self.mmap.keys():
            pvalue = pickle.dumps(self.mmap[key], pickle.HIGHEST_PROTOCOL)
            if key not in self.db or pvalue != self.db[key]:
                self.db[key] = pvalue
        self.mmap.clear()
        self.db.close()
        
    def clear(self):
        for key in self.db.keys():
            del self.db[key]
        self.mmap.clear()
        
    def update(self, other):
        self.mmap.update(other)

    def get(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            if default:
                return default
            raise


class BottleDB(threading.local):
    '''Holds multible BottleBucket instances in a thread-local way.'''
    def __init__(self):
        self.__dict__['open'] = {}
        
    def __getitem__(self, key):
        if key not in self.open and not key.startswith('_'):
            self.open[key] = BottleBucket(key)
        return self.open[key]

    def __setitem__(self, key, value):
        if isinstance(value, BottleBucket):
            self.open[key] = value
        elif hasattr(value, 'items'):
            if key not in self.open:
                self.open[key] = BottleBucket(key)
            self.open[key].clear()
            for k, v in value.items():
                self.open[key][k] = v
        else:
            raise ValueError("Only dicts and BottleBuckets are allowed.")

    def __delitem__(self, key):
        if key not in self.open:
            self.open[key].clear()
            self.open[key].save()
            del self.open[key]

    def __getattr__(self, key):
        try: return self[key]
        except KeyError: raise AttributeError(key)

    def __setattr__(self, key, value):
        self[key] = value

    def __delattr__(self, key):
        try: del self[key]
        except KeyError: raise AttributeError(key)

    def save(self):
        self.close()
        self.__init__()
    
    def close(self):
        for db in self.open.values():
            db.close()
        self.open.clear()






# Modul initialization

DB_PATH = './'
DEBUG = False
OPTIMIZER = False
TEMPLATE_PATH = ['./%s.tpl', './views/%s.tpl']
TEMPLATES = {}
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

request = Request()
response = Response()
db = BottleDB()
local = threading.local()

@error(500)
def error500(exception):
    if DEBUG:
        return "<br>\n".join(traceback.format_exc(10).splitlines()).replace('  ','&nbsp;&nbsp;')
    else:
        return """<b>Error:</b> Internal server error."""

def error_default(exception):
    status = response.status
    name = HTTP_CODES.get(status,'Unknown').title()
    url = request.path
    yield '<!DOCTYPE HTML PUBLIC "-//IETF//DTD HTML 2.0//EN">'
    yield template('<html><head><title>Error {{status}}: {{msg}}</title>'+\
      '</head><body><h1>Error {{status}}: {{msg}}</h1>'+\
      '<p>Sorry, the requested URL {{url}} caused an error.</p>', 
      status=status, msg=name, url=url)
    if hasattr(exception, 'output'):
      yield exception.output
    yield '</body></html>'
