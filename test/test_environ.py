import unittest
import sys, os.path
from bottle import request, response
from StringIO import StringIO
import tools



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
        sq = 'a=a&a=1&b=b&c=c'
        e = {}
        e['wsgi.input'] = StringIO(sq)
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
        e['QUERY_STRING'] = 'a=a'
        e['wsgi.input'] = StringIO('b=b')
        request.bind(e)
        self.assertTrue('b' not in request.GET)
        self.assertTrue('a' not in request.POST)


class TestMultipart(unittest.TestCase):
    def test_multipart(self):
        """ Environ: POST (multipart files and multible values per key) """
        fields = [('field1','value1'), ('field2','value2'), ('field2','value3')]
        files = [('file1','filename1.txt','content1'), ('file2','filename2.py','content2')]
        e = tools.multipart_environ(fields=fields, files=files)
        request.bind(e)
        self.assertTrue(e['CONTENT_LENGTH'], request.input_length)
        # File content
        self.assertTrue('file1' in request.POST)
        self.assertEqual('content1', request.POST['file1'].file.read())
        # File name and meta data
        self.assertTrue('file2' in request.POST)
        self.assertEqual('filename2.py', request.POST['file2'].filename)
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
