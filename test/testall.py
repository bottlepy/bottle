#!/usr/bin/python
# -*- coding: utf-8 -*-

import unittest
import sys, os, glob

test_root = os.path.dirname(os.path.abspath(__file__))
test_files = glob.glob(os.path.join(test_root, 'test_*.py'))

os.chdir(test_root)
sys.path.insert(0, os.path.dirname(test_root))
sys.path.insert(0, test_root)
test_names = [os.path.basename(name)[:-3] for name in test_files]

if 'help' in sys.argv or '-h' in sys.argv:
    print
    print "Command line arguments:"
    print
    print "fast: Skip server adapter tests."
    print "verbose: Print tests even if they pass."
    print "coverage: Measure code coverage."
    print "html: Create a html coverage report. Requires 'coverage'"
    print "clean: Delete coverage or temporary files"
    print
    sys.exit(0)


if 'fast' in sys.argv:
    print "Warning: The 'fast' keyword skipps server tests."
    test_names.remove('test_server')

cov = None
if 'coverage' in sys.argv:
    import coverage
    cov = coverage.coverage(data_suffix=True, branch=True)
    cov.start()

suite = unittest.defaultTestLoader.loadTestsFromNames(test_names)

#import doctest
#doctests = glob.glob('./doctest_*.txt')
#suite.addTest(doctest.DocFileSuite(*doctests))

def run():
    import bottle
    bottle.debug(True)
    vlevel = 2 if 'verbose' in sys.argv else 0
    result = unittest.TextTestRunner(verbosity=vlevel).run(suite)
    print

    if cov:
        cov.stop()
        cov.save()
        # Recreate coverage object so new files created in other processes are
        # recognized
        cnew = coverage.coverage(data_suffix=True, branch=True)
        cnew.combine()
        print "Coverage:"
        cnew.report(morfs=['bottle.py']+test_files, show_missing=False)
        if 'html' in sys.argv:
            print
            cnew.html_report(morfs=['bottle.py']+test_files, directory='../build/coverage')
            print "Coverage report is in %s" % \
                  os.path.abspath('../build/coverage/index.html')

    sys.exit((result.errors or result.failures) and 1 or 0)

if __name__ == '__main__':
    run()

