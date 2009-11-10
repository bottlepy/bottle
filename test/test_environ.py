# -*- coding: utf-8 -*-
import unittest
import sys, os.path
from bottle import request, response
import tools
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
            request.bind({'PATH_INFO': k})
            self.assertEqual(v, request.path)
        request.bind({})
        self.assertEqual('/', request.path)

    def test_ilength(self):
        """ Environ: CONTENT_LENGTH """
        t = dict()
        t[''] = 0
        t['0815'] = 815
        t['-666'] = 0
        t['0'] = 0
        t['a'] = 0
        for k, v in t.iteritems():
            request.bind({'CONTENT_LENGTH': k})
            self.assertEqual(v, request.input_length)
        request.bind({})
        self.assertEqual(0, request.input_length)

    def test_cookie(self):
        """ Environ: COOKIES """ 
        t = dict()
        t['a=a'] = {'a': 'a'}
        t['a=a; b=b'] = {'a': 'a', 'b':'b'}
        t['a=a; a=b'] = {'a': 'b'}
        for k, v in t.iteritems():
            request.bind({'HTTP_COOKIE': k})
            self.assertEqual(v, request.COOKIES)

    def test_get(self):
        """ Environ: GET data """ 
        e = {}
        e['QUERY_STRING'] = 'a=a&a=1&b=b&c=c'
        request.bind(e)
        self.assertTrue('a' in request.GET)
        self.assertTrue('b' in request.GET)
        self.assertTrue(isinstance(request.GET['a'], list))
        self.assertEqual(2, len(request.GET['a']))
        self.assertTrue('a' in request.GET['a'])
        self.assertTrue('1' in request.GET['a'])
        self.assertEqual('b', request.GET['b'])
        
    def test_post(self):
        """ Environ: POST data """ 
        sq = u'a=a&a=1&b=b&c=c'.encode('utf8')
        e = {}
        wsgiref.util.setup_testing_defaults(e)
        e['wsgi.input'].write(sq)
        e['wsgi.input'].seek(0)
        e['CONTENT_LENGTH'] = str(len(sq))
        e['REQUEST_METHOD'] = "POST"
        request.bind(e)
        self.assertTrue('a' in request.POST)
        self.assertTrue('b' in request.POST)
        self.assertTrue(isinstance(request.POST['a'], list))
        self.assertEqual(2, len(request.POST['a']))
        self.assertTrue('a' in request.POST['a'])
        self.assertTrue('1' in request.POST['a'])
        self.assertEqual('b', request.POST['b'])

    def test_getpostleak(self):
        """ Environ: GET and POST shuld not leak into each other """ 
        e = {}
        wsgiref.util.setup_testing_defaults(e)
        e['wsgi.input'].write(u'b=b'.encode('utf8'))
        e['wsgi.input'].seek(0)
        e['CONTENT_LENGTH'] = '3'
        e['QUERY_STRING'] = 'a=a'
        request.bind(e)
        self.assertTrue('b' not in request.GET)
        self.assertTrue('a' not in request.POST)

    def test_body(self):
        """ Environ: Request.body should behave like a file object factory """ 
        e = {}
        wsgiref.util.setup_testing_defaults(e)
        e['wsgi.input'].write(u'abc'.encode('utf8'))
        e['wsgi.input'].seek(0)
        e['CONTENT_LENGTH'] = str(3)
        request.bind(e)
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
        request.bind(e)
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
        request.bind(e)
        self.assertEqual(42, len(request.body.read()))
        self.assertEqual(42, len(request.body.read(1024)))
        self.assertEqual(42, len(request.body.readline()))
        self.assertEqual(42, len(request.body.readline(1024)))

class TestMultipart(unittest.TestCase):
    def test_multipart(self):
        """ Environ: POST (multipart files and multible values per key) """
        fields = [('field1','value1'), ('field2','value2'), ('field2','value3')]
        files = [('file1','filename1.txt','content1'), ('file2','filename2.py',u'äöü')]
        e = tools.multipart_environ(fields=fields, files=files)
        request.bind(e)
        self.assertTrue(e['CONTENT_LENGTH'], request.input_length)
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
        self.assertEqual(u'äöü'.encode('utf8'), x)
        # No file
        self.assertTrue('file3' not in request.POST)
        # Field (single)
        self.assertEqual('value1', request.POST['field1'])
        # Field (multi)
        self.assertEqual(2, len(request.POST['field2']))
        self.assertTrue('value2' in request.POST['field2'])
        self.assertTrue('value3' in request.POST['field2'])

 
suite = unittest.TestSuite()
suite.addTest(unittest.makeSuite(TestEnviron))
suite.addTest(unittest.makeSuite(TestMultipart))

if __name__ == '__main__':
    unittest.main()
