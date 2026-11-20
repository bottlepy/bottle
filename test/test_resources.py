import os.path
import sys
import unittest
from bottle import ResourceManager

if sys.platform == 'win32':
    TEST_PATHS = ('C:\\foo\\bar\\', 'C:\\foo\\bar\\baz', 'C:\\foo\\baz\\..\\bar\\blub')
    EXPECTED = ['C:\\foo\\bar\\']
else:
    TEST_PATHS = ('/foo/bar/', '/foo/bar/baz', '/foo/baz/../bar/blub')
    EXPECTED = ['/foo/bar/']


class TestResourceManager(unittest.TestCase):

    def test_path_normalize(self):
        for test in TEST_PATHS:
            rm = ResourceManager()
            rm.add_path(test)
            self.assertEqual(rm.path, EXPECTED)

    def test_path_create(self):
        import shutil
        import tempfile
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
        if sys.platform == 'win32':
            tests = ('.\\foo\\bar\\', '.\\foo\\bar\\baz', '.\\foo\\baz\\..\\bar\\blub')
            abspath = os.path.abspath('.\\foo\\bar\\') + os.sep
        else:
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
        rm = ResourceManager()
        [rm.add_path(test) for test in TEST_PATHS]
        self.assertEqual(rm.path, EXPECTED)

    def test_root_path(self):
        if sys.platform == 'win32':
            expected = ['C:\\foo\\bar\\baz\\']
        else:
            expected = ['/foo/bar/baz/']

        for test in TEST_PATHS:
            rm = ResourceManager()
            rm.add_path('./baz/', test)
            self.assertEqual(rm.path, expected)

        for test in TEST_PATHS:
            rm = ResourceManager()
            rm.add_path('baz/', test)
            self.assertEqual(rm.path, expected)

    def test_path_order(self):
        rm = ResourceManager()
        rm.add_path('/middle/')
        rm.add_path('/first/', index=0)
        rm.add_path('/last/')

        if sys.platform == 'win32':
            self.assertEqual(rm.path, ['C:\\first\\', 'C:\\middle\\', 'C:\\last\\'])
        else:
            self.assertEqual(rm.path, ['/first/', '/middle/', '/last/'])

    def test_get(self):
        rm = ResourceManager()
        rm.add_path('/first/')
        rm.add_path(__file__)
        rm.add_path('/last/')
        self.assertEqual(None, rm.lookup('nonexistent.txt'))
        self.assertEqual(__file__, rm.lookup(os.path.basename(__file__)))

    def test_open(self):
        rm = ResourceManager()
        rm.add_path(__file__)
        fp = rm.open(__file__)
        self.assertEqual(fp.read(), open(__file__).read())
