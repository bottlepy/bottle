import unittest
import sys, os.path
from bottle import SimpleTemplate, MakoTemplate, TemplateError
import bottle

try:
  import mako
except ImportError:
  MakoTemplate = False # No python3 support for Mako

class TestSimpleTemplate(unittest.TestCase):

    def test_inline(self):
        """ Templates: Inline statements """
        t = SimpleTemplate('start {{var}} end')
        self.assertEqual('start True end', ''.join(t.render(var=True)))
        self.assertEqual('start False end', ''.join(t.render(var=False)))
        self.assertEqual('start None end', ''.join(t.render(var=None)))
        self.assertEqual('start 0 end', ''.join(t.render(var=0)))
        self.assertEqual('start 5 end', ''.join(t.render(var=5)))
        self.assertEqual('start b end', ''.join(t.render(var='b')))
        self.assertEqual('start 1.0 end', ''.join(t.render(var=1.0)))
        self.assertEqual('start [1, 2] end', ''.join(t.render(var=[1,2])))

    def test_blocks(self):
        """ Templates: Code blocks and loops """
        t = SimpleTemplate("start\n%for i in l:\n{{i}} \n%end\nend")
        self.assertEqual('start\n1 \n2 \n3 \nend', ''.join(t.render(l=[1,2,3])))
        self.assertEqual('start\nend', ''.join(t.render(l=[])))

    def test_nobreak(self):
        """ Templates: Nobreak statements"""
        t = SimpleTemplate("start\\\\\n%pass\nend")
        self.assertEqual('startend', ''.join(t.render()))
        
    def test_nonobreak(self):
        """ Templates: Escaped nobreak statements"""
        t = SimpleTemplate("start\\\\\n\\\\\n%pass\nend")
        self.assertEqual('start\\\\\nend', ''.join(t.render()))

    def test_notfound(self):
        """ Templates: Unavailable templates"""
        self.assertRaises(TemplateError, SimpleTemplate, name="abcdef")

    def test_error(self):
        """ Templates: Exceptions"""
        self.assertRaises(SyntaxError, SimpleTemplate, '%for badsyntax')
        self.assertRaises(IndexError, SimpleTemplate('{{i[5]}}').render, i=[0])


class TestMakoTemplate(unittest.TestCase):

    def test_inline(self):
        """ Templates: Inline Mako statements """
        t = bottle.MakoTemplate('start ${var} end').render(var='var')
        self.assertEqual('start var end', ''.join(t))
        t = bottle.mako_template('start ${var} end', var='var')
        self.assertEqual('start var end', ''.join(t))

    def test_lookup(self):
        """ Templates: test mako lookup """
        t = MakoTemplate(name='mako_inherit', lookup='./').render(var='v')
        self.assertEqual('o\ncvc\no\n', ''.join(t))
        t = bottle.mako_template('mako_inherit', var='v')
        self.assertEqual('o\ncvc\no\n', ''.join(t))

    def test_notfound(self):
        """ Templates: Unavailable templates"""
        self.assertRaises(TemplateError, MakoTemplate, name="abcdef")

    def test_error(self):
        """ Templates: Exceptions"""
        self.assertRaises(Exception, MakoTemplate, '%for badsyntax')

suite = unittest.TestSuite()
suite.addTest(unittest.makeSuite(TestSimpleTemplate))
if MakoTemplate:
  suite.addTest(unittest.makeSuite(TestMakoTemplate))

if __name__ == '__main__':
    unittest.main()

