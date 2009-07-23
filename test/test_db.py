#!/usr/bin/python
# -*- coding: utf-8 -*-

import unittest
import sys, os, os.path
TESTDIR = os.path.dirname(os.path.abspath(__file__))
DISTDIR = os.path.dirname(TESTDIR)
sys.path.insert(0, TESTDIR)
sys.path.insert(0, DISTDIR)

import bottle
bottle.DB_PATH = '/tmp/'

class TestDB(unittest.TestCase):

    def test_save(self):
        """ DB: Save to disk """
        if os.path.exists('/tmp/db1.db'):
            os.unlink('/tmp/db1.db')
        if os.path.exists('/tmp/db2.db'):
            os.unlink('/tmp/db2.db')

        data = [1, 1.5, 'a', u'ä']
        bottle.db.db1.value1 = data
        bottle.db['db2']['value2'] = data

        self.assertEqual(bottle.db['db1']['value1'], data)
        self.assertEqual(bottle.db.db2.value2, data)
        bottle.db.close()
        self.assertEqual(bottle.db['db1']['value1'], data)
        self.assertEqual(bottle.db.db2.value2, data)
        self.assertTrue(os.path.exists('/tmp/db1.db'))
        self.assertTrue(os.path.exists('/tmp/db2.db'))

suite = unittest.TestSuite()
suite.addTest(unittest.makeSuite(TestDB))

if __name__ == '__main__':
    unittest.main()
