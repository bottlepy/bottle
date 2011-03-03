# -*- coding: utf-8 -*-
'''Everything returned by Bottle()._cast() MUST be WSGI compatiple.'''

import unittest
import bottle
from tools import ServerTestBase, tob, tobs

class TestOutputFilter(ServerTestBase):
    ''' Tests for WSGI functionality, routing and output casting (decorators) '''

    def test_bytes(self):
        self.app.route('/')(lambda: tob('test'))
        self.assertBody('test')

    def test_bytearray(self):
        self.app.route('/')(lambda: map(tob, ['t', 'e', 'st']))
        self.assertBody('test')

    def test_tuple(self):
        self.app.route('/')(lambda: ('t', 'e', 'st'))
        self.assertBody('test')

    def test_emptylist(self):
        self.app.route('/')(lambda: [])
        self.assertBody('')

    def test_none(self):
        self.app.route('/')(lambda: None)
        self.assertBody('')

    def test_illegal(self):
        self.app.route('/')(lambda: 1234)
        self.assertStatus(500)
        self.assertInBody('Unhandled exception')

    def test_error(self):
        self.app.route('/')(lambda: 1/0)
        self.assertStatus(500)
        self.assertInBody('ZeroDivisionError')

    def test_fatal_error(self):
        @self.app.route('/')
        def test(): raise KeyboardInterrupt()
        self.assertRaises(KeyboardInterrupt, self.assertStatus, 500)

    def test_file(self):
        self.app.route('/')(lambda: tobs('test'))
        self.assertBody('test')

    def test_unicode(self):
        self.app.route('/')(lambda: u'äöüß')
        self.assertBody(u'äöüß'.encode('utf8'))

        self.app.route('/')(lambda: [u'äö',u'üß'])
        self.assertBody(u'äöüß'.encode('utf8'))

        @self.app.route('/')
        def test5():
            bottle.response.content_type='text/html; charset=iso-8859-15'
            return u'äöüß'
        self.assertBody(u'äöüß'.encode('iso-8859-15'))

        @self.app.route('/')
        def test5():
            bottle.response.content_type='text/html'
            return u'äöüß'
        self.assertBody(u'äöüß'.encode('utf8'))

    def test_json(self):
        self.app.route('/')(lambda: {'a': 1})
        if bottle.json_dumps:
            res = bottle.json_dumps({'a': 1})
            self.assertBody(res)
            self.assertHeader('Content-Type','application/json')
            self.assertHeader('Content-Length',str(len(res)))
        else:
            print "Warning: No json module installed."

    def test_json_emptydict(self):
        if bottle.json_dumps:
            res = bottle.json_dumps({})
            self.app.route('/')(lambda: {})
            self.assertBody(res)
            self.assertHeader('Content-Type','application/json')
            self.assertHeader('Content-Length',str(len(res)))

    def test_custom(self):
        self.app.route('/')(lambda: {'a': 1, 'b': 2})
        self.app.add_filter(dict, lambda x: x.keys())
        self.assertBody('ab')

    def test_generator_callback(self):
        @self.app.route('/')
        def test():
            bottle.response.headers['Test-Header'] = 'test'
            yield 'foo'
        self.assertBody('foo')
        self.assertHeader('Test-Header', 'test')
        
    def test_empty_generator_callback(self):
        @self.app.route('/')
        def test():
            yield
            bottle.response.headers['Test-Header'] = 'test'
        self.assertBody('')
        self.assertHeader('Test-Header', 'test')
        
    def test_error_in_generator_callback(self):
        @self.app.route('/')
        def test():
            yield 1/0
        self.assertStatus(500)
        self.assertInBody('ZeroDivisionError')

    def test_fatal_error_in_generator_callback(self):
        @self.app.route('/')
        def test():
            yield 
            raise KeyboardInterrupt()
        self.assertRaises(KeyboardInterrupt, self.assertStatus, 500)

    def test_httperror_in_generator_callback(self):
        @self.app.route('/')
        def test():
            yield
            bottle.abort(404, 'teststring')
        self.assertInBody('teststring')
        self.assertInBody('Error 404: Not Found')
        self.assertStatus(404)

    def test_httpresponse_in_generator_callback(self):
        @self.app.route('/')
        def test():
            yield bottle.HTTPResponse('test')
        self.assertBody('test')        
        
    def test_unicode_generator_callback(self):
        @self.app.route('/')
        def test():
            yield u'äöüß'
        self.assertBody(u'äöüß'.encode('utf8')) 
        
    def test_invalid_generator_callback(self):
        @self.app.route('/')
        def test():
            yield 1234
        self.assertStatus(500)
        self.assertInBody('Unsupported response type')
        
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

if __name__ == '__main__': #pragma: no cover
    unittest.main()
