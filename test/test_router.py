import unittest
import bottle

class TestRouter(unittest.TestCase):
    def setUp(self):
        self.r = r = bottle.Router()
    
    def add(self, *a, **ka):
        self.r.add(*a, **ka)
        self.r.compile()

    def testBasic(self):
        add = self.add
        match = self.r.match
        add('/static', 'static')
        self.assertEqual(('static', {}), match('/static'))
        add('/\\:its/:#.+#/:test/:name#[a-z]+#/', 'handler')
        self.assertEqual(('handler', {'test': 'cruel', 'name': 'world'}), match('/:its/a/cruel/world/'))
        add('/:test', 'notail')
        self.assertEqual(('notail', {'test': 'test'}), match('/test'))
        add(':test/', 'nohead')
        self.assertEqual(('nohead', {'test': 'test'}), match('test/'))
        add(':test', 'fullmatch')
        self.assertEqual(('fullmatch', {'test': 'test'}), match('test'))
        add('/:#anon#/match', 'anon')
        self.assertEqual(('anon', {}), match('/anon/match'))
        self.assertEqual((None, {}), match('//no/m/at/ch/'))

    def testParentheses(self):
        add = self.add
        match = self.r.match
        add('/func(:param)', 'func')
        self.assertEqual(('func', {'param':'foo'}), match('/func(foo)'))
        add('/func2(:param#(foo|bar)#)', 'func2')
        self.assertEqual(('func2', {'param':'foo'}), match('/func2(foo)'))
        self.assertEqual(('func2', {'param':'bar'}), match('/func2(bar)'))
        self.assertEqual((None, {}),                match('/func2(baz)'))        
        add('/groups/:param#(foo|bar)#', 'groups')
        self.assertEqual(('groups', {'param':'foo'}), match('/groups/foo'))

    def testErrorInPattern(self):
        self.assertRaises(bottle.RouteSyntaxError, self.add, '/:bug#(#/', 'buggy')

    def testBuild(self):
        add = self.add
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
