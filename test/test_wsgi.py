import unittest
import sys, os.path
import bottle
import urllib2

try:
    import wsgi_intercept
    import wsgi_intercept.urllib2_intercept
except ImportError:
    print "WARNING: WSGI tests need wsgi_intercept. Not testing!"

wsgi_intercept.urllib2_intercept.install_opener()

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
        
    def test_casting(self):
        """ WSGI: Output Casting (strings an lists) """
        @bottle.route('/str')
        def test(): return 'test'
        @bottle.route('/list')
        def test2(): return ['t','e','st']
        self.assertEqual('test', self.urlopen('/str').read())
        self.assertEqual('test', self.urlopen('/list').read())

    def test_unicode(self):
        """ WSGI: Test Unicode support """
        @bottle.route('/')
        def test():
            bottle.response.content_type = 'text/html; charset=utf-8'
            return u'test'
        self.assertEqual('test', self.urlopen('/').read())
     
    def test_json(self):
        """ WSGI: Autojson feature """
        @bottle.route('/json')
        def test(): return {'a': 1}
        self.assertEqual(r'{"a":1}', ''.join(self.urlopen('/json').read().split()))
        self.assertEqual('application/json', self.urlopen('/json').info().getheader('Content-Type',''))


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


suite = unittest.TestSuite()
suite.addTest(unittest.makeSuite(TestWsgi))
suite.addTest(unittest.makeSuite(TestDecorators))

if __name__ == '__main__':
    unittest.main()
