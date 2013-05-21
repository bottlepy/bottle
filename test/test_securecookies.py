#coding: utf-8
import unittest

import bottle
from bottle import tob, touni

class TestSecureCookies(unittest.TestCase):
    def setUp(self):
        self.data = dict(a=5, b=touni('υηι¢σ∂є'), c=[1,2,3,4,tob('bytestring')])
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

class TestSecureCookiesInBottle(unittest.TestCase):
    def setUp(self):
        self.data = dict(a=5, b=touni('υηι¢σ∂є'), c=[1,2,3,4,tob('bytestring')])
        self.secret = tob('secret')
        bottle.app.push()
        bottle.response.bind()

    def tear_down(self):
        bottle.app.pop()

    def get_pairs(self):
        for k, v in bottle.response.headerlist:
            if k == 'Set-Cookie':
                key, value = v.split(';')[0].split('=', 1)
                yield key.lower().strip(), value.strip()
    
    def set_pairs(self, pairs):
        header = ','.join(['%s=%s' % (k, v) for k, v in pairs])
        bottle.request.bind({'HTTP_COOKIE': header})

    def testValid(self):
        bottle.response.set_cookie('key', self.data, secret=self.secret)
        pairs = self.get_pairs()
        self.set_pairs(pairs)
        result = bottle.request.get_cookie('key', secret=self.secret)
        self.assertEqual(self.data, result)

    def testWrongKey(self):
        bottle.response.set_cookie('key', self.data, secret=self.secret)
        pairs = self.get_pairs()
        self.set_pairs([(k+'xxx', v) for (k, v) in pairs])
        result = bottle.request.get_cookie('key', secret=self.secret)
        self.assertEqual(None, result)


if __name__ == '__main__': #pragma: no cover
    unittest.main()
