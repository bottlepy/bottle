import unittest

from bottle import _parse_http_header


class TestHttpUtils(unittest.TestCase):

    # TODO: Move more of the low level http stuff here.

    def test_accept_header(self):
        self.assertEqual(_parse_http_header(
                'text/xml, text/whitespace ,'
                'application/params;param=value; ws = lots ;"quote"="mid\\"quote",'
                '"more\\"quotes\\"",'
                'I\'m in space!!!'),

                [('text/xml', {}),
                 ('text/whitespace', {}),
                 ('application/params', {'param': 'value', 'ws': 'lots', 'quote': 'mid"quote'}),
                 ('more"quotes"', {}),
                 ('I\'m in space!!!', {})]
        )

    def test_valueless_parameter(self):
        # A parameter with no value must degrade gracefully to an empty value
        # instead of raising, on both the fast path (no quotes) and the slow
        # path (quotes present).
        self.assertEqual(
            _parse_http_header('text/plain; charset'),
            [('text/plain', {'charset': ''})]
        )
        self.assertEqual(
            _parse_http_header('text/plain; charset; x="y"'),
            [('text/plain', {'charset': '', 'x': 'y'})]
        )

