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

    def testIsEncoded(self):
        cookie = bottle.cookie_encode(self.data, self.key)
        self.assertTrue(bottle.cookie_is_encoded(cookie))
        self.assertFalse(bottle.cookie_is_encoded(tob('some string')))

if __name__ == '__main__':
    unittest.main()
