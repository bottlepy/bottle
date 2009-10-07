import unittest
from bottle import send_file, BreakTheBottle, HTTPError, request, response, parse_date
import os
import os.path
import tempfile
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


class TestSendFile(unittest.TestCase):
    def test_valid(self):
        """ SendFile: Valid requests"""
        try:
            send_file(os.path.basename(__file__), root='./')
        except BreakTheBottle, e:
            self.assertEqual(open(__file__,'rb').read(), e.output.read())

    def test_invalid(self):
        """ SendFile: Invalid requests"""
        try:
            send_file('not/a/file', root='./')
        except HTTPError, e:
            self.assertEqual(404, e.http_status)
        try:
            send_file(os.path.join('./../', os.path.basename(__file__)), root='./views/')
        except HTTPError, e:
            self.assertEqual(401, e.http_status)
        try:
            fp, fn = tempfile.mkstemp()
            os.chmod(fn, 0)
            try:
                send_file(fn, root='/')
            except HTTPError, e:
                self.assertEqual(401, e.http_status)
        finally:
            os.close(fp)
            os.unlink(fn)
            
    def test_mime(self):
        """ SendFile: Mime Guessing"""
        try:
            send_file(os.path.basename(__file__), root='./')
        except BreakTheBottle, e:
            self.assertTrue(response.content_type in ('application/x-python-code', 'text/x-python'))
        try:
            send_file(os.path.basename(__file__), root='./', mimetype='some/type')
        except BreakTheBottle, e:
            self.assertEqual('some/type', response.content_type)
        try:
            send_file(os.path.basename(__file__), root='./', guessmime=False)
        except BreakTheBottle, e:
            self.assertEqual('text/plain', response.content_type)

    def test_ims(self):
        """ SendFile: If-Modified-Since"""
        request.environ['HTTP_IF_MODIFIED_SINCE'] = time.strftime("%a, %d %b %Y %H:%M:%S GMT", time.gmtime())
        response.bind()
        try:
            send_file(os.path.basename(__file__), root='./')
        except HTTPError, e:
            self.assertEqual(304 ,e.http_status)

        request.environ['HTTP_IF_MODIFIED_SINCE'] = time.strftime("%a, %d %b %Y %H:%M:%S GMT", time.gmtime(100))
        try:
            send_file(os.path.basename(__file__), root='./')
        except BreakTheBottle, e:
            self.assertEqual(open(__file__,'rb').read(), e.output.read())



suite = unittest.TestSuite()
suite.addTest(unittest.makeSuite(TestSendFile))
suite.addTest(unittest.makeSuite(TestDateParser))

if __name__ == '__main__':
    unittest.main()

