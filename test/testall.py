#!/usr/bin/python
# -*- coding: utf-8 -*-

import bottle
import unittest
import doctest
import glob
import sys

if __name__ == '__main__':
    bottle.debug(True)
    unittests = [name[2:-3] for name in glob.glob('./test_*.py')]
    suite = unittest.defaultTestLoader.loadTestsFromNames(unittests)
    #doctests = glob.glob('./doctest_*.txt')
    #suite.addTest(doctest.DocFileSuite(*doctests))
    result = unittest.TextTestRunner(verbosity=0).run(suite)
    sys.exit((result.errors or result.failures) and 1 or 0)

