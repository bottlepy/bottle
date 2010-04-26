# -*- coding: utf-8 -*-
import unittest
import sys, os.path
import bottle
import urllib2
from StringIO import StringIO
import thread
import time

try:
    import wsgi_intercept
    import wsgi_intercept.urllib2_intercept
    wsgi_intercept.urllib2_intercept.install_opener()
except ImportError:
    print "WARNING: WSGI tests need wsgi_intercept. Not testing!"
    wsgi_intercept = None

class MethodRequest(urllib2.Request):
    ''' Used to create HEAD/PUT/DELETE/... requests with urllib2 '''
    def set_method(self, method):
        self.method = method.upper()
    def get_method(self):
        return getattr(self, 'method', urllib2.Request.get_method(self))

class WsgiTestBase(unittest.TestCase):
    def setUp(self):
        ''' Create a new Bottle app set it as default_app and register it to urllib2 '''
        self.url = 'http://test:80'
        self.wsgi = bottle.Bottle()
        self.oldapp = bottle.default_app()
        bottle.default_app(self.wsgi)
        wsgi_intercept.add_wsgi_intercept('test', 80, bottle.default_app)

    def tearDown(self):
        ''' Recover the olt default_app and remove wsgi_intercept from urllib2 '''
        wsgi_intercept.remove_wsgi_intercept('test', 80)
        bottle.default_app(self.oldapp)

    def urlopen(self, url, post=None, method=None):
        ''' Open a path using urllip2.urlopen and the wsgi_intercept domain '''
        r = MethodRequest(self.url+url, post)
        if method:
            r.set_method('HEAD')
        try:
            return urllib2.urlopen(r)
        except urllib2.HTTPError, e:
            return e

class TestWsgi(WsgiTestBase):
    ''' Tests for WSGI functionality, routing and output casting (decorators) '''

    def test_get(self):
        """ WSGI: GET routes"""
        @bottle.route('/')
        def test(): return 'test'
        self.assertEqual(404, self.urlopen('/not/found').code)
        self.assertEqual(404, self.urlopen('/', post="var=value").code)
        self.assertEqual('test', self.urlopen('/').read())

    def test_post(self):
        """ WSGI: POST routes"""
        @bottle.route('/', method='POST')
        def test(): return 'test'
        self.assertEqual(404, self.urlopen('/not/found').code)
        self.assertEqual(404, self.urlopen('/').code)
        self.assertEqual('test', self.urlopen('/', post="var=value").read())

    def test_headget(self):
        """ WSGI: HEAD routes and GET fallback"""
        @bottle.route('/get')
        def test(): return 'test'
        @bottle.route('/head', method='HEAD')
        def test2(): return 'test'
        # GET -> HEAD
        self.assertEqual(404, self.urlopen('/head').code)
        # HEAD -> HEAD
        self.assertEqual(200, self.urlopen('/head', method='HEAD').code)
        self.assertEqual('', self.urlopen('/head', method='HEAD').read())
        # HEAD -> GET
        self.assertEqual(200, self.urlopen('/get', method='HEAD').code)
        self.assertEqual('', self.urlopen('/get', method='HEAD').read())

    def test_500(self):
        """ WSGI: Exceptions within handler code (HTTP 500) """
        @bottle.route('/')
        def test(): return 1/0
        self.assertEqual(500, self.urlopen('/').code)
        bottle.default_app().catchall = False
        self.assertRaises(ZeroDivisionError, self.urlopen, '/')
        

    def test_503(self):
        """ WSGI: Server stopped (HTTP 503) """
        @bottle.route('/')
        def test(): return 'bla'
        self.assertEqual(200, self.urlopen('/').code)
        bottle.default_app().serve = False
        self.assertEqual(503, self.urlopen('/').code)

    def test_default(self):
        """ WSGI: default routes """
        @bottle.route('/')
        def test2(): return 'test'
        self.assertEqual(404, self.urlopen('/not/found').code)
        self.assertEqual(200, self.urlopen('/').code)
        self.assertEqual('test', self.urlopen('/').read())
        @bottle.default()
        def test(): return 'default'
        self.assertEqual(200, self.urlopen('/not/found').code)
        self.assertEqual('default', self.urlopen('/not/found').read())
        self.assertEqual(200, self.urlopen('/').code)
        self.assertEqual('test', self.urlopen('/').read())

    def test_401(self):
        """ WSGI: abort(401, '') (HTTP 401) """
        @bottle.route('/')
        def test(): bottle.abort(401)
        self.assertEqual(401, self.urlopen('/').code)
        @bottle.error(401)
        def err(e):
            bottle.response.status = 200
            return str(type(e))
        self.assertEqual(200, self.urlopen('/').code)
        self.assertEqual("<class 'bottle.HTTPError'>", self.urlopen('/').read())

    def test_307(self):
        """ WSGI: redirect (HTTP 307) """
        @bottle.route('/')
        def test(): bottle.redirect('/yes')
        @bottle.route('/yes')
        def test2(): return 'yes'
        self.assertEqual(200, self.urlopen('/').code)
        self.assertEqual('yes', self.urlopen('/').read())

    def test_interrupt(self):
        """ WSGI: Server stopped (HTTP 503) """
        @bottle.route('/')
        def test(): raise KeyboardInterrupt()
        self.assertRaises(KeyboardInterrupt, self.urlopen, '/')

    def test_casting(self):
        """ WSGI: Output Casting (strings an lists) """
        @bottle.route('/str')
        def test(): return 'test'
        self.assertEqual('test', self.urlopen('/str').read())
        @bottle.route('/list')
        def test2(): return ['t','e','st']
        self.assertEqual('test', self.urlopen('/list').read())
        @bottle.route('/empty')
        def test3(): return []
        self.assertEqual('', self.urlopen('/empty').read())
        @bottle.route('/none')
        def test4(): return None
        self.assertEqual('', self.urlopen('/none').read())
        @bottle.route('/bad')
        def test5(): return 12345
        self.assertEqual(500, self.urlopen('/bad').code)

    def test_file(self):
        """ WSGI: Output Casting (files) """
        @bottle.route('/file')
        def test(): return StringIO('test')
        self.assertEqual('test', self.urlopen('/file').read())


    def test_unicode(self):
        """ WSGI: Test Unicode support """
        @bottle.route('/unicode')
        def test3(): return u'äöüß'
        @bottle.route('/unicode2')
        def test4(): return [u'äöüß']
        @bottle.route('/unicode3')
        def test5():
            bottle.response.content_type='text/html; charset=iso-8859-15'
            return u'äöüß'  
        self.assertEqual(u'äöüß'.encode('utf8'), self.urlopen('/unicode').read())
        self.assertEqual(u'äöüß'.encode('utf8'), self.urlopen('/unicode2').read())
        self.assertEqual(u'äöüß'.encode('iso-8859-15'), self.urlopen('/unicode3').read())

    def test_json(self):
        """ WSGI: Autojson feature """
        @bottle.route('/json')
        def test(): return {'a': 1}
        self.assertEqual(r'{"a":1}', ''.join(self.urlopen('/json').read().split()))
        self.assertEqual('application/json', self.urlopen('/json').info().getheader('Content-Type',''))

    def test_emptyjson(self):
        """ WSGI: Autojson feature for empty dicts """
        @bottle.route('/json')
        def test(): return {}
        self.assertEqual(r'{}', ''.join(self.urlopen('/json').read().split()))
        self.assertEqual('application/json', self.urlopen('/json').info().getheader('Content-Type',''))

    def test_cookie(self):
        """ WSGI: Cookies """
        @bottle.route('/cookie')
        def test():
            bottle.response.COOKIES['a']="a"
            bottle.response.set_cookie('b','b')
            bottle.response.set_cookie('c','c', path='/')
            return 'hello'
        c = self.urlopen('/cookie').info().getheader('Set-Cookie','')
        c = [x.strip() for x in c.split(',')]
        self.assertTrue('a=a' in c)
        self.assertTrue('b=b' in c)
        self.assertTrue('c=c; Path=/' in c)


