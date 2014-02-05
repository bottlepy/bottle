import bottle
from tools import ServerTestBase
from bottle import response

class TestAppMounting(ServerTestBase):
    def setUp(self):
        ServerTestBase.setUp(self)
        self.subapp = bottle.Bottle()
        @self.subapp.route('/')
        @self.subapp.route('/test/:test')
        def test(test='foo'):
            return test


    def test_mount_order_bug581(self):
        self.app.mount('/test/', self.subapp)

        # This should not match
        self.app.route('/<test:path>', callback=lambda test: test)

        self.assertStatus(200, '/test/')
        self.assertBody('foo', '/test/')

    def test_mount(self):
        self.app.mount('/test/', self.subapp)
        self.assertStatus(404, '/')
        self.assertStatus(404, '/test')
        self.assertStatus(200, '/test/')
        self.assertBody('foo', '/test/')
        self.assertStatus(200, '/test/test/bar')
        self.assertBody('bar', '/test/test/bar')

    def test_mount_meta(self):
        self.app.mount('/test/', self.subapp)
        self.assertEqual(
            self.app.routes[0].config['mountpoint.prefix'],
            '/test/')
        self.assertEqual(
            self.app.routes[0].config['mountpoint.target'],
            self.subapp)

    def test_no_slash_prefix(self):
        self.app.mount('/test', self.subapp)
        self.assertStatus(404, '/')
        self.assertStatus(200, '/test')
        self.assertBody('foo', '/test')
        self.assertStatus(200, '/test/')
        self.assertBody('foo', '/test/')
        self.assertStatus(200, '/test/test/bar')
        self.assertBody('bar', '/test/test/bar')

    def test_mount_no_plugins(self):
        def plugin(func):
            def wrapper(*a, **ka):
                return 'Plugin'
            return wrapper
        self.app.install(plugin)
        self.app.route('/foo', callback=lambda: 'baz')
        self.app.mount('/test/', self.subapp)
        self.assertBody('Plugin', '/foo')
        self.assertBody('foo', '/test/')

    def test_mount_wsgi(self):
        status = {}
        def app(environ, start_response):
            start_response('200 OK', [('X-Test', 'WSGI')])
            return 'WSGI ' + environ['PATH_INFO']
        self.app.mount('/test', app)
        self.assertStatus(200, '/test/')
        self.assertBody('WSGI /', '/test')
        self.assertBody('WSGI /', '/test/')
        self.assertHeader('X-Test', 'WSGI', '/test/')
        self.assertBody('WSGI /test/bar', '/test/test/bar')
            
    def test_mount_wsgi(self):
        @self.subapp.route('/cookie')
        def test_cookie():
            response.set_cookie('a', 'a')
            response.set_cookie('b', 'b')
        self.app.mount('/test', self.subapp)
        c = self.urlopen('/test/cookie')['header']['Set-Cookie']
        self.assertEqual(['a=a', 'b=b'], list(sorted(c.split(', '))))

    def test_mount_wsgi_ctype_bug(self):
        status = {}
        def app(environ, start_response):
            start_response('200 OK', [('Content-Type', 'test/test')])
            return 'WSGI ' + environ['PATH_INFO']
        self.app.mount('/test', app)
        self.assertHeader('Content-Type', 'test/test', '/test/')

    def test_mount_json_bug(self):
        @self.subapp.route('/json')
        def test_cookie():
            return {'a':5}
        self.app.mount('/test', self.subapp)
        self.assertHeader('Content-Type', 'application/json', '/test/json')

class TestAppMerging(ServerTestBase):
    def setUp(self):
        ServerTestBase.setUp(self)
        self.subapp = bottle.Bottle()
        @self.subapp.route('/')
        @self.subapp.route('/test/:test')
        def test(test='foo'):
            return test

    def test_merge(self):
        self.app.merge(self.subapp)
        self.assertStatus(200, '/')
        self.assertBody('foo', '/')
        self.assertStatus(200, '/test/bar')
        self.assertBody('bar', '/test/bar')



if __name__ == '__main__': #pragma: no cover
    unittest.main()
