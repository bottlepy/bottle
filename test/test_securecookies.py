import unittest
import bottle
from tools import tob

class TestSecureCookies(unittest.TestCase):
    def setUp(self):
        self.data = dict(a=5, b=u'unicode', c=[1,2,3,4,tob('bytestring')])
        self.key = tob('secret')

    def testDeEncode(self):
        cookie = bottle.cookie_encode(self.data, self.key)
        decoded = bottle.cookie_decode(cookie, self.key)
        self.assertEqual(self.data, decoded)
        decoded = bottle.cookie_decode(cookie+tob('x'), self.key)
        self.assertEqual(None, decoded)

    def testIsEncoded(self):
        cookie = bottle.cookie_encode(self.data, self.key)
        self.assertTrue(bottle.cookie_is_encoded(cookie))
        self.assertFalse(bottle.cookie_is_encoded(tob('some string')))

    def testWithBottle(self):
        bottle.app.push()
        bottle.response.bind()
        bottle.response.set_cookie('key', dict(value=5), secret=tob('1234'))
        cheader = [v for k, v in bottle.response.wsgiheader() if k == 'Set-Cookie'][0]
        bottle.request.bind({'HTTP_COOKIE': cheader.split(';')[0]})
        self.assertEqual(repr(dict(value=5)), repr(bottle.request.get_cookie('key', secret=tob('1234'))))
        bottle.app.pop()

if __name__ == '__main__':
    unittest.main()
