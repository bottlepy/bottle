#!/usr/bin/python
# -*- coding: utf-8 -*-

import bottle
import unittest
import doctest
import glob
import sys

import test_templates
import test_stpl
import test_mako
import test_jinja2
import test_environ
import test_wsgi
import test_sendfile


suite = unittest.TestSuite()
suite.addTest(test_stpl.suite)
suite.addTest(test_mako.suite)
suite.addTest(test_jinja2.suite)
suite.addTest(test_templates.suite)
suite.addTest(test_environ.suite)
suite.addTest(test_wsgi.suite)
suite.addTest(test_sendfile.suite)

doctests = doctest.DocFileSuite(*glob.glob('./doctest_*.txt'))
suite.addTest(doctests)

if __name__ == '__main__':
    bottle.debug(True)
    result = unittest.TextTestRunner(verbosity=0).run(suite)
    sys.exit((result.errors or result.failures) and 1 or 0)

