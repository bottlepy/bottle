import unittest
import sys, os.path
TESTDIR = os.path.dirname(os.path.abspath(__file__))
DISTDIR = os.path.dirname(TESTDIR)
sys.path.insert(0, TESTDIR)
sys.path.insert(0, DISTDIR)

from bottle import route, add_route, match_url, compile_route, ROUTES_REGEXP, ROUTES_SIMPLE

class TestRoutes(unittest.TestCase):

    def test_static(self):
        """ Routes: Static routes """ 
        token = 'abc'
        routes = ['','/','/abc','abc','/abc/','/abc/def','/abc/def.ghi']
        for r in routes:
            add_route(r, token, simple=True)
        self.assertTrue('GET' in ROUTES_SIMPLE)
        r = [r for r in ROUTES_SIMPLE['GET'].values() if r == 'abc']
        self.assertEqual(5, len(r))
        for r in routes:
            self.assertEqual(token, match_url(r)[0])

    def test_dynamic(self):
        """ Routes: Dynamic routes """ 
        token = 'abcd'
        add_route('/:a/:b', token)
        self.assertTrue('GET' in ROUTES_REGEXP)
        self.assertEqual(token, match_url('/aa/bb')[0])
        self.assertEqual(None, match_url('/aa')[0])
        self.assertEqual(repr({'a':'aa','b':'bb'}), repr(match_url('/aa/bb')[1]))


suite = unittest.TestSuite()
suite.addTest(unittest.makeSuite(TestRoutes))

if __name__ == '__main__':
    unittest.main()
