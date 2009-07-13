import unittest
import sys, os.path
TESTDIR = os.path.dirname(os.path.abspath(__file__))
DISTDIR = os.path.dirname(TESTDIR)
sys.path.insert(0, TESTDIR)
sys.path.insert(0, DISTDIR)

from test_templates import suite as suite1
from test_routes import suite as suite2

suite = unittest.TestSuite()
suite.addTest(suite1)
suite.addTest(suite2)

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite)

