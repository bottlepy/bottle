import unittest
from bottle import parse_date
import time

class TestDateParser(unittest.TestCase):
    def test_rfc1123(self):
        """DateParser: RFC 1123 format"""
        ts = time.time()
        rs = time.strftime("%a, %d %b %Y %H:%M:%S GMT", time.gmtime(ts))
        self.assertEqual(int(ts), int(parse_date(rs)))

    def test_rfc850(self):
        """DateParser: RFC 850 format"""
        ts = time.time()
        rs = time.strftime("%A, %d-%b-%y %H:%M:%S GMT", time.gmtime(ts))
        self.assertEqual(int(ts), int(parse_date(rs)))

    def test_asctime(self):
        """DateParser: asctime format"""
        ts = time.time()
        rs = time.strftime("%a %b %d %H:%M:%S %Y", time.gmtime(ts))
        self.assertEqual(int(ts), int(parse_date(rs)))

    def test_bad(self):
        """DateParser: Bad format"""
        self.assertEqual(None, parse_date('Bad 123'))


suite = unittest.TestSuite()
suite.addTest(unittest.makeSuite(TestDateParser))

if __name__ == '__main__':
    unittest.main()

