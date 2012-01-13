# -*- coding: utf-8 -*-
import unittest
from bottle import ShpamlTemplate, TemplateError, shpaml_template, shpaml_view

class TestShpamlTemplate(unittest.TestCase):
    def test_string(self):
        """ Templates: Shpaml string"""
        t = ShpamlTemplate('a\n  b | {{var}}').render(var='var')
        self.assertEqual(u'<a>\n  <b>var</b>\n</a>\n',t)

    def test_file(self):
        """ Templates: Shpaml file"""
        t = ShpamlTemplate(name='./views/shpaml_simple.tpl').render(var='var')
        self.assertEqual(u'<a>\n  <b>var</b>\n</a>\n',t)

    def test_name(self):
        """ Templates: Shpaml lookup by name """
        t = ShpamlTemplate(name='shpaml_simple', lookup=['./views/']).render(var='var')
        self.assertEqual(u'<a>\n  <b>var</b>\n</a>\n',t)

    def test_unicode(self):
        """ Templates: Unicode variables """
        t = ShpamlTemplate('a\n  b | {{var}}').render(var='äöü')
        self.assertEqual(u'<a>\n  <b>äöü</b>\n</a>\n',t)

    def test_unicode_code(self):
        """ Templates: utf8 code in file"""
        t = ShpamlTemplate(name='./views/shpaml_unicode.tpl').render(var='äöü')
        self.assertEqual(u'<a>\n  <b>ñç äöü</b>\n</a>\n',t)

    def test_import(self):
        """ Templates: import statement"""
        t = '%from base64 import b64encode\na\n  b | {{b64encode(var.encode("ascii") if hasattr(var, "encode") else var)}}'
        t = ShpamlTemplate(t).render(var='var')
        self.assertEqual(u'<a>\n  <b>dmFy</b>\n</a>\n',t)

    def test_data(self):
        """ Templates: Data representation """
        t = ShpamlTemplate('.data | {{var}}')
        self.assertEqual(u'<div class="data">True</div>\n', t.render(var=True))
        self.assertEqual(u'<div class="data">False</div>\n', t.render(var=False))
        self.assertEqual(u'<div class="data">None</div>\n', t.render(var=None))
        self.assertEqual(u'<div class="data">0</div>\n', t.render(var=0))
        self.assertEqual(u'<div class="data">5</div>\n', t.render(var=5))
        self.assertEqual(u'<div class="data">b</div>\n', t.render(var='b'))
        self.assertEqual(u'<div class="data">1.0</div>\n', t.render(var=1.0))
        self.assertEqual(u'<div class="data">[1, 2]</div>\n', t.render(var=[1,2]))

    def test_escape(self):
        t = ShpamlTemplate('.data | {{var}}')
        self.assertEqual(u'<div class="data">b</div>\n', t.render(var='b'))
        self.assertEqual(u'<div class="data">&lt;&amp;&gt;</div>\n', t.render(var='<&>'))

    def test_noescape(self):
        t = ShpamlTemplate('.data | {{!var}}')
        self.assertEqual(u'<div class="data">b</div>\n', t.render(var='b'))
        self.assertEqual(u'<div class="data"><&></div>\n', t.render(var='<&>'))

    def test_noescape_setting(self):
        t = ShpamlTemplate('.data | {{var}}', noescape=True)
        self.assertEqual(u'<div class="data">b</div>\n', t.render(var='b'))
        self.assertEqual(u'<div class="data"><&></div>\n', t.render(var='<&>'))
        t = ShpamlTemplate('.data | {{!var}}', noescape=True)
        self.assertEqual(u'<div class="data">b</div>\n', t.render(var='b'))
        self.assertEqual(u'<div class="data">&lt;&amp;&gt;</div>\n', t.render(var='<&>'))

    def test_blocks(self):
        """ Templates: Code blocks and loops """
        t = ShpamlTemplate('ul.list\n  %for i in l:\n    li | {{i}}\n  %end');
        self.assertEqual(u'<ul class="list">\n    <li>1</li>\n    <li>2</li>\n    <li>3</li>\n</ul>\n', t.render(l=[1,2,3]))
        self.assertEqual(u'<ul class="list">\n</ul>\n', t.render(l=[]))
        t = ShpamlTemplate('.condition\n  %if i:\n    {{i}}\n  %end');
        self.assertEqual(u'<div class="condition">\n    True\n</div>\n', t.render(i=True))
        self.assertEqual(u'<div class="condition">\n</div>\n', t.render(i=False))

    def test_elsebug(self):
        ''' Whitespace between block keyword and colon is allowed '''
        t = ShpamlTemplate("%if 1:\nyes\n%else:\nno\n%end\n")
        self.assertEqual(u"yes\n", t.render())
        t = ShpamlTemplate("%if 1:\nyes\n%else     :\nno\n%end\n")
        self.assertEqual(u"yes\n", t.render())

    def test_commentbug(self):
        ''' A "#" sign within an string is not a comment '''
        t = ShpamlTemplate("%if '#':\nyes\n%end\n")
        self.assertEqual(u"yes\n", t.render())

    def test_multiline(self):
        ''' Block statements with non-terminating newlines '''
        t = ShpamlTemplate("%if 1\\\n%and 1:\nyes\n%end\n")
        self.assertEqual(u"yes\n", t.render())

    def test_newline_in_parameterlist(self):
        ''' Block statements with non-terminating newlines in list '''
        t = ShpamlTemplate("%a=[1,\n%2]\n{{len(a)}}")
        self.assertEqual(u"2\n", t.render())

    def test_dedentbug(self):
        ''' One-Line dednet blocks should not change indention '''
        t = ShpamlTemplate('%if x: a="if"\n%else: a="else"\n{{a}}')
        self.assertEqual(u"if\n", t.render(x=True))
        self.assertEqual(u"else\n", t.render(x=False))
        t = ShpamlTemplate('%if x:\n%a="if"\n%else: a="else"\n{{a}}')
        self.assertEqual(u"if\n", t.render(x=True))
        self.assertEqual(u"else\n", t.render(x=False))
        t = ShpamlTemplate('%if x: a="if"\n%else: a="else"\n%end')
        self.assertRaises(NameError, t.render)

    def test_onelinebugs(self):
        ''' One-Line blocks should not change indention '''
        t = ShpamlTemplate('%if x:\n%a=1\n%end\n{{a}}')
        self.assertEqual(u"1\n", t.render(x=True))
        t = ShpamlTemplate('%if x: a=1\n{{a}}')
        self.assertEqual(u"1\n", t.render(x=True))
        t = ShpamlTemplate('%if x:\n%a=1\n%else:\n%a=2\n%end\n{{a}}')
        self.assertEqual(u"1\n", t.render(x=True))
        self.assertEqual(u"2\n", t.render(x=False))
        t = ShpamlTemplate('%if x:   a=1\n%else:\n%a=2\n%end\n{{a}}')
        self.assertEqual(u"1\n", t.render(x=True))
        self.assertEqual(u"2\n", t.render(x=False))
        t = ShpamlTemplate('%if x:\n%a=1\n%else:   a=2\n{{a}}')
        self.assertEqual(u"1\n", t.render(x=True))
        self.assertEqual(u"2\n", t.render(x=False))
        t = ShpamlTemplate('%if x:   a=1\n%else:   a=2\n{{a}}')
        self.assertEqual(u"1\n", t.render(x=True))
        self.assertEqual(u"2\n", t.render(x=False))

    def test_onelineblocks(self):
        """ Templates: one line code blocks """
        t = ShpamlTemplate("start\n%a=''\n%for i in l: a += str(i)\n{{a}}\nend")
        self.assertEqual(u'start\n123\nend\n', t.render(l=[1,2,3]))
        self.assertEqual(u'start\n\nend\n', t.render(l=[]))

    def test_escaped_codelines(self):
        t = ShpamlTemplate('%% test')
        self.assertEqual(u'% test\n', t.render())
        t = ShpamlTemplate('%%% test')
        self.assertEqual(u'%% test\n', t.render())

    def test_nobreak(self):
        """ Templates: Nobreak statements"""
        t = ShpamlTemplate("start\\\\\n%pass\nend")
        self.assertEqual(u'startend\n', t.render())
        
    def test_nonobreak(self):
        """ Templates: Escaped nobreak statements"""
        t = ShpamlTemplate("start\\\\\n\\\\\n%pass\nend")
        self.assertEqual(u'start\\\\\nend\n', t.render())

    def test_include(self):
        """ Templates: Include statements"""
        t = ShpamlTemplate(name='shpaml_include', lookup=['./views/'])
        self.assertEqual(u'<wrap>\n<a>\n  <b>var</b>\n</a>\n</wrap>\n',t.render(var='var'))

    def test_simple_rebase(self):
        t = ShpamlTemplate('.child | {{var}}\n%rebase shpaml_simple_rebase title="rebase"', lookup=['./views/'])
        result = u"""\
<div class="wrap">
  <div class="title">rebase</div>
  <div class="content">
<div class="child">var</div>
  </div>
</div>
"""
        self.assertEqual(result,t.render(var='var'))

    def test_rebase(self):
        """ Templates: %rebase and method passing """
        t = ShpamlTemplate(name='shpaml_t2main', lookup=['./views/'])
        result=u'+base+\n+main+\n!1234!\n+include+\n-main-\n+include+\n-base-\n'
        self.assertEqual(result, t.render(content='1234'))

    def test_notfound(self):
        """ Templates: Unavailable templates"""
        self.assertRaises(TemplateError, ShpamlTemplate, name="abcdef")

    def test_error(self):
        """ Templates: Exceptions"""
        self.assertRaises(SyntaxError, lambda: ShpamlTemplate('%for badsyntax').co)
        self.assertRaises(IndexError, ShpamlTemplate('{{i[5]}}').render, i=[0])
    
    def test_winbreaks(self):
        """ Templates: Test windows line breaks """
        t = ShpamlTemplate('%var+=1\r\n{{var}}\r\n')
        t = t.render(var=5)
        self.assertEqual(u'6\n', t)

    def test_commentonly(self):
        """ Templates: Comments should behave like code-lines (e.g. flush text-lines) """
        t = ShpamlTemplate('...\n%#test\n...')
        self.failIfEqual('#test', t.code.splitlines()[0])

    def test_detect_pep263(self):
        ''' PEP263 strings in code-lines change the template encoding on the fly '''
        t = ShpamlTemplate(u'%#coding: iso8859_15\nöäü?@€'.encode('utf8'))
        self.failIfEqual(u'öäü?@€', t.render())
        self.assertEqual(t.encoding, 'iso8859_15')
        t = ShpamlTemplate(u'%#coding: iso8859_15\nöäü?@€'.encode('iso8859_15'))
        self.assertEqual(u'öäü?@€\n', t.render())
        self.assertEqual(t.encoding, 'iso8859_15')
        self.assertEqual(2, len(t.code.splitlines()))

    def test_ignore_pep263_in_textline(self):
        ''' PEP263 strings in text-lines have no effect '''
        self.assertRaises(UnicodeError, lambda: ShpamlTemplate(u'#coding: iso8859_15\nöäü?@€'.encode('iso8859_15')).co)
        t = ShpamlTemplate(u'#coding: iso8859_15\nöäü?@€'.encode('utf8'))
        self.assertEqual(u'#coding: iso8859_15\nöäü?@€\n', t.render())
        self.assertEqual(t.encoding, 'utf8')

    def test_ignore_late_pep263(self):
        ''' PEP263 strings must appear within the first two lines '''
        self.assertRaises(UnicodeError, lambda: ShpamlTemplate(u'\n\n%#coding: iso8859_15\nöäü?@€'.encode('iso8859_15')).co)
        t = ShpamlTemplate(u'\n\n%#coding: iso8859_15\nöäü?@€'.encode('utf8'))
        self.assertEqual(u'\n\nöäü?@€\n', t.render())
        self.assertEqual(t.encoding, 'utf8')

    def test_template_shortcut(self):
        result = shpaml_template('start {{var}} end', var='middle')
        self.assertEqual(u'start middle end\n', result)

    def test_view_decorator(self):
        @shpaml_view('start\n  middle | {{var}}')
        def test():
            return dict(var='middle')
        self.assertEqual(u'<start>\n  <middle>middle</middle>\n</start>\n',test())

    def test_global_config(self):
        ShpamlTemplate.global_config('meh', 1)
        t = ShpamlTemplate(u'anything')
        self.assertEqual(u'anything\n', t.render())

try:
  import shpaml
except ImportError:
  print "WARNING: No SHPAML template support. Skipping tests."
  del TestShpamlTemplate

if __name__ == '__main__': #pragma: no cover
    unittest.main()

