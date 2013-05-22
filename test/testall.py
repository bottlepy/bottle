#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
    import coverage
    coverage.process_startup()
except ImportError:
    pass

import unittest
import sys, os, glob

test_root = os.path.dirname(os.path.abspath(__file__))
test_files = glob.glob(os.path.join(test_root, 'test_*.py'))

os.chdir(test_root)
sys.path.insert(0, os.path.dirname(test_root))
sys.path.insert(0, test_root)
test_names = [os.path.basename(name)[:-3] for name in test_files]

if 'help' in sys.argv or '-h' in sys.argv:
    sys.stdout.write('''Command line arguments:
    fast: Skip server adapter tests.
    verbose: Print tests even if they pass.
    ''')
    sys.exit(0)

if 'fast' in sys.argv:
    sys.stderr.write("Warning: The 'fast' keyword skipps server tests.\n")
    test_names.remove('test_server')

suite = unittest.defaultTestLoader.loadTestsFromNames(test_names)

def run():
    import bottle

    bottle.debug(True)
    vlevel = 2 if 'verbose' in sys.argv else 0
    result = unittest.TextTestRunner(verbosity=vlevel).run(suite)

    sys.exit((result.errors or result.failures) and 1 or 0)

if __name__ == '__main__':
    run()

