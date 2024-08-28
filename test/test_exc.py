import bottle
from .tools import ServerTestBase

class SomeError(Exception):
    pass

class TestAppException(ServerTestBase):

    def test_no_exc(self):
        @bottle.route('/')
        def test(): return 'test'
        self.assertBody('test', '/')

    def test_memory_error(self):
        @bottle.route('/')
        def test(): raise MemoryError
        with self.assertRaises(MemoryError):
            self.urlopen("/")

    def test_system_Exit(self):
        @bottle.route('/')
        def test(): raise SystemExit
        with self.assertRaises(SystemExit):
            self.urlopen("/")

    def test_other_error(self):
        @bottle.route('/')
        def test(): raise SomeError
        self.assertStatus(500, '/')
        self.assertInBody('SomeError')

    def test_noncatched_error(self):
        @bottle.route('/')
        def test(): raise SomeError
        bottle.request.environ['exc_info'] = None
        bottle.catchall = False
        self.assertStatus(500, '/')
        self.assertInBody('SomeError')
