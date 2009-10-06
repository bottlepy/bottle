import unittest
import sys, os.path
from bottle import SimpleTemplate, TemplateError

class TestSimpleTemplate(unittest.TestCase):
    pass

suite = unittest.TestSuite()
suite.addTest(unittest.makeSuite(TestSimpleTemplate))

if __name__ == '__main__':
    unittest.main()

