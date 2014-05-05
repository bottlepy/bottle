# -*- coding: utf-8 -*-
import unittest
import tools


class MyPlugin(object):
    def __init__(self):
        self.app = None
        self.add_args = {}
        self.add_content = ''

    def setup(self, app):
        self.app = app

    def apply(self, func, config):
        def wrapper(*a, **ka):
            ka.update(self.add_args)
            self.lastcall = func, a, ka
            return ''.join(func(*a, **ka)) + self.add_content
        return wrapper


def my_decorator(func):
    def wrapper(*a, **ka):
        return list(func(*a, **ka))[-1]



class TestPluginManagement(tools.ServerTestBase):

    def verify_installed(self, plugin, otype, **config):
        self.assertEqual(type(plugin), otype)
        self.assertEqual(plugin.config, config)
        self.assertEqual(plugin.app, self.app)
        self.assertTrue(plugin in self.app.plugins)

    def test_install_plugin(self):
        plugin = MyPlugin()
        installed = self.app.install(plugin)
        self.assertEqual(plugin, installed)
        self.assertTrue(plugin in self.app.plugins)

    def test_install_decorator(self):
        installed = self.app.install(my_decorator)
        self.assertEqual(my_decorator, installed)
        self.assertTrue(my_decorator in self.app.plugins)

    def test_install_non_plugin(self):
        self.assertRaises(TypeError, self.app.install, 'I am not a plugin')

    def test_uninstall_by_instance(self):
        plugin  = self.app.install(MyPlugin())
        plugin2 = self.app.install(MyPlugin())
        self.app.uninstall(plugin)
        self.assertTrue(plugin not in self.app.plugins)
        self.assertTrue(plugin2 in self.app.plugins)

    def test_uninstall_by_type(self):
        plugin = self.app.install(MyPlugin())
        plugin2 = self.app.install(MyPlugin())
        self.app.uninstall(MyPlugin)
        self.assertTrue(plugin not in self.app.plugins)
        self.assertTrue(plugin2 not in self.app.plugins)

    def test_uninstall_by_name(self):
        plugin = self.app.install(MyPlugin())
        plugin2 = self.app.install(MyPlugin())
        plugin.name = 'myplugin'
        self.app.uninstall('myplugin')
        self.assertTrue(plugin not in self.app.plugins)
        self.assertTrue(plugin2 in self.app.plugins)

    def test_uninstall_all(self):
        plugin = self.app.install(MyPlugin())
        plugin2 = self.app.install(MyPlugin())
        self.app.uninstall(True)
        self.assertFalse(self.app.plugins)

    def test_route_plugin(self):
        plugin = MyPlugin()
        plugin.add_content = ';foo'
        @self.app.route('/a')
        @self.app.route('/b', apply=[plugin])
        def a(): return 'plugin'
        self.assertBody('plugin', '/a')
        self.assertBody('plugin;foo', '/b')

    def test_plugin_oder(self):
        self.app.install(MyPlugin()).add_content = ';global-1'
        self.app.install(MyPlugin()).add_content = ';global-2'
        l1 = MyPlugin()
        l1.add_content = ';local-1'
        l2 = MyPlugin()
        l2.add_content = ';local-2'
        @self.app.route('/a')
        @self.app.route('/b', apply=[l1, l2])
        def a(): return 'plugin'
        self.assertBody('plugin;global-2;global-1', '/a')
        self.assertBody('plugin;local-2;local-1;global-2;global-1', '/b')

    def test_skip_by_instance(self):
        g1 = self.app.install(MyPlugin())
        g1.add_content = ';global-1'
        g2 = self.app.install(MyPlugin())
        g2.add_content = ';global-2'
        l1 = MyPlugin()
        l1.add_content = ';local-1'
        l2 = MyPlugin()
        l2.add_content = ';local-2'
        @self.app.route('/a', skip=[g2, l2])
        @self.app.route('/b', apply=[l1, l2], skip=[g2, l2])
        def a(): return 'plugin'
        self.assertBody('plugin;global-1', '/a')
        self.assertBody('plugin;local-1;global-1', '/b')

    def test_skip_by_class(self):
        g1 = self.app.install(MyPlugin())
        g1.add_content = ';global-1'
        @self.app.route('/a')
        @self.app.route('/b', skip=[MyPlugin])
        def a(): return 'plugin'
        self.assertBody('plugin;global-1', '/a')
        self.assertBody('plugin', '/b')

    def test_skip_by_name(self):
        g1 = self.app.install(MyPlugin())
        g1.add_content = ';global-1'
        g1.name = 'test'
        @self.app.route('/a')
        @self.app.route('/b', skip=['test'])
        def a(): return 'plugin'
        self.assertBody('plugin;global-1', '/a')
        self.assertBody('plugin', '/b')

    def test_skip_all(self):
        g1 = self.app.install(MyPlugin())
        g1.add_content = ';global-1'
        @self.app.route('/a')
        @self.app.route('/b', skip=[True])
        def a(): return 'plugin'
        self.assertBody('plugin;global-1', '/a')
        self.assertBody('plugin', '/b')

    def test_skip_nonlist(self):
        g1 = self.app.install(MyPlugin())
        g1.add_content = ';global-1'
        @self.app.route('/a')
        @self.app.route('/b', skip=g1)
        def a(): return 'plugin'
        self.assertBody('plugin;global-1', '/a')
        self.assertBody('plugin', '/b')



class TestPluginAPI(tools.ServerTestBase):

    def setUp(self):
        super(TestPluginAPI, self).setUp()
        @self.app.route('/', test='plugin.cfg')
        def test(**args):
            return ', '.join('%s:%s' % (k,v) for k,v in args.items())

    def test_callable(self):
        def plugin(func):
            def wrapper(*a, **ka):
                return func(test='me', *a, **ka) + '; tail'
            return wrapper
        self.app.install(plugin)
        self.assertBody('test:me; tail', '/')


    def test_apply(self):
        class Plugin(object):
            def apply(self, func, route):
                def wrapper(*a, **ka):
                    return func(test=route.config['test'], *a, **ka) + '; tail'
                return wrapper
            def __call__(self, func):
                raise AssertionError("Plugins must not be called "\
                                     "if they implement 'apply'")
        self.app.install(Plugin())
        self.assertBody('test:plugin.cfg; tail', '/')

    def test_instance_method_wrapper(self):
        class Plugin(object):
            api=2
            def apply(self, callback, route):
                return self.b
            def b(self): return "Hello"
        self.app.install(Plugin())
        self.assertBody('Hello', '/')

    def test_setup(self):
        class Plugin(object):
            def __call__(self, func): return func
            def setup(self, app): self.app = app
        plugin = self.app.install(Plugin())
        self.assertEqual(getattr(plugin, 'app', None), self.app)

    def test_close(self):
        class Plugin(object):
            def __call__(self, func): return func
            def close(self): self.closed = True
        plugin = self.app.install(Plugin())
        plugin2 = self.app.install(Plugin())
        self.app.uninstall(plugin)
        self.assertTrue(getattr(plugin, 'closed', False))
        self.app.close()
        self.assertTrue(getattr(plugin2, 'closed', False))


if __name__ == '__main__': #pragma: no cover
    unittest.main()
