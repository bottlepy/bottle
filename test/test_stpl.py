# -*- coding: utf-8 -*-
import unittest
from bottle import SimpleTemplate, TemplateError, view, template, touni, tob
import re
import traceback

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
        t = '%if x: a="if"\n%else: a="else"\n%end\n{{a}}'
        self.assertRenders(t, "if", x=True)
        self.assertRenders(t, "else", x=False)
        t = '%if x:\n%a="if"\n%else: a="else"\n%end\n{{a}}'
        self.assertRenders(t, "if", x=True)
        self.assertRenders(t, "else", x=False)
        t = SimpleTemplate('%if x: a="if"\n%else: a="else"\n%end')
        self.assertRaises(NameError, t.render)

    def test_onelinebugs(self):
        ''' One-Line blocks should not change indention '''
        t = '%if x:\n%a=1\n%end\n{{a}}'
        self.assertRenders(t, "1", x=True)
        t = '%if x: a=1; end\n{{a}}'
        self.assertRenders(t, "1", x=True)
        t = '%if x:\n%a=1\n%else:\n%a=2\n%end\n{{a}}'
        self.assertRenders(t, "1", x=True)
        self.assertRenders(t, "2", x=False)
        t = '%if x:   a=1\n%else:\n%a=2\n%end\n{{a}}'
        self.assertRenders(t, "1", x=True)
        self.assertRenders(t, "2", x=False)
        t = '%if x:\n%a=1\n%else:   a=2; end\n{{a}}'
        self.assertRenders(t, "1", x=True)
        self.assertRenders(t, "2", x=False)
        t = '%if x:   a=1\n%else:   a=2; end\n{{a}}'
        self.assertRenders(t, "1", x=True)
        self.assertRenders(t, "2", x=False)

    def test_onelineblocks(self):
        """ Templates: one line code blocks """
        t = "start\n%a=''\n%for i in l: a += str(i); end\n{{a}}\nend"
        self.assertRenders(t, 'start\n123\nend', l=[1,2,3])
        self.assertRenders(t, 'start\n\nend', l=[])

    def test_escaped_codelines(self):
        self.assertRenders('%% test', '% test')
        self.assertRenders('%%% test', '%% test')
        self.assertRenders('\\% test', '% test')
        self.assertRenders('\\%% test', '%% test')

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

    def test_winbreaks_end_bug(self):
        d = { 'test': [ 1, 2, 3 ] }
        self.assertRenders('%for i in test:\n{{i}}\n%end\n', '1\n2\n3\n', **d)
        self.assertRenders('%for i in test:\n{{i}}\r\n%end\n', '1\r\n2\r\n3\r\n', **d)
        self.assertRenders('%for i in test:\r\n{{i}}\n%end\r\n', '1\n2\n3\n', **d)
        self.assertRenders('%for i in test:\r\n{{i}}\r\n%end\r\n', '1\r\n2\r\n3\r\n', **d)

    def test_commentonly(self):
        """ Templates: Commentd should behave like code-lines (e.g. flush text-lines) """
        t = SimpleTemplate('...\n%#test\n...')
        self.assertNotEqual('#test', t.code.splitlines()[0])

    def test_detect_pep263(self):
        ''' PEP263 strings in code-lines change the template encoding on the fly '''
        t = SimpleTemplate(touni('%#coding: iso8859_15\nöäü?@€').encode('utf8'))
        self.assertNotEqual(touni('öäü?@€'), t.render())
        self.assertEqual(t.encoding, 'iso8859_15')
        t = SimpleTemplate(touni('%#coding: iso8859_15\nöäü?@€').encode('iso8859_15'))
        self.assertEqual(touni('öäü?@€'), t.render())
        self.assertEqual(t.encoding, 'iso8859_15')
        self.assertEqual(2, len(t.code.splitlines()))

    def test_ignore_pep263_in_textline(self):
        ''' PEP263 strings in text-lines have no effect '''
        t = SimpleTemplate(touni('#coding: iso8859_15\nöäü?@€').encode('utf8'))
        self.assertEqual(touni('#coding: iso8859_15\nöäü?@€'), t.render())
        self.assertEqual(t.encoding, 'utf8')

    def test_ignore_late_pep263(self):
        ''' PEP263 strings must appear within the first two lines '''
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

    def test_view_decorator_issue_407(self):
        @view('stpl_no_vars')
        def test():
            pass
        self.assertEqual(touni('hihi'), test())
        @view('aaa {{x}}', x='bbb')
        def test2():
            pass
        self.assertEqual(touni('aaa bbb'), test2())

    def test_global_config(self):
        SimpleTemplate.global_config('meh', 1)
        t = SimpleTemplate('anything')
        self.assertEqual(touni('anything'), t.render())

    def test_bug_no_whitespace_before_stmt(self):
        self.assertRenders('\n{{var}}', '\nx', var='x')