class TestDecorators(WsgiTestBase):
    ''' Tests Decorators '''

    def test_view(self):
        """ WSGI: Test view-decorator (should override autojson) """
        @bottle.route('/tpl')
        @bottle.view('stpl_t2main')
        def test():
            return dict(content='1234')
        result='+base+\n+main+\n!1234!\n+include+\n-main-\n+include+\n-base-\n'
        self.assertEqual('text/html', self.urlopen('/tpl').info().getheader('Content-Type',''))
        self.assertEqual(result, self.urlopen('/tpl').read())
    
    def test_validate(self):
        """ WSGI: Test validate-decorator"""
        @bottle.route('/:var')
        @bottle.route('/')
        @bottle.validate(var=int)
        def test(var): return 'x' * var
        self.assertEqual(403, self.urlopen('/noint').code)
        self.assertEqual(403, self.urlopen('/').code)
        self.assertEqual(200, self.urlopen('/5').code)
        self.assertEqual('xxx', self.urlopen('/3').read())


class TestRun(WsgiTestBase):
    ''' Tests Running a Server '''

    def test_wsgiref(self):
        """ WSGI: Test wsgiref """
        @bottle.route('/test')
        def test():
            return 'test'
        def paratest():
            try:
                time.sleep(1)
                self.assertEqual('test', urllib2.urlopen('http://127.0.0.1:61382/test').read())
            finally:
                thread.interrupt_main()
        
        thread.start_new_thread(paratest, ())
        bottle.run(port=61382, quiet=True)


suite = unittest.TestSuite()
if wsgi_intercept:
    suite.addTest(unittest.makeSuite(TestWsgi))
    suite.addTest(unittest.makeSuite(TestDecorators))
    suite.addTest(unittest.makeSuite(TestRun))

if __name__ == '__main__':
    unittest.main()
