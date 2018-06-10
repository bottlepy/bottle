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

