#!/usr/bin/python
# -*- coding: utf-8 -*-

import unittest
import sys, os, os.path
import bottle
import tempfile
TMPDIR = tempfile.mkdtemp(prefix='bottle_unittest_') + '/'

class TestDB(unittest.TestCase):

    def setUp(self):
        bottle.DB_PATH = TMPDIR
        for f in os.listdir(TMPDIR):
            os.unlink(os.path.join(TMPDIR, f))

    def tearDown(self):
        for f in os.listdir(TMPDIR):
            os.unlink(os.path.join(TMPDIR, f))
        os.rmdir(TMPDIR)

    def test_save(self):
        """ DB: Save to disk """
        data = [1, 1.5, 'a', 'ä']
        bottle.db.db1.value1 = data
        bottle.db['db2']['value2'] = data

        self.assertEqual(bottle.db['db1']['value1'], data)
        self.assertEqual(bottle.db.db2.value2, data)
        bottle.db.close()
        self.assertEqual(bottle.db['db1']['value1'], data)
        self.assertEqual(bottle.db.db2.value2, data)

suite = unittest.TestSuite()
suite.addTest(unittest.makeSuite(TestDB))

if __name__ == '__main__':
    unittest.main()
