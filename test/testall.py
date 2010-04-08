#!/usr/bin/python
# -*- coding: utf-8 -*-

import unittest
import sys, glob

unittests = [name[2:-3] for name in glob.glob('./test_*.py')]
suite = unittest.defaultTestLoader.loadTestsFromNames(unittests)

#import doctest
#doctests = glob.glob('./doctest_*.txt')
#suite.addTest(doctest.DocFileSuite(*doctests))

def run():
    import bottle
    bottle.debug(True)
    result = unittest.TextTestRunner(verbosity=0).run(suite)
    sys.exit((result.errors or result.failures) and 1 or 0)

if __name__ == '__main__':
    run()

