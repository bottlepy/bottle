import unittest
import sys, os.path
from bottle import request, response

if sys.version_info[0] == 2:
    from StringIO import StringIO
else:
    from io import StringIO
            
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


    def test_getpost(self):
        """ Environ: GET and POST (simple) """ 
        sq = 'a=a&b=b&c=c'
        qd = {'a':'a', 'b':'b','c':'c'}
        e = {}
        e['wsgi.input']   = sq
        e['QUERY_STRING'] = sq
        request.bind(e)
        self.assertEqual(qd, request.GET)
        self.assertEqual(qd, request.POST)
        self.assertEqual(qd, request.params)

    def test_multigetpost(self):
        """ Environ: GET and POST (multi values) """ 
        sq = 'a=a&a=1'
        qd = {'a':['a','1']}
        e = {}
        e['wsgi.input']   = sq
        e['QUERY_STRING'] = sq
        request.bind(e)
        self.assertEqual(qd, request.GET)
        self.assertEqual(qd, request.POST)
        self.assertEqual(qd, request.params)

    def test_multipart(self):
        """ Environ: POST (multipart files and multible values per key) """

        e = {}
        e['SERVER_PROTOCOL'] = "HTTP/1.1"
        e['REQUEST_METHOD'] = 'POST'
        e['CONTENT_TYPE'] = 'multipart/form-data; boundary=----------------314159265358979323846'
        e['wsgi.input']  = '------------------314159265358979323846\n'
        e['wsgi.input'] += 'Content-Disposition: form-data; name=test.txt; filename=test.txt\n'
        e['wsgi.input'] += 'Content-Type: application/octet-stream; charset=ISO-8859-1\n'
        e['wsgi.input'] += 'Content-Transfer-Encoding: binary\n'
        e['wsgi.input'] += 'This is a test.\n'
        e['wsgi.input'] += '------------------314159265358979323846\n'
        e['wsgi.input'] += 'Content-Disposition: form-data; name=sample.txt; filename=sample.txt\n'
        e['wsgi.input'] += 'Content-Type: text/plain; charset=ISO-8859-1\n'
        e['wsgi.input'] += 'Content-Transfer-Encoding: binary\n'
        e['wsgi.input'] += 'This is a sample\n'
        e['wsgi.input'] += '------------------314159265358979323846\n'
        e['wsgi.input'] += 'Content-Disposition: form-data; name=sample.txt; filename=sample2.txt\n'
        e['wsgi.input'] += 'Content-Type: text/plain; charset=ISO-8859-1\n'
        e['wsgi.input'] += 'Content-Transfer-Encoding: binary\n'
        e['wsgi.input'] += 'This is a second sample\n'
        e['wsgi.input'] += '------------------314159265358979323846--\n'
        e['CONTENT_LENGTH'] = len(e['wsgi.input'])
        e['wsgi.input'] = StringIO(e['wsgi.input'])
        e['wsgi.input'].seek(0)
        request.bind(e)
        self.assertTrue(e['CONTENT_LENGTH'], request.input_length)
        self.assertTrue('test.txt' in request.POST)
        self.assertTrue('sample.txt' in request.POST)
        self.assertEqual('This is a test.', request.POST['test.txt'].file.read())
        self.assertEqual('test.txt', request.POST['test.txt'].filename)
        self.assertEqual(2, len(request.POST['sample.txt']))
        self.assertEqual('This is a sample', request.POST['sample.txt'][0].file.read())
        self.assertEqual('This is a second sample', request.POST['sample.txt'][1].file.read())

 
suite = unittest.TestSuite()
suite.addTest(unittest.makeSuite(TestEnviron))

if __name__ == '__main__':
    unittest.main()
