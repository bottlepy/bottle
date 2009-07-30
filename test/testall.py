#!/usr/bin/python
# -*- coding: utf-8 -*-

import unittest
import sys, os.path
import test_templates
import test_routes
import test_environ
import test_db
import test_wsgi

suite = unittest.TestSuite()
suite.addTest(test_templates.suite)
suite.addTest(test_routes.suite)
suite.addTest(test_environ.suite)
suite.addTest(test_db.suite)
suite.addTest(test_wsgi.suite)

if __name__ == '__main__':
    result = unittest.TextTestRunner(verbosity=0).run(suite)
    sys.exit((result.errors or result.failures) and 1 or 0)

