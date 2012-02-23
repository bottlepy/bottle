# -*- coding: utf-8 -*-
import unittest
from bottle import SimpleTemplate, TemplateError, view, template, touni, tob

class TestSimpleTemplate(unittest.TestCase):
    def assertRenders(self, tpl, to, *args, **vars):
        if isinstance(tpl, str):
            tpl = SimpleTemplate(tpl)
        self.assertEqual(touni(to), tpl.render(*args, **vars))

    def test_string(self):
        """ Templates: Parse string"""
        self.assertRenders('start {{var}} end', 'start var end', var='var')
    
    def test_self_as_variable_name(self):
        self.assertRenders('start {{self}} end', 'start var end', {'self':'var'})

    def test_file(self):
        t = SimpleTemplate(name='./views/stpl_simple.tpl')
        self.assertRenders(t, 'start var end\n', var='var')

    def test_name(self):
        t = SimpleTemplate(name='stpl_simple', lookup=['./views/'])
        self.assertRenders(t, 'start var end\n', var='var')

    def test_unicode(self):
        self.assertRenders('start {{var}} end', 'start äöü end', var=touni('äöü'))
        self.assertRenders('start {{var}} end', 'start äöü end', var=tob('äöü'))

    def test_unicode_code(self):
        """ Templates: utf8 code in file"""
        t = SimpleTemplate(name='./views/stpl_unicode.tpl')
        self.assertRenders(t, 'start ñç äöü end\n', var=touni('äöü'))

    def test_import(self):
        """ Templates: import statement"""
        t = '%from base64 import b64encode\nstart {{b64encode(var.encode("ascii") if hasattr(var, "encode") else var)}} end'
        self.assertRenders(t, 'start dmFy end', var='var')

    def test_data(self):
        """ Templates: Data representation """
        t = SimpleTemplate('<{{var}}>')
        self.assertRenders('<{{var}}>', '<True>', var=True)
        self.assertRenders('<{{var}}>', '<False>', var=False)
        self.assertRenders('<{{var}}>', '<None>', var=None)
        self.assertRenders('<{{var}}>', '<0>', var=0)
        self.assertRenders('<{{var}}>', '<5>', var=5)
        self.assertRenders('<{{var}}>', '<b>', var=tob('b'))
        self.assertRenders('<{{var}}>', '<1.0>', var=1.0)
        self.assertRenders('<{{var}}>', '<[1, 2]>', var=[1,2])

    def test_escape(self):
        self.assertRenders('<{{var}}>', '<b>', var='b')
        self.assertRenders('<{{var}}>', '<&lt;&amp;&gt;>',var='<&>')

    def test_noescape(self):
        self.assertRenders('<{{!var}}>', '<b>',   var='b')
        self.assertRenders('<{{!var}}>', '<<&>>', var='<&>')

    def test_noescape_setting(self):
        t = SimpleTemplate('<{{var}}>', noescape=True)
        self.assertRenders(t, '<b>', var='b')
        self.assertRenders(t, '<<&>>', var='<&>')
        t = SimpleTemplate('<{{!var}}>', noescape=True)
        self.assertRenders(t, '<b>', var='b')
        self.assertRenders(t, '<&lt;&amp;&gt;>', var='<&>')

    def test_blocks(self):
        """ Templates: Code blocks and loops """
        t = "start\n%for i in l:\n{{i}} \n%end\nend"
        self.assertRenders(t, 'start\n1 \n2 \n3 \nend', l=[1,2,3])
        self.assertRenders(t, 'start\nend', l=[])
        t = "start\n%if i:\n{{i}} \n%end\nend"
        self.assertRenders(t, 'start\nTrue \nend', i=True)
        self.assertRenders(t, 'start\nend', i=False)

    def test_elsebug(self):
        ''' Whirespace between block keyword and colon is allowed '''
        self.assertRenders("%if 1:\nyes\n%else:\nno\n%end\n", "yes\n")
        self.assertRenders("%if 1:\nyes\n%else     :\nno\n%end\n", "yes\n")

    def test_commentbug(self):
        ''' A "#" sign within an string is not a comment '''
        self.assertRenders("%if '#':\nyes\n%end\n", "yes\n")

    def test_multiline(self):
        ''' Block statements with non-terminating newlines '''
        self.assertRenders("%if 1\\\n%and 1:\nyes\n%end\n", "yes\n")

    def test_newline_in_parameterlist(self):
        ''' Block statements with non-terminating newlines in list '''
        self.assertRenders("%a=[1,\n%2]\n{{len(a)}}", "2")

    def test_dedentbug(self):
        ''' One-Line dednet blocks should not change indention '''
        t = '%if x: a="if"\n%else: a="else"\n{{a}}'
        self.assertRenders(t, "if", x=True)
        self.assertRenders(t, "else", x=False)
        t = '%if x:\n%a="if"\n%else: a="else"\n{{a}}'
        self.assertRenders(t, "if", x=True)
        self.assertRenders(t, "else", x=False)
        t = SimpleTemplate('%if x: a="if"\n%else: a="else"\n%end')
        self.assertRaises(NameError, t.render)

    def test_onelinebugs(self):
        ''' One-Line blocks should not change indention '''
        t = '%if x:\n%a=1\n%end\n{{a}}'
        self.assertRenders(t, "1", x=True)
        t = '%if x: a=1\n{{a}}'
        self.assertRenders(t, "1", x=True)
        t = '%if x:\n%a=1\n%else:\n%a=2\n%end\n{{a}}'
        self.assertRenders(t, "1", x=True)
        self.assertRenders(t, "2", x=False)
        t = '%if x:   a=1\n%else:\n%a=2\n%end\n{{a}}'
        self.assertRenders(t, "1", x=True)
        self.assertRenders(t, "2", x=False)
        t = '%if x:\n%a=1\n%else:   a=2\n{{a}}'
        self.assertRenders(t, "1", x=True)
        self.assertRenders(t, "2", x=False)
        t = '%if x:   a=1\n%else:   a=2\n{{a}}'
        self.assertRenders(t, "1", x=True)
        self.assertRenders(t, "2", x=False)

    def test_onelineblocks(self):
        """ Templates: one line code blocks """
        t = "start\n%a=''\n%for i in l: a += str(i)\n{{a}}\nend"
        self.assertRenders(t, 'start\n123\nend', l=[1,2,3])
        self.assertRenders(t, 'start\n\nend', l=[])

    def test_escaped_codelines(self):
        self.assertRenders('%% test', '% test')
        self.assertRenders('%%% test', '%% test')

    def test_nobreak(self):
        """ Templates: Nobreak statements"""
        self.assertRenders("start\\\\\n%pass\nend", 'startend')
        
    def test_nonobreak(self):
        """ Templates: Escaped nobreak statements"""
        self.assertRenders("start\\\\\n\\\\\n%pass\nend", 'start\\\\\nend')

    def test_include(self):
        """ Templates: Include statements"""
        t = SimpleTemplate(name='stpl_include', lookup=['./views/'])
        self.assertRenders(t, 'before\nstart var end\nafter\n', var='var')

    def test_rebase(self):
        """ Templates: %rebase and method passing """
        t = SimpleTemplate(name='stpl_t2main', lookup=['./views/'])
        result='+base+\n+main+\n!1234!\n+include+\n-main-\n+include+\n-base-\n'
        self.assertRenders(t, result, content='1234')

    def test_get(self):
        self.assertRenders('{{get("x", "default")}}', '1234', x='1234')
        self.assertRenders('{{get("x", "default")}}', 'default')

    def test_setdefault(self):
        t = '%setdefault("x", "default")\n{{x}}'
        self.assertRenders(t, '1234', x='1234')
        self.assertRenders(t, 'default')

    def test_defnied(self):
        self.assertRenders('{{x if defined("x") else "no"}}', 'yes', x='yes')
        self.assertRenders('{{x if defined("x") else "no"}}', 'no')

    def test_notfound(self):
        """ Templates: Unavailable templates"""
        self.assertRaises(TemplateError, SimpleTemplate, name="abcdef")

    def test_error(self):
        """ Templates: Exceptions"""
        self.assertRaises(SyntaxError, lambda: SimpleTemplate('%for badsyntax').co)
        self.assertRaises(IndexError, SimpleTemplate('{{i[5]}}').render, i=[0])
    
    def test_winbreaks(self):
        """ Templates: Test windows line breaks """
        self.assertRenders('%var+=1\r\n{{var}}\r\n', '6\r\n', var=5)

    def test_commentonly(self):
        """ Templates: Commentd should behave like code-lines (e.g. flush text-lines) """
        t = SimpleTemplate('...\n%#test\n...')
        self.failIfEqual('#test', t.code.splitlines()[0])

    def test_detect_pep263(self):
        ''' PEP263 strings in code-lines change the template encoding on the fly '''
        t = SimpleTemplate(touni('%#coding: iso8859_15\nöäü?@€').encode('utf8'))
        self.failIfEqual(touni('öäü?@€'), t.render())
        self.assertEqual(t.encoding, 'iso8859_15')
        t = SimpleTemplate(touni('%#coding: iso8859_15\nöäü?@€').encode('iso8859_15'))
        self.assertEqual(touni('öäü?@€'), t.render())
        self.assertEqual(t.encoding, 'iso8859_15')
        self.assertEqual(2, len(t.code.splitlines()))

    def test_ignore_pep263_in_textline(self):
        ''' PEP263 strings in text-lines have no effect '''
        self.assertRaises(UnicodeError, lambda: SimpleTemplate(touni('#coding: iso8859_15\nöäü?@€').encode('iso8859_15')).co)
        t = SimpleTemplate(touni('#coding: iso8859_15\nöäü?@€').encode('utf8'))
        self.assertEqual(touni('#coding: iso8859_15\nöäü?@€'), t.render())
        self.assertEqual(t.encoding, 'utf8')

    def test_ignore_late_pep263(self):
        ''' PEP263 strings must appear within the first two lines '''
        self.assertRaises(UnicodeError, lambda: SimpleTemplate(touni('\n\n%#coding: iso8859_15\nöäü?@€').encode('iso8859_15')).co)
        t = SimpleTemplate(touni('\n\n%#coding: iso8859_15\nöäü?@€').encode('utf8'))
        self.assertEqual(touni('\n\nöäü?@€'), t.render())
        self.assertEqual(t.encoding, 'utf8')

    def test_coding_stress(self):
        self.assertRenders('%a=1\n%coding=a\nok', 'ok')
        self.assertRenders('a %coding:b', 'a %coding:b')
        self.assertRenders(' % #coding:utf-8', '')

    def test_template_shortcut(self):
        result = template('start {{var}} end', var='middle')
        self.assertEqual(touni('start middle end'), result)

    def test_view_decorator(self):
        @view('start {{var}} end')
        def test():
            return dict(var='middle')
        self.assertEqual(touni('start middle end'), test())

    def test_global_config(self):
        SimpleTemplate.global_config('meh', 1)
        t = SimpleTemplate('anything')
        self.assertEqual(touni('anything'), t.render())

if __name__ == '__main__': #pragma: no cover
    unittest.main()

