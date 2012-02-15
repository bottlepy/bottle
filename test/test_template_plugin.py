# -*- coding: utf-8 -*-
import unittest
import bottle
import tools

class TestTemplatePlugin(tools.ServerTestBase):

    def test_basic(self):
        @self.app.route('/a', template='{{a}}-{{b}}')
        def test():
            return dict(a='foo', b='bar')
        @self.app.route('/b', template='{{a}}-{{b}}')
        def test():
            return 'no-dict'
        @self.app.route('/c',)
        def test():
            return {}
        self.assertBody('foo-bar', '/a')
        self.assertBody('no-dict', '/b')
        self.assertBody('{}', '/c')

    def test_globals(self):
        @self.app.route('/', template='{{a}}-{{b}}')
        def test():
            return dict(b='bar')
        self.app.views.globals['a'] = 'faa'
        self.assertBody('faa-bar', '/')
        self.app.views.globals['a'] = 'fee'
        self.assertBody('fee-bar', '/')

    def test_options(self):
        @self.app.route('/', template='{{a}}-{{!b}}')
        def test():
            return dict(a='&a', b='&b')
        self.assertBody('&amp;a-&b', '/')
        self.app.views.options['noescape'] = True
        self.app.views.cache.clear()
        self.assertBody('&a-&amp;b', '/')

    def test_appconfig(self):
        self.app.config.view_globals['foo'] = 'bar'
        self.assertEqual(self.app.views.globals, self.app.config.view_globals)

    def test_path_helper(self):
        self.assertFalse(self.app.views.lookup('stpl_simple.tpl'))
        self.app.views.add_path('./views/', __file__)
        self.assertTrue(self.app.views.lookup('stpl_simple.tpl'))
        self.assertFalse(self.app.views.lookup('white_rabbit.tpl'))



if __name__ == '__main__': #pragma: no cover
    unittest.main()


