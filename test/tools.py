import bottle
import threading
import urllib
import urllib2
import sys
import time
import unittest
import wsgiref
import wsgiref.simple_server
from StringIO import StringIO

class MethodRequest(urllib2.Request):
    ''' Used to create HEAD/PUT/DELETE/... requests with urllib2 '''
    def set_method(self, method):
        self.method = method.upper()
    def get_method(self):
        return getattr(self, 'method', urllib2.Request.get_method(self))

class NonLoggingRequestHandler(wsgiref.simple_server.WSGIRequestHandler):
    def log_message(self, *args):
        pass
    def get_stderr(self):
        return StringIO()
        
class TestServer(bottle.ServerAdapter):
    ''' Bottle compatible ServerAdapter with no logging and a shutdown() routine '''
    def run(self, handler):
        from wsgiref.simple_server import make_server
        srv = make_server(self.host, self.port, handler, handler_class=NonLoggingRequestHandler)
        self.alive = True
        while self.alive:
            srv.handle_request()

    def urlopen(self, path, post=None, method=None):
        ''' Open a path using urllip2.urlopen and the wsgi_intercept domain '''
        url = 'http://%s:%d/%s' % (self.host, self.port, path.lstrip('/'))
        r = MethodRequest(url, post)
        if method:
            r.set_method(method)
        try:
            return urllib2.urlopen(r)
        except urllib2.HTTPError, e:
            return e
        
    def shutdown(self):
      self.alive = False
      self.urlopen('/shutdown/now', method='SHUTDOWN')
      
class ServerTestBase(unittest.TestCase):
    def setUp(self):
        ''' Create a new Bottle app set it as default_app and register it to urllib2 '''
        self.port = 61382
        self.host = 'localhost'
        self.app = bottle.Bottle()
        self.oldapp = bottle.default_app()
        bottle.default_app(self.app)
        self.server = TestServer(host=self.host, port=self.port)
        self.urlopen = self.server.urlopen
        self.thread = threading.Thread(target=bottle.run, args=(), kwargs=dict(app=self.app, server=self.server, quiet=True))
        self.thread.start()

    def tearDown(self):
        ''' Recover the olt default_app and remove wsgi_intercept from urllib2 '''
        self.server.shutdown()
        self.thread.join()
        bottle.default_app(self.oldapp)
    
    def same(self, data, url):
        if isinstance(data, unicode):
            data = data.encode('utf-8')
        self.assertEqual(data, self.urlopen(url).read())
