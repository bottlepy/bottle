# -*- coding: utf-8 -*-
import unittest
import sys, os.path
from bottle import request, response
import tools
from tools import tob
import wsgiref.util

class TestEnviron(unittest.TestCase):
    def test_path(self):
        """ Environ: PATH_INFO """ 
        t = dict()
        t[''] = '/'
        t['bla'] = '/bla'
        t['bla/'] = '/bla/'
        t['/bla'] = '/bla'
        t['/bla/'] = '/bla/'
        for k, v in t.iteritems():
            request.bind({'PATH_INFO': k}, None)
            self.assertEqual(v, request.path)
        request.bind({}, None)
        self.assertEqual('/', request.path)

    def test_pathshift(self):
        """ Environ: Request.path_shift() """
        def test_shift(s, p, c):
            request.bind({'SCRIPT_NAME': s, 'PATH_INFO': p})
            request.path_shift(c)
            return [request['SCRIPT_NAME'], request.path]
        self.assertEqual(['/a/b', '/c/d'], test_shift('/a/b', '/c/d', 0))
        self.assertEqual(['/a/b', '/c/d/'], test_shift('/a/b', '/c/d/', 0))
        self.assertEqual(['/a/b/c', '/d'], test_shift('/a/b', '/c/d', 1))
        self.assertEqual(['/a', '/b/c/d'], test_shift('/a/b', '/c/d', -1))
        self.assertEqual(['/a/b/c', '/d/'], test_shift('/a/b', '/c/d/', 1))
        self.assertEqual(['/a', '/b/c/d/'], test_shift('/a/b', '/c/d/', -1))
        self.assertEqual(['/a/b/c', '/d/'], test_shift('/a/b/', '/c/d/', 1))
        self.assertEqual(['/a', '/b/c/d/'], test_shift('/a/b/', '/c/d/', -1))
        self.assertEqual(['/a/b/c/d', '/'], test_shift('/', '/a/b/c/d', 4))
        self.assertEqual(['/', '/a/b/c/d/'], test_shift('/a/b/c/d', '/', -4))
        self.assertRaises(AssertionError, test_shift, '/a/b', '/c/d', 3)
        self.assertRaises(AssertionError, test_shift, '/a/b', '/c/d', -3)
        
    def test_url(self):
        """ Environ: URL building """
        request.bind({'HTTP_HOST':'example.com'}, None)
        self.assertEqual('http://example.com/', request.url)
        request.bind({'SERVER_NAME':'example.com'}, None)
        self.assertEqual('http://example.com/', request.url)
        request.bind({'SERVER_NAME':'example.com', 'SERVER_PORT':'81'}, None)
        self.assertEqual('http://example.com:81/', request.url)
        request.bind({'wsgi.url_scheme':'https', 'SERVER_NAME':'example.com'}, None)
        self.assertEqual('https://example.com:80/', request.url)
        request.bind({'HTTP_HOST':'example.com', 'PATH_INFO':'/path', 'QUERY_STRING':'1=b&c=d', 'SCRIPT_NAME':'/sp'}, None)
        self.assertEqual('http://example.com/sp/path?1=b&c=d', request.url)

    def test_dict_access(self):
        """ Environ: request objects are environment dicts """
        e = {}
        wsgiref.util.setup_testing_defaults(e)
        request.bind(e, None)
        self.assertEqual(list(request), e.keys())
        self.assertEqual(len(request), len(e))
        for k, v in e.iteritems():
            self.assertTrue(k in request)
            self.assertEqual(request[k], v)
            request[k] = 'test'
            self.assertEqual(request[k], 'test')
        del request['PATH_INFO']
        self.assertTrue('PATH_INFO' not in request)

    def test_header_access(self):
        """ Environ: Request objects decode headers """
        e = {}
        wsgiref.util.setup_testing_defaults(e)
        e['HTTP_SOME_HEADER'] = 'some value'
        request.bind(e, None)
        request['HTTP_SOME_OTHER_HEADER'] = 'some other value'
        self.assertTrue('Some-Header' in request.header)
        self.assertTrue(request.header['Some-Header'] == 'some value')
        self.assertTrue(request.header['Some-Other-Header'] == 'some other value')

    def test_cookie(self):
        """ Environ: COOKIES """ 
        t = dict()
        t['a=a'] = {'a': 'a'}
        t['a=a; b=b'] = {'a': 'a', 'b':'b'}
        t['a=a; a=b'] = {'a': 'b'}
        for k, v in t.iteritems():
            request.bind({'HTTP_COOKIE': k}, None)
            self.assertEqual(v, request.COOKIES)

    def test_get(self):
        """ Environ: GET data """ 
        e = {}
        e['QUERY_STRING'] = 'a=a&a=1&b=b&c=c'
        request.bind(e, None)
        self.assertTrue('a' in request.GET)
        self.assertTrue('b' in request.GET)
        self.assertEqual(['a','1'], request.GET.getall('a'))
        self.assertEqual(['b'], request.GET.getall('b'))
        self.assertEqual('1', request.GET['a'])
        self.assertEqual('b', request.GET['b'])
        
    def test_post(self):
        """ Environ: POST data """ 
        sq = u'a=a&a=1&b=b&c=&d'.encode('utf8')
        e = {}
        wsgiref.util.setup_testing_defaults(e)
        e['wsgi.input'].write(sq)
        e['wsgi.input'].seek(0)
        e['CONTENT_LENGTH'] = str(len(sq))
        e['REQUEST_METHOD'] = "POST"
        request.bind(e, None)
        self.assertTrue('a' in request.POST)
        self.assertTrue('b' in request.POST)
        self.assertEqual(['a','1'], request.POST.getall('a'))
        self.assertEqual(['b'], request.POST.getall('b'))
        self.assertEqual('1', request.POST['a'])
        self.assertEqual('b', request.POST['b'])
        self.assertEqual('', request.POST['c'])
        self.assertEqual('', request.POST['d'])

    def test_bodypost(self):
        sq = u'foobar'.encode('utf8')
        e = {}
        wsgiref.util.setup_testing_defaults(e)
        e['wsgi.input'].write(sq)
        e['wsgi.input'].seek(0)
        e['CONTENT_LENGTH'] = str(len(sq))
        e['REQUEST_METHOD'] = "POST"
        request.bind(e, None)
        self.assertEqual('', request.POST['foobar'])

    def test_body_noclose(self):
        """ Test that the body file handler is not closed after request.POST """
        sq = u'a=a&a=1&b=b&c=&d'.encode('utf8')
        e = {}
        wsgiref.util.setup_testing_defaults(e)
        e['wsgi.input'].write(sq)
        e['wsgi.input'].seek(0)
        e['CONTENT_LENGTH'] = str(len(sq))
        e['REQUEST_METHOD'] = "POST"
        request.bind(e, None)
        self.assertEqual(sq, request.body.read())
        request.POST # This caused a body.close() with Python 3.x
        self.assertEqual(sq, request.body.read())

    def test_params(self):
        """ Environ: GET and POST are combined in request.param """ 
        e = {}
        wsgiref.util.setup_testing_defaults(e)
        e['wsgi.input'].write(tob('b=b&c=p'))
        e['wsgi.input'].seek(0)
        e['CONTENT_LENGTH'] = '7'
        e['QUERY_STRING'] = 'a=a&c=g'
        e['REQUEST_METHOD'] = "POST"
        request.bind(e, None)
        self.assertEqual(['a','b','c'], sorted(request.params.keys()))
        self.assertEqual('p', request.params['c'])

    def test_getpostleak(self):
        """ Environ: GET and POST sh0uld not leak into each other """ 
        e = {}
        wsgiref.util.setup_testing_defaults(e)
        e['wsgi.input'].write(u'b=b'.encode('utf8'))
        e['wsgi.input'].seek(0)
        e['CONTENT_LENGTH'] = '3'
        e['QUERY_STRING'] = 'a=a'
        e['REQUEST_METHOD'] = "POST"
        request.bind(e, None)
        self.assertEqual(['a'], request.GET.keys())
        self.assertEqual(['b'], request.POST.keys())

    def test_body(self):
        """ Environ: Request.body should behave like a file object factory """ 
        e = {}
        wsgiref.util.setup_testing_defaults(e)
        e['wsgi.input'].write(u'abc'.encode('utf8'))
        e['wsgi.input'].seek(0)
        e['CONTENT_LENGTH'] = str(3)
        request.bind(e, None)
        self.assertEqual(u'abc'.encode('utf8'), request.body.read())
        self.assertEqual(u'abc'.encode('utf8'), request.body.read(3))
        self.assertEqual(u'abc'.encode('utf8'), request.body.readline())
        self.assertEqual(u'abc'.encode('utf8'), request.body.readline(3))

    def test_bigbody(self):
        """ Environ: Request.body should handle big uploads using files """
        e = {}
        wsgiref.util.setup_testing_defaults(e)
        e['wsgi.input'].write((u'x'*1024*1000).encode('utf8'))
        e['wsgi.input'].seek(0)
        e['CONTENT_LENGTH'] = str(1024*1000)
        request.bind(e, None)
        self.assertTrue(hasattr(request.body, 'fileno'))        
        self.assertEqual(1024*1000, len(request.body.read()))
        self.assertEqual(1024, len(request.body.read(1024)))
        self.assertEqual(1024*1000, len(request.body.readline()))
        self.assertEqual(1024, len(request.body.readline(1024)))

    def test_tobigbody(self):
        """ Environ: Request.body should truncate to Content-Length bytes """
        e = {}
        wsgiref.util.setup_testing_defaults(e)
        e['wsgi.input'].write((u'x'*1024).encode('utf8'))
        e['wsgi.input'].seek(0)
        e['CONTENT_LENGTH'] = '42'
        request.bind(e, None)
        self.assertEqual(42, len(request.body.read()))
        self.assertEqual(42, len(request.body.read(1024)))
        self.assertEqual(42, len(request.body.readline()))
        self.assertEqual(42, len(request.body.readline(1024)))

class TestMultipart(unittest.TestCase):
    def test_multipart(self):
        """ Environ: POST (multipart files and multible values per key) """
        fields = [('field1','value1'), ('field2','value2'), ('field2','value3')]
        files = [('file1','filename1.txt','content1'), ('file2','filename2.py',u'ä\nö\rü')]
        e = tools.multipart_environ(fields=fields, files=files)
        request.bind(e, None)
        # File content
        self.assertTrue('file1' in request.POST)
        self.assertEqual('content1', request.POST['file1'].file.read())
        # File name and meta data
        self.assertTrue('file2' in request.POST)
        self.assertEqual('filename2.py', request.POST['file2'].filename)
        # UTF-8 files
        x = request.POST['file2'].file.read()
        if sys.version_info >= (3,0,0):
            x = x.encode('ISO-8859-1')
        self.assertEqual(u'ä\nö\rü'.encode('utf8'), x)
        # No file
        self.assertTrue('file3' not in request.POST)
        # Field (single)
        self.assertEqual('value1', request.POST['field1'])
        # Field (multi)
        self.assertEqual(2, len(request.POST.getall('field2')))
        self.assertEqual(['value2', 'value3'], request.POST.getall('field2'))

if __name__ == '__main__':
    unittest.main()
