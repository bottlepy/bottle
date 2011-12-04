import unittest
from bottle import static_file, HTTPError, HTTPResponse, request, response, parse_date, parse_range_header, Bottle, tob
import wsgiref.util
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
    def setUp(self):
        e = dict()
        wsgiref.util.setup_testing_defaults(e)
        b = Bottle()
        request.bind(e)
        response.bind()

    def test_valid(self):
        """ SendFile: Valid requests"""
        out = static_file(os.path.basename(__file__), root='./')
        self.assertEqual(open(__file__,'rb').read(), out.output.read())

    def test_invalid(self):
        """ SendFile: Invalid requests"""
        self.assertEqual(404, static_file('not/a/file', root='./').status)
        f = static_file(os.path.join('./../', os.path.basename(__file__)), root='./views/')
        self.assertEqual(403, f.status)
        try:
            fp, fn = tempfile.mkstemp()
            os.chmod(fn, 0)
            self.assertEqual(403, static_file(fn, root='/').status)
        finally:
            os.close(fp)
            os.unlink(fn)
            
    def test_mime(self):
        """ SendFile: Mime Guessing"""
        f = static_file(os.path.basename(__file__), root='./')
        self.assertTrue(f.headers['Content-Type'] in ('application/x-python-code', 'text/x-python'))
        f = static_file(os.path.basename(__file__), root='./', mimetype='some/type')
        self.assertEqual('some/type', f.headers['Content-Type'])

    def test_ims(self):
        """ SendFile: If-Modified-Since"""
        request.environ['HTTP_IF_MODIFIED_SINCE'] = time.strftime("%a, %d %b %Y %H:%M:%S GMT", time.gmtime())
        res = static_file(os.path.basename(__file__), root='./')
        self.assertEqual(304, res.status)
        self.assertEqual(int(os.stat(__file__).st_mtime), parse_date(res.headers['Last-Modified']))
        self.assertAlmostEqual(int(time.time()), parse_date(res.headers['Date']))
        request.environ['HTTP_IF_MODIFIED_SINCE'] = time.strftime("%a, %d %b %Y %H:%M:%S GMT", time.gmtime(100))
        self.assertEqual(open(__file__,'rb').read(), static_file(os.path.basename(__file__), root='./').output.read())

    def test_download(self):
        """ SendFile: Download as attachment """
        basename = os.path.basename(__file__)
        f = static_file(basename, root='./', download=True)
        self.assertEqual('attachment; filename="%s"' % basename, f.headers['Content-Disposition'])
        request.environ['HTTP_IF_MODIFIED_SINCE'] = time.strftime("%a, %d %b %Y %H:%M:%S GMT", time.gmtime(100))
        f = static_file(os.path.basename(__file__), root='./')
        self.assertEqual(open(__file__,'rb').read(), f.output.read())

    def test_range(self):
        basename = os.path.basename(__file__)
        request.environ['HTTP_RANGE'] = 'bytes=10-25,-80'
        f = static_file(basename, root='./')
        c = open(basename, 'rb'); c.seek(10)
        self.assertEqual(c.read(16), tob('').join(f.output))
        self.assertEqual('bytes 10-25/%d' % len(open(basename, 'rb').read()),
                         f.headers['Content-Range'])
        self.assertEqual('bytes', f.headers['Accept-Ranges'])
    
    def test_range_parser(self):
        r = lambda rs: list(parse_range_header(rs, 100))
        self.assertEqual([(90, 100)], r('bytes=-10'))
        self.assertEqual([(10, 100)], r('bytes=10-'))
        self.assertEqual([(5, 11)],  r('bytes=5-10'))
        self.assertEqual([(10, 100), (90, 100), (5, 11)],  r('bytes=10-,-10,5-10'))


if __name__ == '__main__': #pragma: no cover
    unittest.main()

