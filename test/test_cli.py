# -*- coding: utf-8 -*-
import unittest
import sys
from io import StringIO

import bottle
from bottle import Bottle, _cli_parse, _format_routes, _list_routes


class TestCliParseListRoutes(unittest.TestCase):

    def test_list_routes_flag_parsed(self):
        args, _ = _cli_parse(['bottle', '--list-routes', 'app:module'])
        self.assertTrue(args.list_routes)

    def test_list_routes_flag_default_false(self):
        args, _ = _cli_parse(['bottle', 'app:module'])
        self.assertFalse(args.list_routes)

    def test_sort_routes_default(self):
        args, _ = _cli_parse(['bottle', 'app:module'])
        self.assertEqual(args.sort_routes, 'definition')

    def test_sort_routes_alphabetical(self):
        args, _ = _cli_parse(['bottle', '--sort-routes', 'alphabetical',
                              'app:module'])
        self.assertEqual(args.sort_routes, 'alphabetical')

    def test_sort_routes_definition(self):
        args, _ = _cli_parse(['bottle', '--sort-routes', 'definition',
                              'app:module'])
        self.assertEqual(args.sort_routes, 'definition')

    def test_sort_routes_invalid_choice(self):
        with self.assertRaises(SystemExit):
            _cli_parse(['bottle', '--sort-routes', 'invalid', 'app:module'])


class TestFormatRoutes(unittest.TestCase):
    """Tests for _format_routes — the pure, I/O-free formatter."""

    def test_no_routes(self):
        app = Bottle()
        self.assertEqual(_format_routes(app), "No routes found.")

    def test_no_routes_alphabetical(self):
        app = Bottle()
        self.assertEqual(_format_routes(app, sort="alphabetical"),
                         "No routes found.")

    def test_single_route(self):
        app = Bottle()

        @app.route('/hello', method='GET')
        def hello():
            return 'hello'

        result = _format_routes(app)
        lines = result.splitlines()
        self.assertEqual(len(lines), 3)  # header, separator, one route
        self.assertIn("Method", lines[0])
        self.assertIn("Route", lines[0])
        self.assertIn("Handler", lines[0])
        self.assertIn("GET", lines[2])
        self.assertIn("/hello", lines[2])
        self.assertIn("hello", lines[2])

    def test_multiple_methods(self):
        app = Bottle()

        @app.route('/item', method=['GET', 'POST'])
        def item():
            return 'item'

        result = _format_routes(app)
        lines = result.splitlines()
        self.assertEqual(len(lines), 4)  # header + separator + 2 routes
        methods = {line.split()[0] for line in lines[2:]}
        self.assertEqual(methods, {'GET', 'POST'})

    def test_definition_order_preserved(self):
        app = Bottle()

        @app.route('/b')
        def route_b():
            return 'b'

        @app.route('/a', method='POST')
        def route_a():
            return 'a'

        result = _format_routes(app)
        lines = result.splitlines()
        self.assertEqual(len(lines), 4)
        # /b was registered first, so it stays first
        self.assertIn("/b", lines[2])
        self.assertIn("route_b", lines[2])
        self.assertIn("/a", lines[3])
        self.assertIn("route_a", lines[3])

    def test_alphabetical_sort_by_rule(self):
        app = Bottle()

        @app.route('/zebra')
        def zebra():
            return 'z'

        @app.route('/alpha')
        def alpha():
            return 'a'

        result = _format_routes(app, sort="alphabetical")
        lines = result.splitlines()
        # /alpha should now come before /zebra
        self.assertIn("/alpha", lines[2])
        self.assertIn("/zebra", lines[3])

    def test_alphabetical_sort_method_tiebreak(self):
        app = Bottle()

        @app.route('/same', method='POST')
        def post_handler():
            return 'post'

        @app.route('/same', method='GET')
        def get_handler():
            return 'get'

        result = _format_routes(app, sort="alphabetical")
        lines = result.splitlines()
        # Same rule, GET < POST alphabetically
        self.assertIn("GET", lines[2])
        self.assertIn("POST", lines[3])

    def test_mounted_sub_app_routes(self):
        parent = Bottle()
        child = Bottle()

        @parent.route('/parent')
        def parent_handler():
            return 'parent'

        @child.route('/child')
        def child_handler():
            return 'child'

        parent.mount('/sub/', child)

        result = _format_routes(parent)
        lines = result.splitlines()
        # header + separator + parent route + child route
        self.assertEqual(len(lines), 4)
        texts = '\n'.join(lines[2:])
        self.assertIn("/parent", texts)
        self.assertIn("parent_handler", texts)
        self.assertIn("/sub/child", texts)
        self.assertIn("child_handler", texts)

    def test_mounted_sub_app_alphabetical(self):
        parent = Bottle()
        child = Bottle()

        @parent.route('/zzz')
        def zzz_handler():
            return 'zzz'

        @child.route('/aaa')
        def aaa_handler():
            return 'aaa'

        parent.mount('/sub/', child)

        result = _format_routes(parent, sort="alphabetical")
        lines = result.splitlines()
        # /sub/aaa should sort before /zzz
        self.assertIn("/sub/aaa", lines[2])
        self.assertIn("/zzz", lines[3])

    def test_column_alignment(self):
        app = Bottle()

        @app.route('/short')
        def s():
            return 's'

        @app.route('/a-much-longer-route-path')
        def longer_name():
            return 'long'

        result = _format_routes(app)
        lines = result.splitlines()
        # All non-separator lines should have the same length (padded)
        header_len = len(lines[0])
        for line in lines[2:]:
            self.assertEqual(len(line), header_len)

    def test_separator_line_uses_dashes(self):
        app = Bottle()

        @app.route('/x')
        def x():
            return 'x'

        result = _format_routes(app)
        lines = result.splitlines()
        sep = lines[1]
        self.assertTrue(all(c in ('-', ' ') for c in sep))

    def test_wildcard_route(self):
        app = Bottle()

        @app.route('/user/<name>')
        def user(name):
            return name

        result = _format_routes(app)
        self.assertIn("/user/<name>", result)
        self.assertIn("user", result)

    def test_returns_string(self):
        app = Bottle()

        @app.route('/check')
        def check():
            return 'ok'

        result = _format_routes(app)
        self.assertIsInstance(result, str)


class TestListRoutesIO(unittest.TestCase):
    """Verify that _list_routes prints what _format_routes returns."""

    def test_list_routes_prints_format_output(self):
        app = Bottle()

        @app.route('/io-test')
        def io_test():
            return 'io'

        expected = _format_routes(app)

        old = sys.stdout
        sys.stdout = buf = StringIO()
        try:
            _list_routes(app)
        finally:
            sys.stdout = old

        self.assertEqual(buf.getvalue().rstrip("\n"), expected)

    def test_list_routes_passes_sort(self):
        app = Bottle()

        @app.route('/z')
        def z():
            return 'z'

        @app.route('/a')
        def a():
            return 'a'

        expected = _format_routes(app, sort="alphabetical")

        old = sys.stdout
        sys.stdout = buf = StringIO()
        try:
            _list_routes(app, sort="alphabetical")
        finally:
            sys.stdout = old

        self.assertEqual(buf.getvalue().rstrip("\n"), expected)


if __name__ == '__main__':
    unittest.main()
