from __future__ import with_statement
from glob import glob
from tools import chdir
import unittest
import sys, os

try:
    import coverage
    coverage.process_startup()
except ImportError:
    pass


if 'fast' in sys.argv:
    sys.stderr.write("Warning: The 'fast' keyword skipps server tests.\n")
    os.environ["TEST_FAST"] = "true"

suite = None
if sys.version_info[:2] in ((2,5), (2,6), (3,1)):
    with chdir(__file__):
        suite = unittest.defaultTestLoader.loadTestsFromNames([n[:-3] for n in glob('test_*.py')])
else:
    suite = unittest.defaultTestLoader.discover(__name__)

def main():
    import bottle
    bottle.debug(True)
    vlevel = 2 if 'verbose' in sys.argv else 0
    result = unittest.TextTestRunner(verbosity=vlevel).run(suite)
    sys.exit((result.errors or result.failures) and 1 or 0)

