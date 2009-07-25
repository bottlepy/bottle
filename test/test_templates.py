import unittest
import sys, os.path
TESTDIR = os.path.dirname(os.path.abspath(__file__))
DISTDIR = os.path.dirname(TESTDIR)
sys.path.insert(0, TESTDIR)
sys.path.insert(0, DISTDIR)

from bottle import SimpleTemplate

class TestSimpleTemplate(unittest.TestCase):

    def test_inline(self):
        """ Templates: Inline statements """
        t = SimpleTemplate('start {{var}} end')
        self.assertEqual('start True end', t.render(var=True))
        self.assertEqual('start False end', t.render(var=False))
        self.assertEqual('start None end', t.render(var=None))
        self.assertEqual('start 0 end', t.render(var=0))
        self.assertEqual('start 5 end', t.render(var=5))
        self.assertEqual('start b end', t.render(var='b'))
        self.assertEqual('start 1.0 end', t.render(var=1.0))
        self.assertEqual('start [1, 2] end', t.render(var=[1,2]))

    def test_blocks(self):
        """ Templates: Code blocks and loops """
        t = SimpleTemplate("start\n%for i in l:\n{{i}} \n%end\nend")
        self.assertEqual('start\n1 \n2 \n3 \nend', t.render(l=[1,2,3]))
        self.assertEqual('start\nend', t.render(l=[]))

    def test_nobreak(self):
        """ Templates: Nobreak statements"""
        t = SimpleTemplate("start\\\\\n%pass\nend")
        self.assertEqual('startend', t.render())
        
    def test_nonobreak(self):
        """ Templates: Escaped nobreak statements"""
        t = SimpleTemplate("start\\\\\n\\\\\n%pass\nend")
        self.assertEqual('start\\\\\nend', t.render())

    def test_notfound(self):
        """ Templates: Unavailable templates"""
        self.assertEqual(None, SimpleTemplate.find("abcdef"))

    def test_error(self):
        """ Templates: Exceptions"""
        self.assertRaises(SyntaxError, SimpleTemplate, '%for badsyntax')
        self.assertRaises(IndexError, SimpleTemplate('{{i[5]}}').render, i=[0])

suite = unittest.TestSuite()
suite.addTest(unittest.makeSuite(TestSimpleTemplate))


if __name__ == '__main__':
    unittest.main()

