"""
Tests & demonstrates various OO approaches to routes
"""
import unittest
import sys

if sys.version_info >= (3, 0, 0):
    from io import BytesIO
else:
    from StringIO import StringIO as BytesIO

__author__ = 'atc'

from bottle import Bottle, request, tob, BaseRequest


class TestRouter(object):
    """
    A test class for wrapping routes to test certain OO scenarios
    """

    app = Bottle()

    @app.post("/route1/<msg>")
    def route_1(self, msg):
        body = request.body.readline()
        return {'msg': msg, 'len': len(body)}


class TestRoutes(unittest.TestCase):
    def test_route1(self):
        body = "abc"
        request.environ['CONTENT_LENGTH'] = str(len(tob(body)))
        request.environ['wsgi.input'] = BytesIO()
        request.environ['wsgi.input'].write(tob(body))
        request.environ['wsgi.input'].seek(0)

        result = TestRouter().route_1("bob")
        self.assertEqual(result, dict(msg="bob", len=3))