class TestSTPLDir(unittest.TestCase):
    def fix_ident(self, string):
        lines = string.splitlines(True)
        if not lines: return string
        if not lines[0].strip(): lines.pop(0)
        whitespace = re.match('([ \t]*)', lines[0]).group(0)
        if not whitespace: return string
        for i in range(len(lines)):
            lines[i] = lines[i][len(whitespace):]
        return lines[0][:0].join(lines)

    def assertRenders(self, source, result, syntax=None, *args, **vars):
        source = self.fix_ident(source)
        result = self.fix_ident(result)
        tpl = SimpleTemplate(source, syntax=syntax)
        try:
            tpl.co
            self.assertEqual(touni(result), tpl.render(*args, **vars))
        except SyntaxError:
            self.fail('Syntax error in template:\n%s\n\nTemplate code:\n##########\n%s\n##########' %
                     (traceback.format_exc(), tpl.code))

    def test_old_include(self):
        t1 = SimpleTemplate('%include foo')
        t1.cache['foo'] = SimpleTemplate('foo')
        self.assertEqual(t1.render(), 'foo')

    def test_old_include_with_args(self):
        t1 = SimpleTemplate('%include foo x=y')
        t1.cache['foo'] = SimpleTemplate('foo{{x}}')
        self.assertEqual(t1.render(y='bar'), 'foobar')

    def test_defect_coding(self):
        t1 = SimpleTemplate('%#coding comment\nfoo{{y}}')
        self.assertEqual(t1.render(y='bar'), 'foobar')

    def test_multiline_block(self):
        source = '''
            <% a = 5
            b = 6
            c = 7 %>
            {{a+b+c}}
        '''; result = '''
            18
        '''
        self.assertRenders(source, result)

    def test_multiline_ignore_eob_in_string(self):
        source = '''
            <% x=5 # a comment
               y = '%>' # a string
               # this is still code
               # lets end this %>
            {{x}}{{!y}}
        '''; result = '''
            5%>
        '''
        self.assertRenders(source, result)

    def test_multiline_find_eob_in_comments(self):
        source = '''
            <% # a comment
               # %> ignore because not end of line
               # this is still code
               x=5
               # lets end this here %>
            {{x}}
        '''; result = '''
            5
        '''
        self.assertRenders(source, result)

    def test_multiline_indention(self):
        source = '''
            <%   if True:
                   a = 2
                     else:
                       a = 0
                         end
            %>
            {{a}}
        '''; result = '''
            2
        '''
        self.assertRenders(source, result)

    def test_multiline_eob_after_end(self):
        source = '''
            <%   if True:
                   a = 2
                 end %>
            {{a}}
        '''; result = '''
            2
        '''
        self.assertRenders(source, result)

    def test_multiline_eob_in_single_line_code(self):
        # eob must be a valid python expression to allow this test.
        source = '''
            cline eob=5; eob
            xxx
        '''; result = '''
            xxx
        '''
        self.assertRenders(source, result, syntax='sob eob cline foo bar')

    def test_multiline_strings_in_code_line(self):
        source = '''
            % a = """line 1
                  line 2"""
            {{a}}
        '''; result = '''
            line 1
                  line 2
        '''
        self.assertRenders(source, result)

if __name__ == '__main__': #pragma: no cover
    unittest.main()

