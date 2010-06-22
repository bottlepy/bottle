import unittest
import bottle

class TestRouter(unittest.TestCase):
    def setUp(self):
        self.r = r = bottle.Router()

    def testBasic(self):
        add = self.r.add
        match = self.r.match
        add('/static', 'static')
        self.assertEqual({'GET': ('static', None)}, match('/static'))
        add('/\\:its/:#.+#/:test/:name#[a-z]+#/', 'handler')
        path = '/:its/a/cruel/world/'
        matcher = match(path).get('GET')
        self.assertEqual(('handler', {'test': 'cruel', 'name': 'world'}), (matcher[0], matcher[1].match(path).groupdict()))
        add('/:test', 'notail')
        path = '/test'
        matcher = match(path).get('GET')
        self.assertEqual(('notail', {'test': 'test'}), (matcher[0], matcher[1].match(path).groupdict()))
        add(':test/', 'nohead')
        path = 'test/'
        matcher = match(path).get('GET')
        self.assertEqual(('nohead', {'test': 'test'}), (matcher[0], matcher[1].match(path).groupdict()))
        add(':test', 'fullmatch')
        path = 'test'
        matcher = match(path).get('GET')
        self.assertEqual(('fullmatch', {'test': 'test'}), (matcher[0], matcher[1].match(path).groupdict()))
        add('/:#anon#/match', 'anon')
        path = '/anon/match'
        matcher = match(path).get('GET')
        self.assertEqual(('anon', {}), (matcher[0], {}))
        path = '//no/m/at/ch/'
        matcher = match(path).get('GET')
        self.assertEqual((None, {}), (None, {}))

    def testParentheses(self):
        add = self.r.add
        match = self.r.match
        add('/func(:param)', 'func')
        path = '/func(foo)'
        matcher = match(path).get('GET')
        self.assertEqual(('func', {'param':'foo'}), (matcher[0], matcher[1].match(path).groupdict()))
        add('/func2(:param#(foo|bar)#)', 'func2')
        path = '/func2(foo)'
        matcher = match(path).get('GET')
        self.assertEqual(('func2', {'param':'foo'}), (matcher[0], matcher[1].match(path).groupdict()))
        path = '/func2(bar)'
        matcher = match(path).get('GET')
        self.assertEqual(('func2', {'param':'bar'}), (matcher[0], matcher[1].match(path).groupdict()))
        path = '/func2(baz)'
        matcher = match(path).get('GET')
        self.assertEqual((None, {}), (None, {}))
        add('/groups/:param#(foo|bar)#', 'groups')
        path = '/groups/foo'
        matcher = match(path).get('GET')
        self.assertEqual(('groups', {'param':'foo'}), (matcher[0], matcher[1].match(path).groupdict()))

    def testErrorInPattern(self):
        self.assertRaises(bottle.RouteSyntaxError, self.r.add, '/:bug#(#/', 'buggy')

    def testBuild(self):
        add = self.r.add
        build = self.r.build
        add('/:test/:name#[a-z]+#/', 'handler', name='testroute')
        add('/anon/:#.#', 'handler', name='anonroute')
        url = build('testroute', test='hello', name='world')
        self.assertEqual('/hello/world/', url)
        self.assertRaises(bottle.RouteBuildError, build, 'test')
        # RouteBuildError: No route found with name 'test'.
        self.assertRaises(bottle.RouteBuildError, build, 'testroute')
        # RouteBuildError: Missing parameter 'test' in route 'testroute'
        #self.assertRaises(bottle.RouteBuildError, build, 'testroute', test='hello', name='1234')
        # RouteBuildError: Parameter 'name' does not match pattern for route 'testroute': '[a-z]+'
        #self.assertRaises(bottle.RouteBuildError, build, 'anonroute')
        # RouteBuildError: Anonymous pattern found. Can't generate the route 'anonroute'.

if __name__ == '__main__':
    unittest.main()
