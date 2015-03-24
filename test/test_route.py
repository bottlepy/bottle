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
        # decorator with argument, modifying kwargs
        def d2(f="1"):
            def d(fn):
                def w(*args, **kwargs):
                    # modification of kwargs WITH the decorator argument
                    # is necessary requirement for the error
                    kwargs["a"] = f
                    return fn(*args, **kwargs)
                return w
            return d

        @d2(f='foo')
        def x(a, b):
            return

        route = bottle.Route(None, None, None, x)

        # triggers the "TypeError: 'foo' is not a Python function"
        self.assertEqual(set(route.get_callback_args()), set(['a', 'b']))
