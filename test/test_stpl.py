import unittest
from bottle import SimpleTemplate, TemplateError

class TestSimpleTemplate(unittest.TestCase):
    def test_string(self):
        """ Templates: Parse string"""
        t = SimpleTemplate('start {{var}} end').render(var='var')
        self.assertEqual('start var end', ''.join(t))

    def test_file(self):
        """ Templates: Parse file"""
        t = SimpleTemplate(filename='./views/stpl_simple.tpl').render(var='var')
        self.assertEqual('start var end\n', ''.join(t))

    def test_name(self):
        """ Templates: Lookup by name """
        t = SimpleTemplate(name='stpl_simple', lookup=['./views/']).render(var='var')
        self.assertEqual('start var end\n', ''.join(t))

    def test_data(self):
        """ Templates: Data representation """
        t = SimpleTemplate('<{{var}}>')
        self.assertEqual('<True>', ''.join(t.render(var=True)))
        self.assertEqual('<False>', ''.join(t.render(var=False)))
        self.assertEqual('<None>', ''.join(t.render(var=None)))
        self.assertEqual('<0>', ''.join(t.render(var=0)))
        self.assertEqual('<5>', ''.join(t.render(var=5)))
        self.assertEqual('<b>', ''.join(t.render(var='b')))
        self.assertEqual('<1.0>', ''.join(t.render(var=1.0)))
        self.assertEqual('<[1, 2]>', ''.join(t.render(var=[1,2])))

    def test_blocks(self):
        """ Templates: Code blocks and loops """
        t = SimpleTemplate("start\n%for i in l:\n{{i}} \n%end\nend")
        self.assertEqual('start\n1 \n2 \n3 \nend', ''.join(t.render(l=[1,2,3])))
        self.assertEqual('start\nend', ''.join(t.render(l=[])))
        t = SimpleTemplate("start\n%if i:\n{{i}} \n%end\nend")
        self.assertEqual('start\nTrue \nend', ''.join(t.render(i=True)))
        self.assertEqual('start\nend', ''.join(t.render(i=False)))

    def test_nobreak(self):
        """ Templates: Nobreak statements"""
        t = SimpleTemplate("start\\\\\n%pass\nend")
        self.assertEqual('startend', ''.join(t.render()))
        
    def test_nonobreak(self):
        """ Templates: Escaped nobreak statements"""
        t = SimpleTemplate("start\\\\\n\\\\\n%pass\nend")
        self.assertEqual('start\\\\\nend', ''.join(t.render()))

    def test_include(self):
        """ Templates: Include statements"""
        t = SimpleTemplate(name='stpl_include', lookup=['./views/'])
        self.assertEqual('before\nstart var end\nafter\n', ''.join(t.render(var='var')))

    def test_rebase(self):
        """ Templates: %rebase and method passing """
        t = SimpleTemplate(name='stpl_t2main', lookup=['./views/'])
        result='+base+\n+main+\n!1234!\n+include+\n-main-\n+include+\n-base-\n'
        self.assertEqual(result, ''.join(t.render(content='1234')))

    def test_notfound(self):
        """ Templates: Unavailable templates"""
        self.assertRaises(TemplateError, SimpleTemplate, name="abcdef")

    def test_error(self):
        """ Templates: Exceptions"""
        self.assertRaises(SyntaxError, SimpleTemplate, '%for badsyntax')
        self.assertRaises(IndexError, SimpleTemplate('{{i[5]}}').render, i=[0])


suite = unittest.TestSuite()
suite.addTest(unittest.makeSuite(TestSimpleTemplate))

if __name__ == '__main__':
    unittest.main()

