# -*- coding: utf-8 -*-
import unittest
from bottle import Jinja2Template, jinja2_template, jinja2_view, touni
from .tools import warn, chdir



class TestJinja2Template(unittest.TestCase):

    def test_string(self):
        """ Templates: Jinja2 string"""
        t = Jinja2Template('start {{var}} end').render(var='var')
        self.assertEqual('start var end', ''.join(t))

    def test_file(self):
        """ Templates: Jinja2 file"""
        with chdir(__file__):
            t = Jinja2Template(name='./views/jinja2_simple.tpl', lookup=['.']).render(var='var')
            self.assertEqual('start var end', ''.join(t))

    def test_name(self):
        """ Templates: Jinja2 lookup by name """
        with chdir(__file__):
            t = Jinja2Template(name='jinja2_simple', lookup=['./views/']).render(var='var')
            self.assertEqual('start var end', ''.join(t))

    def test_notfound(self):
        """ Templates: Unavailable templates"""
        self.assertRaises(Exception, Jinja2Template, name="abcdef")

    def test_error(self):
        """ Templates: Exceptions"""
        self.assertRaises(Exception, Jinja2Template, '{% for badsyntax')

    def test_inherit(self):
        """ Templates: Jinja2 lookup and inherience """
        with chdir(__file__):
            t = Jinja2Template(name='jinja2_inherit', lookup=['./views/']).render()
            self.assertEqual('begin abc end', ''.join(t))

    def test_custom_filters(self):
        """Templates: jinja2 custom filters """
        from bottle import jinja2_template as template
        settings = dict(filters = {"star": lambda var: touni("").join((touni('*'), var, touni('*')))})
        t = Jinja2Template("start {{var|star}} end", **settings)
        self.assertEqual("start *var* end", t.render(var="var"))

    def test_custom_tests(self):
        """Templates: jinja2 custom tests """
        from bottle import jinja2_template as template
        TEMPL = touni("{% if var is even %}gerade{% else %}ungerade{% endif %}")
        settings = dict(tests={"even": lambda x: False if x % 2 else True})
        t = Jinja2Template(TEMPL, **settings)
        self.assertEqual("gerade", t.render(var=2))
        self.assertEqual("ungerade", t.render(var=1))

    def test_template_shortcut(self):
        result = jinja2_template('start {{var}} end', var='middle')
        self.assertEqual(touni('start middle end'), result)

    def test_view_decorator(self):
        @jinja2_view('start {{var}} end')
        def test():
            return dict(var='middle')
        self.assertEqual(touni('start middle end'), test())


try:
  import jinja2
except ImportError:
  warn("No Jinja2 template support. Skipping tests.")
  del TestJinja2Template

