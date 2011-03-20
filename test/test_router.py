import unittest
import bottle

class TestRouter(unittest.TestCase):
    CGI=False
    
    def setUp(self):
        self.r = bottle.Router()
    
    def add(self, path, target, method='GET', **ka):
        self.r.add(path, method, target, **ka)

    def match(self, path, method='GET'):
        env = {'PATH_INFO': path, 'REQUEST_METHOD': method}
        if self.CGI:
            env['wsgi.run_once'] = 'true'
        return self.r.match(env)

    def assertMatches(self, rule, url, method='GET', **args):
        self.add(rule, rule, method)
        target, urlargs = self.match(url, method)
        self.assertEqual(rule, target)
        self.assertEqual(args, urlargs)

    def testBasic(self):
        self.assertMatches('/static', '/static')
        self.assertMatches('/\\:its/:#.+#/:test/:name#[a-z]+#/',
                           '/:its/a/cruel/world/',
                           test='cruel', name='world')
        self.assertMatches('/:test', '/test', test='test') # No tail
        self.assertMatches(':test/', 'test/', test='test') # No head
        self.assertMatches('/:test/', '/test/', test='test') # Middle
        self.assertMatches(':test', 'test', test='test') # Full wildcard
        self.assertMatches('/:#anon#/match', '/anon/match') # Anon wildcards
        self.assertRaises(bottle.HTTPError, self.match, '//no/m/at/ch/')

    def testWildcardNames(self):
        self.assertMatches('/alpha/:abc', '/alpha/alpha', abc='alpha')
        self.assertMatches('/alnum/:md5', '/alnum/sha1', md5='sha1')

    def testParentheses(self):
        self.assertMatches('/func(:param)', '/func(foo)', param='foo')
        self.assertMatches('/func2(:param#(foo|bar)#)', '/func2(foo)', param='foo')
        self.assertMatches('/func2(:param#(foo|bar)#)', '/func2(bar)', param='bar')
        self.assertRaises(bottle.HTTPError, self.match, '/func2(baz)')

    def testErrorInPattern(self):
        self.assertRaises(Exception, self.assertMatches, '/:bug#(#/', '/foo/')

    def testBuild(self):
        add = self.add
        build = self.r.build
        add('/:test/:name#[a-z]+#/', 'handler', name='testroute')
        add('/anon/:#.#', 'handler', name='anonroute')
        url = build('testroute', test='hello', name='world')
        self.assertEqual('/hello/world/', url)
        url = build('testroute', test='hello', name='world', q='value')
        self.assertEqual('/hello/world/?q=value', url)
        self.assertRaises(bottle.RouteBuildError, build, 'test')
        # RouteBuildError: No route found with name 'test'.
        self.assertRaises(bottle.RouteBuildError, build, 'testroute')
        # RouteBuildError: Missing parameter 'test' in route 'testroute'
        #self.assertRaises(bottle.RouteBuildError, build, 'testroute', test='hello', name='1234')
        # RouteBuildError: Parameter 'name' does not match pattern for route 'testroute': '[a-z]+'
        #self.assertRaises(bottle.RouteBuildError, build, 'anonroute')
        # RouteBuildError: Anonymous pattern found. Can't generate the route 'anonroute'.

    def test_method(self):
        #TODO Test method handling. This is done in the router now.
        pass


class TestRouterInCGIMode(TestRouter):
    CGI = True


if __name__ == '__main__': #pragma: no cover
    unittest.main()
