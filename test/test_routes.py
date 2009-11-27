#!/usr/bin/python
# -*- coding: utf-8 -*-

import unittest
import sys, os.path
import bottle
from wsgiref.util import setup_testing_defaults


class TestRouter(unittest.TestCase):
    def setUp(self):
        self.r = bottle.Router()
    
    def test_match(self):
        """ SimpleRouter: Hit """
        td = dict()
        td['hello'] = 'foo'
        td['hello/bar'] = 'bar'
        td[''] = 'empty'
        td[''] = 'really empty'
        td['l'+('o'*1024)+'ng'] = 'Kind of long'
        for k, v in td.iteritems():
            self.r.add(k, v)
        for k, v in td.iteritems():
            self.assertEqual((v, None), self.r.match(k))
        for r in 'a hello2 hell hello_world rld wor'.split():
            self.assertTrue((None, None), self.r.match(r))

    def test_stress(self):
        """ SimpleRouter: Stress test """
        for i in xrange(10000):
            self.r.add('%d'%i,str(i))
        for i in xrange(10000):
            self.assertTrue((str(i), None), self.r.match('%d'%i))

    def test_syntax_placeholder(self):
        """ RegexpRouter: Syntax with placeholders """
        self.r.add('some/:path', 1)
        self.assertEqual((1, dict(path='test')), self.r.match('some/test'))
        self.assertEqual((None, None), self.r.match('some/'))
        self.assertEqual((None, None), self.r.match('some/test/'))
        self.assertEqual((None, None), self.r.match('somee/test'))
        self.r.add('some/:path/', 2)
        self.assertEqual((2, dict(path='test')), self.r.match('some/test/'))
        self.assertEqual((None, None), self.r.match('some//'))
        self.assertEqual((None, None), self.r.match('some/'))
        self.assertEqual((1, dict(path='test')), self.r.match('some/test'))
        self.assertEqual((None, None), self.r.match('some/test//'))
        self.r.add(':path/some', 3)
        self.assertEqual((3, dict(path='test')), self.r.match('test/some'))
        self.assertEqual((None, None), self.r.match('/some'))
        self.assertEqual((None, None), self.r.match('some'))
        self.r.add('/hey:foo/:bar', 4)
        self.assertEqual((4, dict(foo='1', bar='2')), self.r.match('/hey1/2'))
        self.assertEqual((None, None), self.r.match('/hey/1/2'))

    def test_syntax_advanced(self):
        """ RegexpRouter: Syntax with regex placeholders """
        self.r.add('some/:path#with([ a-z]+)[0-9]#', 1)
        self.assertEqual((1, dict(path='withnumbers 4')), self.r.match('some/withnumbers 4'))
        self.assertEqual((1, dict(path='with 4')), self.r.match('some/with 4'))
        self.assertEqual((None, None), self.r.match('some/number 4'))
        self.assertEqual((None, None), self.r.match('some/letters'))

    def test_stress(self):
        """ RegexpRouter: Stress test """
        for i in xrange(101):
            self.r.add('/get%d/:param'%i,str(i))
        for i in xrange(101):
            self.assertTrue((str(i), dict(param=str(i))), self.r.match('/get%d/%d'%(i, i+1)))





suite = unittest.TestSuite()
suite.addTest(unittest.makeSuite(TestRouter))

if __name__ == '__main__':
    unittest.main()
