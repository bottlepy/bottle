#!/usr/bin/python
# -*- coding: utf-8 -*-

import unittest
import sys, os.path
TESTDIR = os.path.dirname(os.path.abspath(__file__))
DISTDIR = os.path.dirname(TESTDIR)
sys.path.insert(0, TESTDIR)
sys.path.insert(0, DISTDIR)

from bottle import route, Bottle

class TestRoutes(unittest.TestCase):

    def test_static(self):
        """ Routes: Static routes """
        app = Bottle()
        token = 'abc'
        routes = ['','/','/abc','abc','/abc/','/abc/def','/abc/def.ghi']
        for r in routes:
            app.add_route(r, token, simple=True)
        self.assertTrue('GET' in app.simple_routes)
        r = [r for r in app.simple_routes['GET'].values() if r == 'abc']
        self.assertEqual(5, len(r))
        for r in routes:
            self.assertEqual(token, app.match_url(r)[0])

    def test_dynamic(self):
        """ Routes: Dynamic routes """ 
        app = Bottle()
        token = 'abcd'
        app.add_route('/:a/:b', token)
        self.assertTrue('GET' in app.regexp_routes)
        self.assertEqual(token, app.match_url('/aa/bb')[0])
        self.assertEqual(None, app.match_url('/aa')[0])
        self.assertEqual(repr({'a':'aa','b':'bb'}), repr(app.match_url('/aa/bb')[1]))

    def test_syntax(self):
        """ Routes: Syntax """ 
        #self.assertEqual(r'^/(?P<bla>[^/]+)$', compile_route('/:bla').pattern)
        #self.assertEqual(r'^/(?P<bla>[^/]+)/(?P<blub>[^/]+)$', compile_route('/:bla/:blub').pattern)
        #self.assertEqual(r'^/(?P<bla>[0-9]+)$', compile_route('/:bla#[0-9]+#').pattern)
        #self.assertEqual(r'^/(?P<bla>[0-9]+)$', compile_route('/:bla:[0-9]+:').pattern)
        #self.assertEqual(r'^/(?P<bla>[0-9]+)$', compile_route('/:bla|[0-9]+|').pattern)


suite = unittest.TestSuite()
suite.addTest(unittest.makeSuite(TestRoutes))

if __name__ == '__main__':
    unittest.main()
