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

    def test_unicode_code(self):
        """ Templates: utf8 code in file"""
        t = SimpleTemplate(name='./views/stpl_unicode.tpl').render(var='äöü')
        self.assertEqual(u'start ñç äöü end\n', ''.join(t))

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
        t = SimpleTemplate('<{{var}}>')
        self.assertEqual(u'<b>', ''.join(t.render(var='b')))
        self.assertEqual(u'<&lt;&amp;&gt;>', ''.join(t.render(var='<&>')))

    def test_noescape(self):
        t = SimpleTemplate('<{{!var}}>')
        self.assertEqual(u'<b>', ''.join(t.render(var='b')))
        self.assertEqual(u'<<&>>', ''.join(t.render(var='<&>')))

    def test_noescape_setting(self):
        t = SimpleTemplate('<{{var}}>', noescape=True)
        self.assertEqual(u'<b>', ''.join(t.render(var='b')))
        self.assertEqual(u'<<&>>', ''.join(t.render(var='<&>')))
        t = SimpleTemplate('<{{!var}}>', noescape=True)
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

    def test_elsebug(self):
        ''' Whirespace between block keyword and colon is allowed '''
        t = SimpleTemplate("%if 1:\nyes\n%else:\nno\n%end\n")
        self.assertEqual(u"yes\n", ''.join(t.render()))
        t = SimpleTemplate("%if 1:\nyes\n%else     :\nno\n%end\n")
        self.assertEqual(u"yes\n", ''.join(t.render()))

    def test_commentbug(self):
        ''' A "#" sign within an string is not a comment '''
        t = SimpleTemplate("%if '#':\nyes\n%end\n")
        self.assertEqual(u"yes\n", ''.join(t.render()))

    def test_multiline(self):
        ''' Block statements with non-terminating newlines '''
        t = SimpleTemplate("%if 1\\\n%and 1:\nyes\n%end\n")
        self.assertEqual(u"yes\n", ''.join(t.render()))

    def test_newline_in_parameterlist(self):
        ''' Block statements with non-terminating newlines in list '''
        t = SimpleTemplate("%a=[1,\n%2]\n{{len(a)}}")
        self.assertEqual(u"2", ''.join(t.render()))

    def test_dedentbug(self):
        ''' One-Line dednet blocks should not change indention '''
        t = SimpleTemplate('%if x: a="if"\n%else: a="else"\n{{a}}')
        self.assertEqual(u"if", ''.join(t.render(x=True)))
        self.assertEqual(u"else", ''.join(t.render(x=False)))
        t = SimpleTemplate('%if x:\n%a="if"\n%else: a="else"\n{{a}}')
        self.assertEqual(u"if", ''.join(t.render(x=True)))
        self.assertEqual(u"else", ''.join(t.render(x=False)))
        t = SimpleTemplate('%if x: a="if"\n%else: a="else"\n%end')
        self.assertRaises(NameError, t.render)

    def test_onelinebugs(self):
        ''' One-Line blocks should not change indention '''
        t = SimpleTemplate('%if x:\n%a=1\n%end\n{{a}}')
        self.assertEqual(u"1", ''.join(t.render(x=True)))
        t = SimpleTemplate('%if x: a=1\n{{a}}')
        self.assertEqual(u"1", ''.join(t.render(x=True)))
        t = SimpleTemplate('%if x:\n%a=1\n%else:\n%a=2\n%end\n{{a}}')
        self.assertEqual(u"1", ''.join(t.render(x=True)))
        self.assertEqual(u"2", ''.join(t.render(x=False)))
        t = SimpleTemplate('%if x:   a=1\n%else:\n%a=2\n%end\n{{a}}')
        self.assertEqual(u"1", ''.join(t.render(x=True)))
        self.assertEqual(u"2", ''.join(t.render(x=False)))
        t = SimpleTemplate('%if x:\n%a=1\n%else:   a=2\n{{a}}')
        self.assertEqual(u"1", ''.join(t.render(x=True)))
        self.assertEqual(u"2", ''.join(t.render(x=False)))
        t = SimpleTemplate('%if x:   a=1\n%else:   a=2\n{{a}}')
        self.assertEqual(u"1", ''.join(t.render(x=True)))
        self.assertEqual(u"2", ''.join(t.render(x=False)))

    def test_onelineblocks(self):
        """ Templates: one line code blocks """
        t = SimpleTemplate("start\n%a=''\n%for i in l: a += str(i)\n{{a}}\nend")
        self.assertEqual(u'start\n123\nend', ''.join(t.render(l=[1,2,3])))
        self.assertEqual(u'start\n\nend', ''.join(t.render(l=[])))

    def test_escaped_codelines(self):
        t = SimpleTemplate('%% test')
        self.assertEqual(u'% test', ''.join(t.render()))
        t = SimpleTemplate('%%% test')
        self.assertEqual(u'%% test', ''.join(t.render()))

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

    def test_commentonly(self):
        """ Templates: Commentd should behave like code-lines (e.g. flush text-lines) """
        t = SimpleTemplate('...\n%#test\n...')
        self.failIfEqual('#test', t.code.splitlines()[0])

    def test_detect_pep263(self):
        ''' PEP263 strings in code-lines change the template encoding on the fly '''
        t = SimpleTemplate(u'%#coding: iso8859_15\nöäü?@€'.encode('utf8'))
        self.failIfEqual(u'öäü?@€', ''.join(t.render()))
        self.assertEqual(t.encoding, 'iso8859_15')
        t = SimpleTemplate(u'%#coding: iso8859_15\nöäü?@€'.encode('iso8859_15'))
        self.assertEqual(u'öäü?@€', ''.join(t.render()))
        self.assertEqual(t.encoding, 'iso8859_15')
        self.assertEqual(2, len(t.code.splitlines()))

    def test_ignore_pep263_in_textline(self):
        ''' PEP263 strings in text-lines have no effect '''
        self.assertRaises(UnicodeError, SimpleTemplate, u'#coding: iso8859_15\nöäü?@€'.encode('iso8859_15'))
        t = SimpleTemplate(u'#coding: iso8859_15\nöäü?@€'.encode('utf8'))
        self.assertEqual(u'#coding: iso8859_15\nöäü?@€', ''.join(t.render()))
        self.assertEqual(t.encoding, 'utf8')

    def test_ignore_late_pep263(self):
        ''' PEP263 strings must appear within the first two lines '''
        self.assertRaises(UnicodeError, SimpleTemplate, u'\n\n%#coding: iso8859_15\nöäü?@€'.encode('iso8859_15'))
        t = SimpleTemplate(u'\n\n%#coding: iso8859_15\nöäü?@€'.encode('utf8'))
        self.assertEqual(u'\n\nöäü?@€', ''.join(t.render()))
        self.assertEqual(t.encoding, 'utf8')
        
if __name__ == '__main__':
    unittest.main()

