# -*- coding: utf-8 -*-
import unittest
import sys, os.path
import bottle
import urllib2
from StringIO import StringIO
import thread
import time
from tools import ServerTestBase


class TestWsgi(ServerTestBase):
    ''' Tests for WSGI functionality, routing and output casting (decorators) '''

    def test_get(self):
        """ WSGI: GET routes"""
        @bottle.route('/')
        def test(): return 'test'
        self.assertEqual(404, self.urlopen('/not/found').code)
        self.assertEqual(404, self.urlopen('/', post="var=value").code)
        self.assertEqual(u'test'.encode('utf8'), self.urlopen('/').read())

    def test_post(self):
        """ WSGI: POST routes"""
        @bottle.route('/', method='POST')
        def test(): return 'test'
        self.assertEqual(404, self.urlopen('/not/found').code)
        self.assertEqual(404, self.urlopen('/').code)
        self.assertEqual(u'test'.encode('utf8'), self.urlopen('/', post="var=value").read())

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
        self.assertEqual(u''.encode('utf8'), self.urlopen('/head', method='HEAD').read())
        # HEAD -> GET
        self.assertEqual(200, self.urlopen('/get', method='HEAD').code)
        self.assertEqual(u''.encode('utf8'), self.urlopen('/get', method='HEAD').read())

    def test_500(self):
        """ WSGI: Exceptions within handler code (HTTP 500) """
        @bottle.route('/')
        def test(): return 1/0
        self.assertEqual(500, self.urlopen('/').code)

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
        self.assertEqual(u'test'.encode('utf8'), self.urlopen('/').read())
        @bottle.default()
        def test(): return 'default'
        self.assertEqual(200, self.urlopen('/not/found').code)
        self.assertEqual(u'default'.encode('utf8'), self.urlopen('/not/found').read())
        self.assertEqual(200, self.urlopen('/').code)
        self.assertEqual(u'test'.encode('utf8'), self.urlopen('/').read())

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
        self.assertEqual(u"<class 'bottle.HTTPError'>".encode('utf8'), self.urlopen('/').read())

    def test_307(self):
        """ WSGI: redirect (HTTP 307) """
        @bottle.route('/')
        def test(): bottle.redirect('/yes')
        @bottle.route('/yes')
        def test2(): return 'yes'
        self.assertEqual(200, self.urlopen('/').code)
        self.assertEqual(u'yes'.encode('utf8'), self.urlopen('/').read())

    def test_casting(self):
        """ WSGI: Output Casting (strings an lists) """
        @bottle.route('/str')
        def test(): return 'test'
        self.assertEqual(u'test'.encode('utf8'), self.urlopen('/str').read())
        @bottle.route('/list')
        def test2(): return ['t','e','st']
        self.assertEqual(u'test'.encode('utf8'), self.urlopen('/list').read())
        @bottle.route('/empty')
        def test3(): return []
        self.assertEqual(u''.encode('utf8'), self.urlopen('/empty').read())
        @bottle.route('/none')
        def test4(): return None
        self.assertEqual(u''.encode('utf8'), self.urlopen('/none').read())
        @bottle.route('/bad')
        def test5(): return 12345
        self.assertEqual(500, self.urlopen('/bad').code)

    def test_file(self):
        """ WSGI: Output Casting (files) """
        @bottle.route('/file')
        def test(): return StringIO('test')
        self.assertEqual(u'test'.encode('utf8'), self.urlopen('/file').read())


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
        self.assertEqual(ur'{"a":1}'.encode('utf8'), u''.encode('utf8').join(self.urlopen('/json').read().split()))
        self.assertEqual('application/json', self.urlopen('/json').info().get('Content-Type',''))

    def test_cookie(self):
        """ WSGI: Cookies """
        @bottle.route('/cookie')
        def test():
            bottle.response.COOKIES['a']="a"
            bottle.response.set_cookie('b','b')
            bottle.response.set_cookie('c','c', path='/')
            return 'hello'
        try:
            c = self.urlopen('/cookie').info().get_all('Set-Cookie','')
        except:
            c = self.urlopen('/cookie').info().getheader('Set-Cookie','').split(',')
            c = [x.strip() for x in c]
        self.assertTrue('a=a' in c)
        self.assertTrue('b=b' in c)
        self.assertTrue('c=c; Path=/' in c)


class TestDecorators(ServerTestBase):
    ''' Tests Decorators '''

    def test_view(self):
        """ WSGI: Test view-decorator (should override autojson) """
        @bottle.route('/tpl')
        @bottle.view('stpl_t2main')
        def test():
            return dict(content='1234')
        result=u'+base+\n+main+\n!1234!\n+include+\n-main-\n+include+\n-base-\n'.encode('utf8')
        self.assertEqual('text/html; charset=UTF-8', self.urlopen('/tpl').info().get('Content-Type',''))
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
        self.assertEqual(u'xxx'.encode('utf8'), self.urlopen('/3').read())


suite = unittest.TestSuite()
suite.addTest(unittest.makeSuite(TestWsgi))
suite.addTest(unittest.makeSuite(TestDecorators))

if __name__ == '__main__':
    unittest.main()
