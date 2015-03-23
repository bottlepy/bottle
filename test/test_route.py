import unittest
import bottle
from tools import api


class TestRoute(unittest.TestCase):

    @api('0.12')
    def test_callback_inspection(self):
        def x(a, b): pass
        def d(f):
            def w():
                return f()
            return w
        
        route = bottle.Route(None, None, None, d(x))
        self.assertEqual(route.get_undecorated_callback(), x)
        self.assertEqual(set(route.get_callback_args()), set(['a', 'b']))

        def d2(foo):
            def d(f):
                def w():
                    return f()
                return w
            return d

        route = bottle.Route(None, None, None, d2('foo')(x))
        self.assertEqual(route.get_undecorated_callback(), x)
        self.assertEqual(set(route.get_callback_args()), set(['a', 'b']))

    def test_callback_inspection_multiple_args(self):
        def x(a, b):
            pass

        # decorator with multiple arguments
        def d2(fn=None, arg1="something", arg2="something else"):
            def d(f):
                def w(*args, **kwargs):
                    return f()
                return w

            # support for calling this decorator without arguments
            if fn:
                return d(fn)

            return d

        # both decorator parameters
        route = bottle.Route(None, None, None, d2(arg1='foo', arg2='bar')(x))
        self.assertEqual(route.get_undecorated_callback(), x)
        self.assertEqual(set(route.get_callback_args()), set(['a', 'b']))

        # first decorator parameter
        route = bottle.Route(None, None, None, d2(arg1='foo')(x))
        self.assertEqual(route.get_undecorated_callback(), x)
        self.assertEqual(set(route.get_callback_args()), set(['a', 'b']))

        # second decorator parameter
        route = bottle.Route(None, None, None, d2(arg2='bar')(x))
        self.assertEqual(route.get_undecorated_callback(), x)
        self.assertEqual(set(route.get_callback_args()), set(['a', 'b']))

        # without decorator parameters
        route = bottle.Route(None, None, None, d2()(x))
        self.assertEqual(route.get_undecorated_callback(), x)
        self.assertEqual(set(route.get_callback_args()), set(['a', 'b']))