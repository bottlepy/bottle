import unittest
import bottle

class TestSecureCookies(unittest.TestCase):
    def setUp(self):
        self.data = dict(a=5, b=u'unicode', c=[1,2,3,4,'5'])
        self.key = u'secret'.encode('utf8')

    def testDeEncode(self):
        cookie = bottle.cookie_encode(self.data, self.key)
        self.assertEqual('!RidFXtwOzjhv4wGg/P2gTA==?gAJ9cQEoVQFhSwVVAWNdcQIoSwFLAksDSwRVATVlVQFiWAcAAAB1bmljb2RlcQN1Lg==', cookie)
        decoded = bottle.cookie_decode(cookie, self.key)
        self.assertEqual(self.data, decoded)

    def testIsEncoded(self):
        cookie = bottle.cookie_encode(self.data, self.key)
        self.assertTrue(bottle.cookie_is_encoded(cookie))
        self.assertFalse(bottle.cookie_is_encoded('some string'))

if __name__ == '__main__':
    unittest.main()
