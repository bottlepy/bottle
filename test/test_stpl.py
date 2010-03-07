# -*- coding: utf-8 -*-
import unittest
from bottle import SimpleTemplate, TemplateError

class TestSimpleTemplate(unittest.TestCase):
    def test_string(self):
        """ Templates: Parse string"""
        t = SimpleTemplate('start {{var}} end').render(var='var')
        self.assertEqual(u'start var end', ''.join(t))

    def test_file(self):
        """ Templates: Parse file"""
        t = SimpleTemplate(name='./views/stpl_simple.tpl').render(var='var')
        self.assertEqual(u'start var end\n', ''.join(t))

    def test_name(self):
        """ Templates: Lookup by name """
        t = SimpleTemplate(name='stpl_simple', lookup=['./views/']).render(var='var')
        self.assertEqual(u'start var end\n', ''.join(t))

    def test_unicode(self):
        """ Templates: Unicode variables """
        t = SimpleTemplate('start {{var}} end').render(var=u'äöü')
        self.assertEqual(u'start äöü end', ''.join(t))

    def test_import(self):
        """ Templates: import statement"""
        t = '%from base64 import b64encode\nstart {{b64encode(var.encode("ascii") if hasattr(var, "encode") else var)}} end'
        t = SimpleTemplate(t).render(var='var')
        self.assertEqual(u'start dmFy end', ''.join(t))

    def test_data(self):
        """ Templates: Data representation """
        t = SimpleTemplate('<{{var}}>')
        self.assertEqual(u'<True>', ''.join(t.render(var=True)))
        self.assertEqual(u'<False>', ''.join(t.render(var=False)))
        self.assertEqual(u'<None>', ''.join(t.render(var=None)))
        self.assertEqual(u'<0>', ''.join(t.render(var=0)))
        self.assertEqual(u'<5>', ''.join(t.render(var=5)))
        self.assertEqual(u'<b>', ''.join(t.render(var='b')))
        self.assertEqual(u'<1.0>', ''.join(t.render(var=1.0)))
        self.assertEqual(u'<[1, 2]>', ''.join(t.render(var=[1,2])))

    def test_escape(self):
        t = SimpleTemplate('<{{!var}}>')
        self.assertEqual(u'<b>', ''.join(t.render(var='b')))
        self.assertEqual(u'<&lt;&amp;&gt;>', ''.join(t.render(var='<&>')))

    def test_blocks(self):
        """ Templates: Code blocks and loops """
        t = SimpleTemplate("start\n%for i in l:\n{{i}} \n%end\nend")
        self.assertEqual(u'start\n1 \n2 \n3 \nend', ''.join(t.render(l=[1,2,3])))
        self.assertEqual(u'start\nend', ''.join(t.render(l=[])))
        t = SimpleTemplate("start\n%if i:\n{{i}} \n%end\nend")
        self.assertEqual(u'start\nTrue \nend', ''.join(t.render(i=True)))
        self.assertEqual(u'start\nend', ''.join(t.render(i=False)))

    def test_onelineblocks(self):
        """ Templates: one line code blocks """
        t = SimpleTemplate("start\n%a=''\n%for i in l: a += str(i)\n{{a}}\nend")
        self.assertEqual(u'start\n123\nend', ''.join(t.render(l=[1,2,3])))
        self.assertEqual(u'start\n\nend', ''.join(t.render(l=[])))

    def test_nobreak(self):
        """ Templates: Nobreak statements"""
        t = SimpleTemplate("start\\\\\n%pass\nend")
        self.assertEqual(u'startend', ''.join(t.render()))
        
    def test_nonobreak(self):
        """ Templates: Escaped nobreak statements"""
        t = SimpleTemplate("start\\\\\n\\\\\n%pass\nend")
        self.assertEqual(u'start\\\\\nend', ''.join(t.render()))

    def test_include(self):
        """ Templates: Include statements"""
        t = SimpleTemplate(name='stpl_include', lookup=['./views/'])
        self.assertEqual(u'before\nstart var end\nafter\n', ''.join(t.render(var='var')))

    def test_rebase(self):
        """ Templates: %rebase and method passing """
        t = SimpleTemplate(name='stpl_t2main', lookup=['./views/'])
        result=u'+base+\n+main+\n!1234!\n+include+\n-main-\n+include+\n-base-\n'
        self.assertEqual(result, ''.join(t.render(content='1234')))

    def test_notfound(self):
        """ Templates: Unavailable templates"""
        self.assertRaises(TemplateError, SimpleTemplate, name="abcdef")

    def test_error(self):
        """ Templates: Exceptions"""
        self.assertRaises(SyntaxError, SimpleTemplate, '%for badsyntax')
        self.assertRaises(IndexError, SimpleTemplate('{{i[5]}}').render, i=[0])
    
    def test_winbreaks(self):
        """ Templates: Test windows line breaks """
        t = SimpleTemplate('%var+=1\r\n{{var}}\r\n')
        t = t.render(var=5)
        self.assertEqual(u'6\r\n', ''.join(t))

    def test_detect_encodung(self):
        t = SimpleTemplate(u'#coding: iso8859_15\nöäü?@€'.encode('utf8'))
        self.failIfEqual(u'# encoding removed: iso8859_15\nöäü?@€', ''.join(t.render()))
        t = SimpleTemplate(u'#coding: iso8859_15\nöäü?@€'.encode('iso8859_15'))
        self.assertEqual(u'# encoding removed: iso8859_15\nöäü?@€', ''.join(t.render()))

if __name__ == '__main__':
    unittest.main()

