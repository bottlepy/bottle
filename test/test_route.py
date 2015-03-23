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
        # decorator with multiple arguments
        def d2(fn=None, filename="default.sqlite", table="default"):
            def d(fn):
                def w(*args, **kwargs):
                    kwargs["a"] = filename
                    kwargs["b"] = table
                    return fn(*args, **kwargs)
                return w

            # support for calling this decorator without arguments
            if fn:
                return d(fn)

            return d

        def pretty_dump(fn):
            def pretty_dump_wrapper(*args, **kwargs):
                return fn(*args, **kwargs)

            return pretty_dump_wrapper

        # multiple decorators
        @bottle.get("somepath")
        @d2(filename='foo', table='bar')
        @pretty_dump
        def x(a, b):
            return

        route = bottle.Route(None, None, None, x)
        self.assertEqual(set(route.get_callback_args()), set(['a', 'b']))
