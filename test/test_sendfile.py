import unittest
from bottle import static_file, request, response, parse_date, parse_range_header, Bottle, tob
import bottle
import wsgiref.util
import os
import tempfile
import time

basename = os.path.basename(__file__)
root = os.path.dirname(__file__)

basename2 = os.path.basename(bottle.__file__)
root2 = os.path.dirname(bottle.__file__)


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
        out = static_file(basename, root=root)
        self.assertEqual(open(__file__,'rb').read(), out.body.read())

    def test_invalid(self):
        """ SendFile: Invalid requests"""
        self.assertEqual(404, static_file('not/a/file', root=root).status_code)
        f = static_file(os.path.join('./../', basename), root='./views/')
        self.assertEqual(403, f.status_code)
        try:
            fp, fn = tempfile.mkstemp()
            os.chmod(fn, 0)
            self.assertEqual(403, static_file(fn, root='/').status_code)
        finally:
            os.close(fp)
            os.unlink(fn)

    def test_mime(self):
        """ SendFile: Mime Guessing"""
        f = static_file(basename, root=root)
        self.assertTrue(f.headers['Content-Type'].split(';')[0] in ('application/x-python-code', 'text/x-python'))
        f = static_file(basename, root=root, mimetype='some/type')
        self.assertEqual('some/type', f.headers['Content-Type'])
        f = static_file(basename, root=root, mimetype='text/foo')
        self.assertEqual('text/foo; charset=UTF-8', f.headers['Content-Type'])
        f = static_file(basename, root=root, mimetype='text/foo', charset='latin1')
        self.assertEqual('text/foo; charset=latin1', f.headers['Content-Type'])

    def test_ims(self):
        """ SendFile: If-Modified-Since"""
        request.environ['HTTP_IF_MODIFIED_SINCE'] = time.strftime("%a, %d %b %Y %H:%M:%S GMT", time.gmtime())
        res = static_file(basename, root=root)
        self.assertEqual(304, res.status_code)
        self.assertEqual(int(os.stat(__file__).st_mtime), parse_date(res.headers['Last-Modified']))
        self.assertAlmostEqual(int(time.time()), parse_date(res.headers['Date']))
        request.environ['HTTP_IF_MODIFIED_SINCE'] = time.strftime("%a, %d %b %Y %H:%M:%S GMT", time.gmtime(100))
        self.assertEqual(open(__file__,'rb').read(), static_file(basename, root=root).body.read())

    def test_etag(self):
        """ SendFile: If-Modified-Since"""
        res = static_file(basename, root=root)
        self.assertTrue('ETag' in res.headers)
        self.assertEqual(200, res.status_code)
        etag = res.headers['ETag']
        
        request.environ['HTTP_IF_NONE_MATCH'] = etag
        res = static_file(basename, root=root)
        self.assertTrue('ETag' in res.headers)
        self.assertEqual(etag, res.headers['ETag'])
        self.assertEqual(304, res.status_code)

        request.environ['HTTP_IF_NONE_MATCH'] = etag
        res = static_file(basename2, root=root2)
        self.assertTrue('ETag' in res.headers)
        self.assertNotEqual(etag, res.headers['ETag'])
        self.assertEqual(200, res.status_code)
       

    def test_download(self):
        """ SendFile: Download as attachment """
        f = static_file(basename, root=root, download="foo.mp3")
        self.assertEqual('audio/mpeg', f.headers['Content-Type'])

        f = static_file(basename, root=root, download=True)
        self.assertEqual('attachment; filename="%s"' % basename, f.headers['Content-Disposition'])
        request.environ['HTTP_IF_MODIFIED_SINCE'] = time.strftime("%a, %d %b %Y %H:%M:%S GMT", time.gmtime(100))

        f = static_file(basename, root=root)
        self.assertEqual(open(__file__,'rb').read(), f.body.read())

    def test_range(self):
        request.environ['HTTP_RANGE'] = 'bytes=10-25,-80'
        f = static_file(basename, root=root)
        c = open(__file__, 'rb'); c.seek(10)
        self.assertEqual(c.read(16), tob('').join(f.body))
        self.assertEqual('bytes 10-25/%d' % len(open(__file__, 'rb').read()),
                         f.headers['Content-Range'])
        self.assertEqual('bytes', f.headers['Accept-Ranges'])

    def test_range_parser(self):
        r = lambda rs: list(parse_range_header(rs, 100))
        self.assertEqual([(90, 100)], r('bytes=-10'))
        self.assertEqual([(10, 100)], r('bytes=10-'))
        self.assertEqual([(5, 11)],  r('bytes=5-10'))
        self.assertEqual([(10, 100), (90, 100), (5, 11)],  r('bytes=10-,-10,5-10'))
