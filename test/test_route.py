import unittest
import bottle
import functools
from tools import api


class TestRoute(unittest.TestCase):

    @api('0.12')
    def test_callback_inspection(self):
        def x(a, b): pass
        def d(f):
            @functools.wraps(f)
            def w():
                return f()
            return w
        
        route = bottle.Route(None, None, None, d(x))
        self.assertEqual(route.get_undecorated_callback(), x)
        self.assertEqual(set(route.get_callback_args()), set(['a', 'b']))

        def d2(foo):
            def d(f):
                @functools.wraps(f)
                def w():
                    return f()
                return w
            return d

        route = bottle.Route(None, None, None, d2('foo')(x))
        self.assertEqual(route.get_undecorated_callback(), x)
        self.assertEqual(set(route.get_callback_args()), set(['a', 'b']))

        def d3(a, b):
            return ''

        route = bottle.Route(None, None, None, bottle.view('index')(d3))
        self.assertEqual(route.get_undecorated_callback(), d3)
        self.assertEqual(set(route.get_callback_args()), set(['a', 'b']))
