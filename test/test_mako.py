import unittest
from bottle import MakoTemplate, mako_template, mako_view

class TestMakoTemplate(unittest.TestCase):
    def test_string(self):
        """ Templates: Mako string"""
        t = MakoTemplate('start ${var} end').render(var='var')
        self.assertEqual('start var end', t)

    def test_file(self):
        """ Templates: Mako file"""
        t = MakoTemplate(name='./views/mako_simple.tpl').render(var='var')
        self.assertEqual('start var end\n', t)

    def test_name(self):
        """ Templates: Mako lookup by name """
        t = MakoTemplate(name='mako_simple', lookup=['./views/']).render(var='var')
        self.assertEqual('start var end\n', t)

    def test_notfound(self):
        """ Templates: Unavailable templates"""
        self.assertRaises(Exception, MakoTemplate, name="abcdef")

    def test_error(self):
        """ Templates: Exceptions"""
        self.assertRaises(Exception, MakoTemplate, '%for badsyntax')

    def test_inherit(self):
        """ Templates: Mako lookup and inherience """
        t = MakoTemplate(name='mako_inherit', lookup=['./views/']).render(var='v')
        self.assertEqual('o\ncvc\no\n', t)
        t = MakoTemplate('<%inherit file="mako_base.tpl"/>\nc${var}c\n', lookup=['./views/']).render(var='v')
        self.assertEqual('o\ncvc\no\n', t)
        t = MakoTemplate('<%inherit file="views/mako_base.tpl"/>\nc${var}c\n', lookup=['./']).render(var='v')
        self.assertEqual('o\ncvc\no\n', t)

    def test_template_shortcut(self):
        result = mako_template('start ${var} end', var='middle')
        self.assertEqual(u'start middle end', result)

    def test_view_decorator(self):
        @mako_view('start ${var} end')
        def test():
            return dict(var='middle')
        self.assertEqual(u'start middle end', test())


try:
  import mako
except ImportError:
  print "WARNING: No Mako template support. Skipping tests."
  del TestMakoTemplate

if __name__ == '__main__': #pragma: no cover
    unittest.main()

