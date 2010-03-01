# -*- coding: utf-8 -*-
import unittest
import sys, os.path
import bottle
import urllib2
from StringIO import StringIO
import thread
import time
from tools import ServerTestBase, tob


class TestWsgi(ServerTestBase):
    ''' Tests for WSGI functionality, routing and output casting (decorators) '''

    def test_get(self):
        """ WSGI: GET routes"""
        @bottle.route('/')
        def test(): return 'test'
        self.assertStatus(404, '/not/found')
        self.assertStatus(404, '/', post="var=value")
        self.assertBody('test', '/')

    def test_post(self):
        """ WSGI: POST routes"""
        @bottle.route('/', method='POST')
        def test(): return 'test'
        self.assertStatus(404, '/not/found')
        self.assertStatus(404, '/')
        self.assertBody('test', '/', post="var=value")

    def test_headget(self):
        """ WSGI: HEAD routes and GET fallback"""
        @bottle.route('/get')
        def test(): return 'test'
        @bottle.route('/head', method='HEAD')
        def test2(): return 'test'
        # GET -> HEAD
        self.assertStatus(404, '/head')
        # HEAD -> HEAD
        self.assertStatus(200, '/head', method='HEAD')
        self.assertBody('', '/head', method='HEAD')
        # HEAD -> GET
        self.assertStatus(200, '/get', method='HEAD')
        self.assertBody('', '/get', method='HEAD')

    def test_anymethod(self):
        self.assertStatus(404, '/any')
        @bottle.route('/any', method='ANY')
        def test2(): return 'test'
        self.assertStatus(200, '/any', method='HEAD')
        self.assertBody('test', '/any', method='GET')
        self.assertBody('test', '/any', method='POST')
        self.assertBody('test', '/any', method='1337')
        @bottle.route('/any', method='GET')
        def test2(): return 'test2'
        self.assertBody('test2', '/any', method='GET')
        @bottle.route('/any', method='POST')
        def test2(): return 'test3'
        self.assertBody('test3', '/any', method='POST')
        self.assertBody('test', '/any', method='1337')

    def test_500(self):
        """ WSGI: Exceptions within handler code (HTTP 500) """
        @bottle.route('/')
        def test(): return 1/0
        self.assertStatus(500, '/')

    def test_503(self):
        """ WSGI: Server stopped (HTTP 503) """
        @bottle.route('/')
        def test(): return 'bla'
        self.assertStatus(200, '/')
        bottle.app().serve = False
        self.assertStatus(503, '/')

    def test_default(self):
        """ WSGI: default routes """
        @bottle.route('/')
        def test2(): return 'test'
        self.assertStatus(404,'/not/found')
        self.assertStatus(200,'/')
        self.assertBody('test', '/')
        @bottle.default()
        def test(): return 'default'
        self.assertStatus(200,'/not/found')
        self.assertBody('default', '/not/found')
        self.assertStatus(200,'/')
        self.assertBody('test', '/')

    def test_401(self):
        """ WSGI: abort(401, '') (HTTP 401) """
        @bottle.route('/')
        def test(): bottle.abort(401)
        self.assertStatus(401,'/')
        @bottle.error(401)
        def err(e):
            bottle.response.status = 200
            return str(type(e))
        self.assertStatus(200,'/')
        self.assertBody("<class 'bottle.HTTPError'>",'/')

    def test_303(self):
        """ WSGI: redirect (HTTP 303) """
        @bottle.route('/')
        def test(): bottle.redirect('/yes')
        self.assertStatus(303, '/')
        self.assertHeader('Location', 'http://127.0.0.1/yes', '/')

    def test_casting(self):
        """ WSGI: Output Casting (strings an lists) """
        @bottle.route('/str')
        def test(): return 'test'
        self.assertBody('test', '/str')
        @bottle.route('/list')
        def test2(): return ['t', 'e', 'st']
        self.assertBody('test', '/list')
        @bottle.route('/empty')
        def test3(): return []
        self.assertBody('', '/empty')
        @bottle.route('/none')
        def test4(): return None
        self.assertBody('', '/none')
        @bottle.route('/bad')
        def test5(): return 12345
        self.assertStatus(500,'/bad')

    def test_file(self):
        """ WSGI: Output Casting (files) """
        @bottle.route('/file')
        def test(): return StringIO('test')
        self.assertBody('test', '/file')

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
        self.assertBody(u'äöüß'.encode('utf8'), '/unicode')
        self.assertBody(u'äöüß'.encode('utf8'), '/unicode2')
        self.assertBody(u'äöüß'.encode('iso-8859-15'), '/unicode3')

    def test_json(self):
        """ WSGI: Autojson feature """
        @bottle.route('/json')
        def test(): return {'a': 1}
        self.assertBody(self.app.jsondump({'a': 1}), '/json')
        self.assertHeader('Content-Type','application/json', '/json')

    def test_cookie(self):
        """ WSGI: Cookies """
        @bottle.route('/cookie')
        def test():
            bottle.response.COOKIES['a']="a"
            bottle.response.set_cookie('b', 'b')
            bottle.response.set_cookie('c', 'c', path='/')
            return 'hello'
        try:
            c = self.urlopen('/cookie')['header'].get_all('Set-Cookie', '')
        except:
            c = self.urlopen('/cookie')['header'].get('Set-Cookie', '').split(',')
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
        result = '+base+\n+main+\n!1234!\n+include+\n-main-\n+include+\n-base-\n'
        self.assertHeader('Content-Type', 'text/html; charset=UTF-8', '/tpl')
        self.assertBody(result, '/tpl')

    def test_validate(self):
        """ WSGI: Test validate-decorator"""
        @bottle.route('/:var')
        @bottle.route('/')
        @bottle.validate(var=int)
        def test(var): return 'x' * var
        self.assertStatus(403,'/noint')
        self.assertStatus(403,'/')
        self.assertStatus(200,'/5')
        self.assertBody('xxx', '/3')

    def test_routebuild(self):
        """ WSGI: Test validate-decorator"""
        @bottle.route('/a/:b/c', name='named')
        def test(var): pass
        self.assertEqual('/a/xxx/c', bottle.url('named', b='xxx'))
        self.assertEqual('/a/xxx/c', bottle.app().get_url('named', b='xxx'))

    def test_decorators(self):
        app = bottle.Bottle()
        app.route('/g')('foo')
        bottle.route('/g')('foo')
        app.route('/g2', method='GET')('foo')
        bottle.get('/g2')('foo')
        app.route('/p', method='POST')('foo')
        bottle.post('/p')('foo')
        app.route('/p2', method='PUT')('foo')
        bottle.put('/p2')('foo')
        app.route('/d', method='DELETE')('foo')
        bottle.delete('/d')('foo')
        self.assertEqual(app.routes, bottle.app().routes)

    def test_autoroute(self):
        app = bottle.Bottle()
        def a(): pass
        def b(x): pass
        def c(x, y): pass
        def d(x, y=5): pass
        def e(x=5, y=6): pass
        self.assertEqual(['a'],list(bottle.yieldroutes(a)))
        self.assertEqual(['b/:x'],list(bottle.yieldroutes(b)))
        self.assertEqual(['c/:x/:y'],list(bottle.yieldroutes(c)))
        self.assertEqual(['d/:x','d/:x/:y'],list(bottle.yieldroutes(d)))
        self.assertEqual(['e','e/:x','e/:x/:y'],list(bottle.yieldroutes(e)))

if __name__ == '__main__':
    unittest.main()
