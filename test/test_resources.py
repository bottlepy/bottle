from bottle import ResourceManager
import os.path
import unittest

class TestResourceManager(unittest.TestCase):

    def test_path_normalize(self):
        tests = ('/foo/bar/', '/foo/bar/baz', '/foo/baz/../bar/blub')
        for test in tests:
            rm = ResourceManager()
            rm.add_path(test)
            self.assertEqual(rm.path, ['/foo/bar/'])

    def test_path_create(self):
        import tempfile, shutil
        tempdir = tempfile.mkdtemp()
        try:
            rm = ResourceManager()
            exists = rm.add_path('./test/', base=tempdir)
            self.assertEqual(exists, False)
            exists = rm.add_path('./test2/', base=tempdir, create=True)
            self.assertEqual(exists, True)
        finally:
            shutil.rmtree(tempdir)

    def test_path_absolutize(self):
        tests = ('./foo/bar/', './foo/bar/baz', './foo/baz/../bar/blub')
        abspath = os.path.abspath('./foo/bar/') + os.sep
        for test in tests:
            rm = ResourceManager()
            rm.add_path(test)
            self.assertEqual(rm.path, [abspath])

        for test in tests:
            rm = ResourceManager()
            rm.add_path(test[2:])
            self.assertEqual(rm.path, [abspath])

    def test_path_unique(self):
        tests = ('/foo/bar/', '/foo/bar/baz', '/foo/baz/../bar/blub')
        rm = ResourceManager()
        [rm.add_path(test) for test in tests]
        self.assertEqual(rm.path, ['/foo/bar/'])

    def test_root_path(self):
        tests = ('/foo/bar/', '/foo/bar/baz', '/foo/baz/../bar/blub')
        for test in tests:
            rm = ResourceManager()
            rm.add_path('./baz/', test)
            self.assertEqual(rm.path, ['/foo/bar/baz/'])

        for test in tests:
            rm = ResourceManager()
            rm.add_path('baz/', test)
            self.assertEqual(rm.path, ['/foo/bar/baz/'])

    def test_path_order(self):
        rm = ResourceManager()
        rm.add_path('/middle/')
        rm.add_path('/first/', index=0)
        rm.add_path('/last/')
        self.assertEqual(rm.path, ['/first/', '/middle/', '/last/'])

    def test_get(self):
        rm = ResourceManager()
        rm.add_path('/first/')
        rm.add_path(__file__)
        rm.add_path('/last/')
        self.assertEqual(None, rm.lookup('notexist.txt'))
        self.assertEqual(__file__, rm.lookup(os.path.basename(__file__)))

    def test_open(self):
        rm = ResourceManager()
        rm.add_path(__file__)
        fp = rm.open(__file__)
        self.assertEqual(fp.read(), open(__file__).read())


if __name__ == '__main__': #pragma: no cover
    unittest.main()
