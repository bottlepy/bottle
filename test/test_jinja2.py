import unittest
from bottle import Jinja2Template

class TestJinja2Template(unittest.TestCase):
    def test_string(self):
        """ Templates: Jinja2 string"""
        t = Jinja2Template('start {{var}} end').render(var='var')
        self.assertEqual('start var end', ''.join(t))

    def test_file(self):
        """ Templates: Jinja2 file"""
        t = Jinja2Template(filename='./views/jinja2_simple.tpl').render(var='var')
        self.assertEqual('start var end', ''.join(t))

    def test_name(self):
        """ Templates: Jinja2 lookup by name """
        t = Jinja2Template(name='jinja2_simple', lookup=['./views/']).render(var='var')
        self.assertEqual('start var end', ''.join(t))

    def test_notfound(self):
        """ Templates: Unavailable templates"""
        self.assertRaises(Exception, Jinja2Template, name="abcdef")

    def test_error(self):
        """ Templates: Exceptions"""
        self.assertRaises(Exception, Jinja2Template, '{% for badsyntax')

    def test_inherit(self):
        """ Templates: Jinja2 lookup and inherience """
        t = Jinja2Template(name='jinja2_inherit', lookup=['./views/']).render()
        self.assertEqual('begin abc end', ''.join(t))

suite = unittest.TestSuite()
try:
  import jinja2; del jinja2
  suite.addTest(unittest.makeSuite(TestJinja2Template))
except ImportError:
  print "WARNING: No Jinja2 template support. Skipping tests."


if __name__ == '__main__':
    unittest.main()

