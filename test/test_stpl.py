# -*- coding: utf-8 -*-
import unittest
from bottle import SimpleTemplate, TemplateError, view, template

class TestSimpleTemplate(unittest.TestCase):
    def test_string(self):
        """ Templates: Parse string"""
        t = SimpleTemplate('start {{var}} end').render(var='var')
        self.assertEqual(u'start var end', t)
        t = SimpleTemplate('start {{self}} end').render({'self':'var'}) # "self" cannot be used as a kwarg
        self.assertEqual(u'start var end', t)

    def test_file(self):
        """ Templates: Parse file"""
        t = SimpleTemplate(name='./views/stpl_simple.tpl').render(var='var')
        self.assertEqual(u'start var end\n', t)

    def test_name(self):
        """ Templates: Lookup by name """
        t = SimpleTemplate(name='stpl_simple', lookup=['./views/']).render(var='var')
        self.assertEqual(u'start var end\n', t)

    def test_unicode(self):
        """ Templates: Unicode variables """
        t = SimpleTemplate('start {{var}} end').render(var=u'äöü')
        self.assertEqual(u'start äöü end', t)

    def test_unicode_code(self):
        """ Templates: utf8 code in file"""
        t = SimpleTemplate(name='./views/stpl_unicode.tpl').render(var='äöü')
        self.assertEqual(u'start ñç äöü end\n', t)

    def test_import(self):
        """ Templates: import statement"""
        t = '%from base64 import b64encode\nstart {{b64encode(var.encode("ascii") if hasattr(var, "encode") else var)}} end'
        t = SimpleTemplate(t).render(var='var')
        self.assertEqual(u'start dmFy end', t)

    def test_data(self):
        """ Templates: Data representation """
        t = SimpleTemplate('<{{var}}>')
        self.assertEqual(u'<True>', t.render(var=True))
        self.assertEqual(u'<False>', t.render(var=False))
        self.assertEqual(u'<None>', t.render(var=None))
        self.assertEqual(u'<0>', t.render(var=0))
        self.assertEqual(u'<5>', t.render(var=5))
        self.assertEqual(u'<b>', t.render(var='b'))
        self.assertEqual(u'<1.0>', t.render(var=1.0))
        self.assertEqual(u'<[1, 2]>', t.render(var=[1,2]))

    def test_escape(self):
        t = SimpleTemplate('<{{var}}>')
        self.assertEqual(u'<b>', t.render(var='b'))
        self.assertEqual(u'<&lt;&amp;&gt;>', t.render(var='<&>'))

    def test_noescape(self):
        t = SimpleTemplate('<{{!var}}>')
        self.assertEqual(u'<b>', t.render(var='b'))
        self.assertEqual(u'<<&>>', t.render(var='<&>'))

    def test_noescape_setting(self):
        t = SimpleTemplate('<{{var}}>', noescape=True)
        self.assertEqual(u'<b>', t.render(var='b'))
        self.assertEqual(u'<<&>>', t.render(var='<&>'))
        t = SimpleTemplate('<{{!var}}>', noescape=True)
        self.assertEqual(u'<b>', t.render(var='b'))
        self.assertEqual(u'<&lt;&amp;&gt;>', t.render(var='<&>'))

    def test_blocks(self):
        """ Templates: Code blocks and loops """
        t = SimpleTemplate("start\n%for i in l:\n{{i}} \n%end\nend")
        self.assertEqual(u'start\n1 \n2 \n3 \nend', t.render(l=[1,2,3]))
        self.assertEqual(u'start\nend', t.render(l=[]))
        t = SimpleTemplate("start\n%if i:\n{{i}} \n%end\nend")
        self.assertEqual(u'start\nTrue \nend', t.render(i=True))
        self.assertEqual(u'start\nend', t.render(i=False))

    def test_elsebug(self):
        ''' Whirespace between block keyword and colon is allowed '''
        t = SimpleTemplate("%if 1:\nyes\n%else:\nno\n%end\n")
        self.assertEqual(u"yes\n", t.render())
        t = SimpleTemplate("%if 1:\nyes\n%else     :\nno\n%end\n")
        self.assertEqual(u"yes\n", t.render())

    def test_commentbug(self):
        ''' A "#" sign within an string is not a comment '''
        t = SimpleTemplate("%if '#':\nyes\n%end\n")
        self.assertEqual(u"yes\n", t.render())

    def test_multiline(self):
        ''' Block statements with non-terminating newlines '''
        t = SimpleTemplate("%if 1\\\n%and 1:\nyes\n%end\n")
        self.assertEqual(u"yes\n", t.render())

    def test_newline_in_parameterlist(self):
        ''' Block statements with non-terminating newlines in list '''
        t = SimpleTemplate("%a=[1,\n%2]\n{{len(a)}}")
        self.assertEqual(u"2", t.render())

    def test_dedentbug(self):
        ''' One-Line dednet blocks should not change indention '''
        t = SimpleTemplate('%if x: a="if"\n%else: a="else"\n{{a}}')
        self.assertEqual(u"if", t.render(x=True))
        self.assertEqual(u"else", t.render(x=False))
        t = SimpleTemplate('%if x:\n%a="if"\n%else: a="else"\n{{a}}')
        self.assertEqual(u"if", t.render(x=True))
        self.assertEqual(u"else", t.render(x=False))
        t = SimpleTemplate('%if x: a="if"\n%else: a="else"\n%end')
        self.assertRaises(NameError, t.render)

    def test_onelinebugs(self):
        ''' One-Line blocks should not change indention '''
        t = SimpleTemplate('%if x:\n%a=1\n%end\n{{a}}')
        self.assertEqual(u"1", t.render(x=True))
        t = SimpleTemplate('%if x: a=1\n{{a}}')
        self.assertEqual(u"1", t.render(x=True))
        t = SimpleTemplate('%if x:\n%a=1\n%else:\n%a=2\n%end\n{{a}}')
        self.assertEqual(u"1", t.render(x=True))
        self.assertEqual(u"2", t.render(x=False))
        t = SimpleTemplate('%if x:   a=1\n%else:\n%a=2\n%end\n{{a}}')
        self.assertEqual(u"1", t.render(x=True))
        self.assertEqual(u"2", t.render(x=False))
        t = SimpleTemplate('%if x:\n%a=1\n%else:   a=2\n{{a}}')
        self.assertEqual(u"1", t.render(x=True))
        self.assertEqual(u"2", t.render(x=False))
        t = SimpleTemplate('%if x:   a=1\n%else:   a=2\n{{a}}')
        self.assertEqual(u"1", t.render(x=True))
        self.assertEqual(u"2", t.render(x=False))

    def test_onelineblocks(self):
        """ Templates: one line code blocks """
        t = SimpleTemplate("start\n%a=''\n%for i in l: a += str(i)\n{{a}}\nend")
        self.assertEqual(u'start\n123\nend', t.render(l=[1,2,3]))
        self.assertEqual(u'start\n\nend', t.render(l=[]))

    def test_escaped_codelines(self):
        t = SimpleTemplate('%% test')
        self.assertEqual(u'% test', t.render())
        t = SimpleTemplate('%%% test')
        self.assertEqual(u'%% test', t.render())

    def test_nobreak(self):
        """ Templates: Nobreak statements"""
        t = SimpleTemplate("start\\\\\n%pass\nend")
        self.assertEqual(u'startend', t.render())
        
    def test_nonobreak(self):
        """ Templates: Escaped nobreak statements"""
        t = SimpleTemplate("start\\\\\n\\\\\n%pass\nend")
        self.assertEqual(u'start\\\\\nend', t.render())

    def test_include(self):
        """ Templates: Include statements"""
        t = SimpleTemplate(name='stpl_include', lookup=['./views/'])
        self.assertEqual(u'before\nstart var end\nafter\n', t.render(var='var'))

    def test_rebase(self):
        """ Templates: %rebase and method passing """
        t = SimpleTemplate(name='stpl_t2main', lookup=['./views/'])
        result=u'+base+\n+main+\n!1234!\n+include+\n-main-\n+include+\n-base-\n'
        self.assertEqual(result, t.render(content='1234'))

    def test_get(self):
        t = SimpleTemplate(source='{{get("x", "default")}}')
        self.assertEqual('1234', t.render(x='1234'))
        self.assertEqual('default', t.render())

    def test_setdefault(self):
        t = SimpleTemplate(source='%setdefault("x", "default")\n{{x}}')
        self.assertEqual('1234', t.render(x='1234'))
        self.assertEqual('default', t.render())

    def test_defnied(self):
        t = SimpleTemplate(source='{{x if defined("x") else "no"}}')
        self.assertEqual('yes', t.render(x='yes'))
        self.assertEqual('no', t.render())

    def test_notfound(self):
        """ Templates: Unavailable templates"""
        self.assertRaises(TemplateError, SimpleTemplate, name="abcdef")

    def test_error(self):
        """ Templates: Exceptions"""
        self.assertRaises(SyntaxError, lambda: SimpleTemplate('%for badsyntax').co)
        self.assertRaises(IndexError, SimpleTemplate('{{i[5]}}').render, i=[0])
    
    def test_winbreaks(self):
        """ Templates: Test windows line breaks """
        t = SimpleTemplate('%var+=1\r\n{{var}}\r\n')
        t = t.render(var=5)
        self.assertEqual(u'6\r\n', t)

    def test_commentonly(self):
        """ Templates: Commentd should behave like code-lines (e.g. flush text-lines) """
        t = SimpleTemplate('...\n%#test\n...')
        self.failIfEqual('#test', t.code.splitlines()[0])

    def test_detect_pep263(self):
        ''' PEP263 strings in code-lines change the template encoding on the fly '''
        t = SimpleTemplate(u'%#coding: iso8859_15\nöäü?@€'.encode('utf8'))
        self.failIfEqual(u'öäü?@€', t.render())
        self.assertEqual(t.encoding, 'iso8859_15')
        t = SimpleTemplate(u'%#coding: iso8859_15\nöäü?@€'.encode('iso8859_15'))
        self.assertEqual(u'öäü?@€', t.render())
        self.assertEqual(t.encoding, 'iso8859_15')
        self.assertEqual(2, len(t.code.splitlines()))

    def test_ignore_pep263_in_textline(self):
        ''' PEP263 strings in text-lines have no effect '''
        self.assertRaises(UnicodeError, lambda: SimpleTemplate(u'#coding: iso8859_15\nöäü?@€'.encode('iso8859_15')).co)
        t = SimpleTemplate(u'#coding: iso8859_15\nöäü?@€'.encode('utf8'))
        self.assertEqual(u'#coding: iso8859_15\nöäü?@€', t.render())
        self.assertEqual(t.encoding, 'utf8')

    def test_ignore_late_pep263(self):
        ''' PEP263 strings must appear within the first two lines '''
        self.assertRaises(UnicodeError, lambda: SimpleTemplate(u'\n\n%#coding: iso8859_15\nöäü?@€'.encode('iso8859_15')).co)
        t = SimpleTemplate(u'\n\n%#coding: iso8859_15\nöäü?@€'.encode('utf8'))
        self.assertEqual(u'\n\nöäü?@€', t.render())
        self.assertEqual(t.encoding, 'utf8')

    def test_template_shortcut(self):
        result = template('start {{var}} end', var='middle')
        self.assertEqual(u'start middle end', result)

    def test_view_decorator(self):
        @view('start {{var}} end')
        def test():
            return dict(var='middle')
        self.assertEqual(u'start middle end', test())

    def test_global_config(self):
        SimpleTemplate.global_config('meh', 1)
        t = SimpleTemplate(u'anything')
        self.assertEqual(u'anything', t.render())

if __name__ == '__main__': #pragma: no cover
    unittest.main()

