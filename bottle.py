# -*- coding: utf-8 -*-
"""
Bottle is a fast and simple micro-framework for small web applications. It
offers request dispatching (Routes) with url parameter support, templates,
key/value databases, a built-in HTTP Server and adapters for many third party
WSGI/HTTP-server and template engines - all in a single file and with no
dependencies other than the Python Standard Library.

Homepage and documentation: http://wiki.github.com/defnull/bottle

Special thanks to Stefan Matthias Aust [http://github.com/sma]
  for his contribution to SimpleTemplate

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
__version__ = '0.6.6'
__license__ = 'MIT'

import types
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
import warnings
import email.utils
from wsgiref.headers import Headers as HeaderWrapper
from Cookie import SimpleCookie
import anydbm as dbm
import subprocess
import thread


try:
    from urlparse import parse_qs
except ImportError: # pragma: no cover
    from cgi import parse_qs

try:
    import cPickle as pickle
except ImportError: # pragma: no cover
    import pickle as pickle
  
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


class HTTPError(BottleException):
    """
    A way to break the execution and instantly jump to an error handler.
    """
    def __init__(self, status, text):
        self.output = text
        self.http_status = int(status)
        BottleException.__init__(self, status, text)

    def __repr__(self):
        return 'HTTPError(%d,%s)' % (self.http_status, repr(self.output))

    def __str__(self):
        return HTTP_ERROR_TEMPLATE % {
            'status' : self.http_status,
            'url' : request.path,
            'error_name' : HTTP_CODES.get(self.http_status, 'Unknown').title(),
            'error_message' : ''.join(self.output)
        }


class BreakTheBottle(BottleException):
    """
    Not an exception, but a straight jump out of the controller code.
    Causes the Bottle to instantly call start_response() and return the
    content of output
    """
    def __init__(self, output):
        self.output = output






# WSGI abstraction: Request and response management

_default_app = None
def default_app(newapp = None):
    """
    Returns the current default app or sets a new one.
    Defaults to an instance of Bottle
    """
    global _default_app
    if newapp:
        _default_app = newapp
    if not _default_app:
        _default_app = Bottle()
    return _default_app


class Bottle(object):

    def __init__(self, catchall=True, optimize=False, autojson=True):
        self.simple_routes = {}
        self.regexp_routes = {}
        self.default_route = None
        self.error_handler = {}
        self.optimize = optimize
        self.autojson = autojson
        self.catchall = catchall
        self.serve = True

    def match_url(self, url, method='GET'):
        """
        Returns the first matching handler and a parameter dict or (None, None)
        """
        url = url.strip().lstrip("/ ")
        # Search for static routes first
        route = self.simple_routes.get(method,{}).get(url,None)
        if route:
            return (route, {})
        
        routes = self.regexp_routes.get(method,[])
        for i in range(len(routes)):
            match = routes[i][0].match(url)
            if match:
                handler = routes[i][1]
                if i > 0 and self.optimize and random.random() <= 0.001:
                    routes[i-1], routes[i] = routes[i], routes[i-1]
                return (handler, match.groupdict())
        if self.default_route:
            return (self.default_route, {})
        if method == 'HEAD': # Fall back to GET
            return self.match_url(url)
        else:
            return (None, None)

    def add_controller(self, route, controller, **kargs):
        """ Adds a controller class or object """
        if '{action}' not in route and 'action' not in kargs:
            raise BottleException("Routes to controller classes or object MUST"
                " contain an {action} placeholder or use the action-parameter")
        for action in (m for m in dir(controller) if not m.startswith('_')):
            handler = getattr(controller, action)
            if callable(handler) and action == kargs.get('action', action):
                self.add_route(route.replace('{action}', action), handler, **kargs)

    def add_route(self, route, handler, method='GET', simple=False, **kargs):
        """ Adds a new route to the route mappings. """
        if isinstance(handler, type) and issubclass(handler, BaseController):
            handler = handler()
        if isinstance(handler, BaseController):
            self.add_controller(route, handler, method=method, simple=simple, **kargs)
            return
        method = method.strip().upper()
        route = route.strip().lstrip('$^/ ').rstrip('$^ ')
        if re.match(r'^(\w+/)*\w*$', route) or simple:
            self.simple_routes.setdefault(method, {})[route] = handler
        else:
            route = re.sub(r':([a-zA-Z_]+)(?P<uniq>[^\w/])(?P<re>.+?)(?P=uniq)',
                           r'(?P<\1>\g<re>)',route)
            route = re.sub(r':([a-zA-Z_]+)', r'(?P<\1>[^/]+)', route)
            route = re.compile('^%s$' % route)
            self.regexp_routes.setdefault(method, []).append([route, handler])

    def route(self, url, **kargs):
        """
        Decorator for request handler.
        Same as add_route(url, handler, **kargs).
        """
        def wrapper(handler):
            self.add_route(url, handler, **kargs)
            return handler
        return wrapper

    def set_default(self, handler):
        self.default_route = handler

    def default(self):
        """ Decorator for request handler. Same as add_defroute( handler )."""
        def wrapper(handler):
            self.set_default(handler)
            return handler
        return wrapper

    def set_error_handler(self, code, handler):
        """ Adds a new error handler. """
        self.error_handler[int(code)] = handler

    def error(self, code=500):
        """
        Decorator for error handler.
        Same as set_error_handler(code, handler).
        """
        def wrapper(handler):
            self.set_error_handler(code, handler)
            return handler
        return wrapper

    def cast(self, out):
        """
        Cast the output to an iterable of strings or something WSGI can handle.
        Set Content-Type and Content-Length when possible. Then clear output
        on HEAD requests.
        Supports: False, str, unicode, list(unicode), dict(), open()
        """
        if self.autojson and json_dumps and isinstance(out, dict):
            out = [json_dumps(out)]
            response.content_type = 'application/json'
        elif not out:
            out = []
            response.header['Content-Length'] = '0'
        elif isinstance(out, types.StringType):
            out = [out]
        elif isinstance(out, unicode):
            out = [out.encode(response.charset)]
        elif isinstance(out, list) and isinstance(out[0], unicode):
            out = map(lambda x: x.encode(response.charset), out)
        elif hasattr(out, 'read'):
            out = request.environ.get('wsgi.file_wrapper',
                  lambda x: iter(lambda: x.read(8192), ''))(out)
        if isinstance(out, list) and len(out) == 1:
            response.header['Content-Length'] = str(len(out[0]))
        if not hasattr(out, '__iter__'):
            raise TypeError('Request handler for route "%s" returned [%s] '
            'which is not iterable.' % (request.path, type(out).__name__))
        return out


    def __call__(self, environ, start_response):
        """ The bottle WSGI-interface. """
        request.bind(environ)
        response.bind()
        try: # Unhandled Exceptions
            try: # Bottle Error Handling
                if not self.serve:
                    abort(503, "Server stopped")
                handler, args = self.match_url(request.path, request.method)
                if not handler:
                    raise HTTPError(404, "Not found")
                output = handler(**args)
                db.close()
            except BreakTheBottle, e:
                output = e.output
            except HTTPError, e:
                response.status = e.http_status
                output = self.error_handler.get(response.status, str)(e)
            output = self.cast(output)
            if response.status in (100, 101, 204, 304) or request.method == 'HEAD':
                output = [] # rfc2616 section 4.3
        except (KeyboardInterrupt, SystemExit, MemoryError):
            raise
        except Exception, e:
            response.status = 500
            if self.catchall:
                err = "Unhandled Exception: %s\n" % (repr(e))
                if DEBUG:
                    err += TRACEBACK_TEMPLATE % traceback.format_exc(10)
                output = [str(HTTPError(500, err))]
                request._environ['wsgi.errors'].write(err)
            else:
                raise
        status = '%d %s' % (response.status, HTTP_CODES[response.status])
        start_response(status, response.wsgiheaders())
        return output



class Request(threading.local):
    """ Represents a single request using thread-local namespace. """

    def bind(self, environ):
        """
        Binds the enviroment of the current request to this request handler
        """
        self._environ = environ
        self.environ = self._environ
        self._GET = None
        self._POST = None
        self._GETPOST = None
        self._COOKIES = None
        self.path = self._environ.get('PATH_INFO', '/').strip()
        if not self.path.startswith('/'):
            self.path = '/' + self.path

    @property
    def method(self):
        """ Get the request method (GET,POST,PUT,DELETE,...) """
        return self._environ.get('REQUEST_METHOD', 'GET').upper()

    @property
    def query_string(self):
        """ Get content of QUERY_STRING """
        return self._environ.get('QUERY_STRING', '')

    @property
    def input_length(self):
        """ Get content of CONTENT_LENGTH """
        try:
            return max(0,int(self._environ.get('CONTENT_LENGTH', '0')))
        except ValueError:
            return 0

    @property
    def GET(self):
        """ Get a dict with GET parameters. """
        if self._GET is None:
            data = parse_qs(self.query_string, keep_blank_values=True)
            self._GET = {}
            for key, value in data.iteritems():
                if len(value) == 1:
                    self._GET[key] = value[0]
                else:
                    self._GET[key] = value
        return self._GET

    @property
    def POST(self):
        """ Get a dict with parsed POST or PUT data. """
        if self._POST is None:
            data = cgi.FieldStorage(fp=self._environ['wsgi.input'],
                environ=self._environ, keep_blank_values=True)
            self._POST  = {}
            for item in data.list or []:
                name = item.name
                if not item.filename:
                    item = item.value
                self._POST.setdefault(name, []).append(item)
            for key in self._POST:
                if len(self._POST[key]) == 1:
                    self._POST[key] = self._POST[key][0]
        return self._POST

    @property
    def params(self):
        """ Returns a mix of GET and POST data. POST overwrites GET """
        if self._GETPOST is None:
            self._GETPOST = dict(self.GET)
            self._GETPOST.update(dict(self.POST))
        return self._GETPOST

    @property
    def COOKIES(self):
        """ Returns a dict with COOKIES. """
        if self._COOKIES is None:
            raw_dict = SimpleCookie(self._environ.get('HTTP_COOKIE',''))
            self._COOKIES = {}
            for cookie in raw_dict.itervalues():
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
        self.charset = 'utf8'

    def wsgiheaders(self):
        ''' Returns a wsgi conform list of header/value pairs '''
        for c in self.COOKIES.itervalues():
            self.header.add_header('Set-Cookie', c.OutputString())
        return [(h.title(), str(v)) for h, v in self.header.items()]

    @property
    def COOKIES(self):
        if not self._COOKIES:
            self._COOKIES = SimpleCookie()
        return self._COOKIES

    def set_cookie(self, key, value, **kargs):
        """
        Sets a Cookie. Optional settings:
        expires, path, comment, domain, max-age, secure, version, httponly
        """
        self.COOKIES[key] = value
        for k, v in kargs.iteritems():
            self.COOKIES[key][k] = v

    def get_content_type(self):
        """ Get the current 'Content-Type' header. """
        return self.header['Content-Type']
        
    def set_content_type(self, value):
        if 'charset=' in value:
            self.charset = value.split('charset=')[-1].split(';')[0].strip()
        self.header['Content-Type'] = value

    content_type = property(get_content_type, set_content_type, None,
                            get_content_type.__doc__)


class BaseController(object):
    _singleton = None
    def __new__(cls, *a, **k):
        if not cls._singleton:
            cls._singleton = object.__new__(cls, *a, **k)
        return cls._singleton


def abort(code=500, text='Unknown Error: Appliction stopped.'):
    """ Aborts execution and causes a HTTP error. """
    raise HTTPError(code, text)


def redirect(url, code=307):
    """ Aborts execution and causes a 307 redirect """
    response.status = code
    response.header['Location'] = url
    raise BreakTheBottle("")


def send_file(filename, root, guessmime = True, mimetype = None):
    """ Aborts execution and sends a static files as response. """
    root = os.path.abspath(root) + os.sep
    filename = os.path.abspath(os.path.join(root, filename.strip('/\\')))

    if not filename.startswith(root):
        abort(401, "Access denied.")
    if not os.path.exists(filename) or not os.path.isfile(filename):
        abort(404, "File does not exist.")
    if not os.access(filename, os.R_OK):
        abort(401, "You do not have permission to access this file.")

    if guessmime and not mimetype:
        mimetype = mimetypes.guess_type(filename)[0]
    if not mimetype: mimetype = 'text/plain'
    response.content_type = mimetype

    stats = os.stat(filename)
    if 'Last-Modified' not in response.header:
        lm = time.strftime("%a, %d %b %Y %H:%M:%S GMT", time.gmtime(stats.st_mtime))
        response.header['Last-Modified'] = lm
    if 'HTTP_IF_MODIFIED_SINCE' in request.environ:
        ims = request.environ['HTTP_IF_MODIFIED_SINCE']
        # IE sends "<date>; length=146"
        ims = ims.split(";")[0].strip()
        ims = parse_date(ims)
        if ims is not None and ims >= stats.st_mtime:
           abort(304, "Not modified")
    if 'Content-Length' not in response.header:
        response.header['Content-Length'] = str(stats.st_size)
    raise BreakTheBottle(open(filename, 'rb'))


def parse_date(ims):
    """
    Parses date strings usually found in HTTP header and returns UTC epoch.
    Understands rfc1123, rfc850 and asctime.
    """
    try:
        ts = email.utils.parsedate_tz(ims)
        if ts is not None:
            if ts[9] is None:
                return time.mktime(ts[:8] + (0,)) - time.timezone
            else:
                return time.mktime(ts[:8] + (0,)) - ts[9] - time.timezone
    except (ValueError, IndexError):
        return None






# Decorators

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


def route(url, **kargs):
    """
    Decorator for request handler. Same as add_route(url, handler, **kargs).
    """
    return default_app().route(url, **kargs)

def default():
    """
    Decorator for request handler. Same as set_default(handler).
    """
    return default_app().default()

def error(code=500):
    """
    Decorator for error handler. Same as set_error_handler(code, handler).
    """
    return default_app().error(code)






# Server adapter

class WSGIAdapter(object):
    def run(self, handler): # pragma: no cover
        pass

    def __repr__(self):
        return "%s()" % (self.__class__.__name__)


class CGIServer(WSGIAdapter):
    def run(self, handler):
        from wsgiref.handlers import CGIHandler
        CGIHandler().run(handler)


class ServerAdapter(WSGIAdapter):
    def __init__(self, host='127.0.0.1', port=8080, **kargs):
        WSGIAdapter.__init__(self)
        self.host = host
        self.port = int(port)
        self.options = kargs

    def __repr__(self):
        return "%s (%s:%d)" % (self.__class__.__name__, self.host, self.port)


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
    """
    Extremly fast webserver using libev.
    See http://william-os4y.livejournal.com/
    Experimental ...
    """
    def run(self, handler):
        import fapws._evwsgi as evwsgi
        from fapws import base
        evwsgi.start(self.host, self.port)
        evwsgi.set_base_module(base)
        def app(environ, start_response):
            environ['wsgi.multiprocess'] = False
            return handler(environ, start_response)
        evwsgi.wsgi_cb(('',app))
        evwsgi.run()


def run(app=None, server=WSGIRefServer, host='127.0.0.1', port=8080,
        interval=1, reloader=False, **kargs):
    """ Runs bottle as a web server. """
    if not app:
        app = default_app()
    
    quiet = bool(kargs.get('quiet', False))

    # Instantiate server, if it is a class instead of an instance
    if isinstance(server, type):
        if issubclass(server, CGIServer):
            server = server()
        elif issubclass(server, ServerAdapter):
            server = server(host=host, port=port, **kargs)

    if not isinstance(server, WSGIAdapter):
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
    def __init__(self, template='', name=None, filename=None, lookup=[]):
        """
        Create a new template.
        If a name is provided, but no filename and no template string, the
        filename is guessed using the lookup path list.
        Subclasses can assume that either self.template or self.filename is set.
        If both are present, self.template should be used.
        """
        self.name = name
        self.filename = filename
        self.template = template
        self.lookup = lookup
        if self.name and not self.filename:
            for path in self.lookup:
                fpath = os.path.join(path, self.name+'.tpl')
                if os.path.isfile(fpath):
                    self.filename = fpath
        if not self.template and not self.filename:
            raise TemplateError('Template (%s) not found.' % self.name)
        self.prepare()

    def prepare(self):
        """
        Run preparatios (parsing, caching, ...).
        It should be possible to call this multible times to refresh a template.
        """
        raise NotImplementedError

    def render(self, **args):
        """
        Render the template with the specified local variables and return an
        iterator of strings (bytes). This must be thread save!
        """
        raise NotImplementedError


class MakoTemplate(BaseTemplate):
    output_encoding=None
    input_encoding=None
    default_filters=None
    global_variables={}

    def prepare(self):
        from mako.template import Template
        from mako.lookup import TemplateLookup
        #TODO: This is a hack... http://github.com/defnull/bottle/issues#issue/8
        mylookup = TemplateLookup(directories=map(os.path.abspath, self.lookup)+['./'])
        if self.template:
            self.tpl = Template(self.template,
                                lookup=mylookup,
                                output_encoding=MakoTemplate.output_encoding,
                                input_encoding=MakoTemplate.input_encoding,
                                default_filters=MakoTemplate.default_filters
                                )
        else:
            self.tpl = Template(filename=self.filename,
                                lookup=mylookup,
                                output_encoding=MakoTemplate.output_encoding,
                                input_encoding=MakoTemplate.input_encoding,
                                default_filters=MakoTemplate.default_filters
                                )
 
    def render(self, **args):
        _defaults = MakoTemplate.global_variables.copy()
        _defaults.update(args)
        return self.tpl.render(**_defaults)


class CheetahTemplate(BaseTemplate):
    def prepare(self):
        from Cheetah.Template import Template
        self.context = threading.local()
        self.context.vars = {}
        if self.template:
            self.tpl = Template(source=self.template, searchList=[self.context.vars])
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
        if self.template:
            self.tpl = self.env.from_string(self.template)
        else:
            self.tpl = self.env.get_template(self.filename)

    def render(self, **args):
        return self.tpl.render(**args).encode("utf-8")
        
    def loader(self, name):
        if not name.endswith(".tpl"):
            for path in self.lookup:
                fpath = os.path.join(path, name+'.tpl')
                if os.path.isfile(fpath):
                    name = fpath
                    break
        f = open(name)
        try: return f.read()
        finally: f.close()


class SimpleTemplate(BaseTemplate):
    re_python = re.compile(r'^\s*%\s*(?:(if|elif|else|try|except|finally|for|'
                            'while|with|def|class)|(include|rebase)|(end)|(.*))')
    re_inline = re.compile(r'\{\{(.*?)\}\}')
    dedent_keywords = ('elif', 'else', 'except', 'finally')

    def prepare(self):
        if self.template:
            code = self.translate(self.template)
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
        for line in template.splitlines(True):
            lineend = '\n' if not line.endswith('\n') else ''
            m = self.re_python.match(line)
            if m:
                flush(allow_nobreak=True)
                keyword, subtpl, end, statement = m.groups()
                if keyword:
                    if keyword in self.dedent_keywords:
                        indent -= 1
                    code.append(" " * indent + line[m.start(1):])
                    indent += 1
                elif subtpl:
                    tmp = line[m.end(2):].strip().split(None, 1)
                    if not tmp:
                      code.append(' ' * indent + "_stdout.extend(_base)\n")
                    else:
                      name = tmp[0]
                      args = tmp[1:] and tmp[1] or ''
                      if name not in self.includes:
                        self.includes[name] = SimpleTemplate(name=name, lookup=self.lookup)
                      if subtpl == 'include':
                        code.append(' ' * indent + 
                                    "_ = _includes[%s].execute(_stdout, %s)\n"
                                    % (repr(name), args))
                      else:
                        code.append(' ' * indent + 
                                    "_tpl['_rebase'] = (_includes[%s], dict(%s))\n"
                                    % (repr(name), args))
                elif end:
                    indent -= 1
                    code.append(' ' * indent + '#' + line[m.start(3):] + lineend)
                elif statement:
                    code.append(' ' * indent + line[m.start(4):] + lineend)
            else:
                splits = self.re_inline.split(line) # text, (expr, text)*
                if len(splits) == 1:
                    strbuffer.append(line)
                else:
                    flush()
                    for i in range(1, len(splits), 2):
                        splits[i] = PyStmt(splits[i])
                    splits = [x for x in splits if bool(x)]
                    code.append(' ' * indent + "_stdout.extend(%s)\n" % repr(splits))
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
            TEMPLATES[tpl] = template_adapter(template=tpl, lookup=lookup)
        elif '.' in tpl:
            TEMPLATES[tpl] = template_adapter(filename=tpl, lookup=lookup)
        else:
            TEMPLATES[tpl] = template_adapter(name=tpl, lookup=lookup)
    if not TEMPLATES[tpl]:
        abort(500, 'Template (%s) not found' % tpl)
    args['abort'] = abort
    args['request'] = request
    args['response'] = response
    return TEMPLATES[tpl].render(**args)


def mako_template(tpl_name, **kargs):
    kargs['template_adapter'] = MakoTemplate
    return template(tpl_name, **kargs)

def cheetah_template(tpl_name, **kargs):
    kargs['template_adapter'] = CheetahTemplate
    return template(tpl_name, **kargs)

def jinja2_template(tpl_name, **kargs):
    kargs['template_adapter'] = Jinja2Template
    return template(tpl_name, **kargs)

def view(tpl_name, **defaults):
    ''' Decorator: Rendes a template for a handler.
        Return a dict of template vars to fill out the template.
    '''
    def decorator(func):
        def wrapper(**kargs):
            out = func(**kargs)
            defaults.update(out)
            return template(tpl_name, **defaults)
        return wrapper
    return decorator

def mako_view(tpl_name, **kargs):
    kargs['template_adapter'] = MakoTemplate
    return view(tpl_name, **kargs)

def cheetah_view(tpl_name, **kargs):
    kargs['template_adapter'] = CheetahTemplate
    return view(tpl_name, **kargs)

def jinja2_view(tpl_name, **kargs):
    kargs['template_adapter'] = Jinja2Template
    return view(tpl_name, **kargs)







# Database

class BottleBucket(object): # pragma: no cover
    """ Memory-caching wrapper around anydbm """
    def __init__(self, name):
        self.__dict__['name'] = name
        self.__dict__['db'] = dbm.open(DB_PATH + '/%s.db' % name, 'c')
        self.__dict__['mmap'] = {}
            
    def __getitem__(self, key):
        if key not in self.mmap:
            self.mmap[key] = pickle.loads(self.db[key])
        return self.mmap[key]
    
    def __setitem__(self, key, value):
        if not isinstance(key, str): raise TypeError("Bottle keys must be strings")
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
        for key in self.mmap:
            pvalue = pickle.dumps(self.mmap[key], pickle.HIGHEST_PROTOCOL)
            if key not in self.db or pvalue != self.db[key]:
                self.db[key] = pvalue
        self.mmap.clear()
        if hasattr(self.db, 'sync'):
            self.db.sync()
        if hasattr(self.db, 'close'):
            self.db.close()
        
    def clear(self):
        for key in self.db:
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


class BottleDB(threading.local): # pragma: no cover
    """ Holds multible BottleBucket instances in a thread-local way. """
    def __init__(self):
        self.__dict__['open'] = {}
        
    def __getitem__(self, key):
        warnings.warn("Please do not use bottle.db anymore. This feature is deprecated. You may use anydb directly.", DeprecationWarning)
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
            for k, v in value.iteritems():
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
        for db in self.open:
            self.open[db].close()
        self.open.clear()






# Modul initialization and configuration

DB_PATH = './'
TEMPLATE_PATH = ['./', './views/']
TEMPLATES = {}
DEBUG = False
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

HTTP_ERROR_TEMPLATE = """
<!DOCTYPE HTML PUBLIC "-//IETF//DTD HTML 2.0//EN">
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

TRACEBACK_TEMPLATE = """
<h2>Traceback:</h2>
<pre>
%s
</pre>
"""

request = Request()
response = Response()
db = BottleDB()
local = threading.local()

#TODO: Global and app local configuration (debug, defaults, ...) is a mess

def debug(mode=True):
    global DEBUG
    DEBUG = bool(mode)

def optimize(mode=True):
    default_app().optimize = bool(mode)


