#!/usr/bin/python
# -*- coding: utf-8 -*-

import unittest
import sys, os.path
TESTDIR = os.path.dirname(os.path.abspath(__file__))
DISTDIR = os.path.dirname(TESTDIR)
sys.path.insert(0, TESTDIR)
sys.path.insert(0, DISTDIR)

import test_templates
import test_routes
import test_environ
import test_db

suite = unittest.TestSuite()
suite.addTest(test_templates.suite)
suite.addTest(test_routes.suite)
suite.addTest(test_environ.suite)
suite.addTest(test_db.suite)

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite)

