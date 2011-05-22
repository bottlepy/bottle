# -*- coding: utf-8 -*-
import unittest
import sys, os.path
import bottle
from bottle import request, response, tob, tonat, touni
import tools
import wsgiref.util

class TestRequest(unittest.TestCase):
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
        request.bind({'HTTP_HOST':'example.com'})
        self.assertEqual('http://example.com/', request.url)
        request.bind({'SERVER_NAME':'example.com'})
        self.assertEqual('http://example.com/', request.url)
        request.bind({'SERVER_NAME':'example.com', 'SERVER_PORT':'81'})
        self.assertEqual('http://example.com:81/', request.url)
        request.bind({'wsgi.url_scheme':'https', 'SERVER_NAME':'example.com'})
        self.assertEqual('https://example.com/', request.url)
        request.bind({'HTTP_HOST':'example.com', 'PATH_INFO':'/path', 'QUERY_STRING':'1=b&c=d', 'SCRIPT_NAME':'/sp'})
        self.assertEqual('http://example.com/sp/path?1=b&c=d', request.url)
        request.bind({'HTTP_HOST':'example.com', 'PATH_INFO':'/pa th', 'SCRIPT_NAME':'/s p'})
        self.assertEqual('http://example.com/s%20p/pa%20th', request.url)

    def test_dict_access(self):
        """ Environ: request objects are environment dicts """
        e = {}
        wsgiref.util.setup_testing_defaults(e)
        request.bind(e)
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
        request.bind(e)
        request['HTTP_SOME_OTHER_HEADER'] = 'some other value'
        self.assertTrue('Some-Header' in request.headers)
        self.assertTrue(request.header['Some-Header'] == 'some value')
        self.assertTrue(request.header['Some-Other-Header'] == 'some other value')
    
    def test_header_access_special(self):
        e = {}
        wsgiref.util.setup_testing_defaults(e)
        request.bind(e)
        request['CONTENT_TYPE'] = 'test'
        request['CONTENT_LENGTH'] = '123'
        self.assertEqual(request.header['Content-Type'], 'test')
        self.assertEqual(request.header['Content-Length'], '123')

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
        request.bind(e)
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
        request.bind(e)
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
        request.bind(e)
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
        request.bind(e)
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
        request.bind(e)
        self.assertEqual(['a'], request.GET.keys())
        self.assertEqual(['b'], request.POST.keys())

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

    def test_isajax(self):
        e = {}
        wsgiref.util.setup_testing_defaults(e)
        request.bind(e)
        self.assertFalse(request.is_ajax)
        e['HTTP_X_REQUESTED_WITH'] = 'XMLHttpRequest'
        self.assertTrue(request.is_ajax)
        
        
        
class TestResponse(unittest.TestCase):
    def setUp(self):
        response.bind()

    def test_set_cookie(self):
        response.set_cookie('name', 'value', max_age=5)
        response.set_cookie('name2', 'value 2', path='/foo')
        cookies = [value for name, value in response.wsgiheader()
                   if name.title() == 'Set-Cookie']
        cookies.sort()
        self.assertTrue(cookies[0], 'name=value; Max-Age=5')
        self.assertTrue(cookies[1], 'name2="value 2"; Path=/foo')

    def test_delete_cookie(self):
        response.set_cookie('name', 'value')
        response.delete_cookie('name')
        cookies = [value for name, value in response.wsgiheader()
                   if name.title() == 'Set-Cookie']
        self.assertTrue('name=;' in cookies[0])



class TestRedirect(unittest.TestCase):
   
    def assertRedirect(self, target, result, query=None, status=303, **args):
        env = {}
        for key in args:
            if key.startswith('wsgi'):
                args[key.replace('_', '.', 1)] = args[key]
                del args[key]
        env.update(args)
        request.bind(env)
        try:
            bottle.redirect(target, **(query or {}))
        except bottle.HTTPResponse, r:
            self.assertEqual(status, r.status)
            self.assertTrue(r.headers)
            self.assertEqual(result, r.headers['Location'])
                
    def test_root(self):
        self.assertRedirect('/', 'http://127.0.0.1/')
        self.assertRedirect('/test.html', 'http://127.0.0.1/test.html')
        self.assertRedirect('/test.html', 'http://127.0.0.1/test.html',
                            PATH_INFO='/some/sub/path/')
        self.assertRedirect('/test.html', 'http://127.0.0.1/test.html',
                            PATH_INFO='/some/sub/file.html')
        self.assertRedirect('/test.html', 'http://127.0.0.1/test.html',
                            SCRIPT_NAME='/some/sub/path/')
        self.assertRedirect('/foo/test.html', 'http://127.0.0.1/foo/test.html')
        self.assertRedirect('/foo/test.html', 'http://127.0.0.1/foo/test.html',
                            PATH_INFO='/some/sub/file.html')

    def test_relative(self):
        self.assertRedirect('./', 'http://127.0.0.1/')
        self.assertRedirect('./test.html', 'http://127.0.0.1/test.html')
        self.assertRedirect('./test.html', 'http://127.0.0.1/foo/test.html',
                            PATH_INFO='/foo/')
        self.assertRedirect('./test.html', 'http://127.0.0.1/foo/test.html',
                            PATH_INFO='/foo/bar.html')
        self.assertRedirect('./test.html', 'http://127.0.0.1/foo/test.html',
                            SCRIPT_NAME='/foo/')
        self.assertRedirect('./test.html', 'http://127.0.0.1/foo/bar/test.html',
                            SCRIPT_NAME='/foo/', PATH_INFO='/bar/baz.html')
        self.assertRedirect('./foo/test.html', 'http://127.0.0.1/foo/test.html')
        self.assertRedirect('./foo/test.html', 'http://127.0.0.1/bar/foo/test.html',
                            PATH_INFO='/bar/file.html')
        self.assertRedirect('../test.html', 'http://127.0.0.1/test.html',
                            PATH_INFO='/foo/')
        self.assertRedirect('../test.html', 'http://127.0.0.1/foo/test.html',
                            PATH_INFO='/foo/bar/')
        self.assertRedirect('../test.html', 'http://127.0.0.1/test.html',
                            PATH_INFO='/foo/bar.html')
        self.assertRedirect('../test.html', 'http://127.0.0.1/test.html',
                            SCRIPT_NAME='/foo/')
        self.assertRedirect('../test.html', 'http://127.0.0.1/foo/test.html',
                            SCRIPT_NAME='/foo/', PATH_INFO='/bar/baz.html')
        self.assertRedirect('../baz/../test.html', 'http://127.0.0.1/foo/test.html',
                            PATH_INFO='/foo/bar/')
      
    def test_sheme(self):
        self.assertRedirect('./test.html', 'https://127.0.0.1/test.html',
                            wsgi_url_scheme='https')
        self.assertRedirect('./test.html', 'https://127.0.0.1:80/test.html',
                            wsgi_url_scheme='https', SERVER_PORT='80')
                            
    def test_host(self):
        self.assertRedirect('./test.html', 'http://example.com/test.html',
                            HTTP_HOST='example.com')
        self.assertRedirect('./test.html', 'http://example.com/test.html',
                            HTTP_X_FORWARDED_HOST='example.com')
        self.assertRedirect('./test.html', 'http://example.com/test.html',
                            SERVER_NAME='example.com')
        self.assertRedirect('./test.html', 'http://example.com:81/test.html',
                            HTTP_HOST='example.com:81')
        self.assertRedirect('./test.html', 'http://127.0.0.1:81/test.html',
                            SERVER_PORT='81')
        self.assertRedirect('./test.html', 'http://example.com:81/test.html',
                            HTTP_HOST='example.com:81', SERVER_PORT='82')

    def test_specialchars(self):
        ''' The target URL is not quoted automatically. '''
        self.assertRedirect('./te st.html',
                            'http://example.com/a%20a/b%20b/te st.html',
                            HTTP_HOST='example.com', SCRIPT_NAME='/a a/', PATH_INFO='/b b/')
                            
class TestMultipart(unittest.TestCase):
    def test_multipart(self):
        """ Environ: POST (multipart files and multible values per key) """
        fields = [('field1','value1'), ('field2','value2'), ('field2','value3')]
        files = [('file1','filename1.txt','content1'), ('file2','filename2.py',u'ä\nö\rü')]
        e = tools.multipart_environ(fields=fields, files=files)
        request.bind(e)
        # File content
        self.assertTrue('file1' in request.POST)
        cmp = tob('content1') if sys.version_info >= (3,2,0) else 'content1'
        self.assertEqual(cmp, request.POST['file1'].file.read())
        # File name and meta data
        self.assertTrue('file2' in request.POST)
        self.assertEqual('filename2.py', request.POST['file2'].filename)
        # UTF-8 files
        x = request.POST['file2'].file.read()
        if (3,2,0) > sys.version_info >= (3,0,0):
            x = x.encode('ISO-8859-1')
        self.assertEqual(u'ä\nö\rü'.encode('utf8'), x)
        # No file
        self.assertTrue('file3' not in request.POST)
        # Field (single)
        self.assertEqual('value1', request.POST['field1'])
        # Field (multi)
        self.assertEqual(2, len(request.POST.getall('field2')))
        self.assertEqual(['value2', 'value3'], request.POST.getall('field2'))


class TestWSGIHeaderDict(unittest.TestCase):
    def setUp(self):
        self.env = {}
        self.headers = bottle.WSGIHeaderDict(self.env)

    def test_native(self):
        self.env['HTTP_TEST_HEADER'] = 'foobar'
        self.assertEqual(self.headers['Test-header'], 'foobar')

    def test_bytes(self):
        self.env['HTTP_TEST_HEADER'] = tob('foobar')
        self.assertEqual(self.headers['Test-Header'], 'foobar')

    def test_unicode(self):
        self.env['HTTP_TEST_HEADER'] = touni('foobar')
        self.assertEqual(self.headers['Test-Header'], 'foobar')

    def test_dict(self):
        for key in 'foo-bar Foo-Bar foo-Bar FOO-BAR'.split():
            self.assertTrue(key not in self.headers)
            self.assertEqual(self.headers.get(key), None)
            self.assertEqual(self.headers.get(key, 5), 5)
            self.assertRaises(KeyError, lambda x: self.headers[x], key)
        self.env['HTTP_FOO_BAR'] = 'test'
        for key in 'foo-bar Foo-Bar foo-Bar FOO-BAR'.split():
            self.assertTrue(key in self.headers)
            self.assertEqual(self.headers.get(key), 'test')
            self.assertEqual(self.headers.get(key, 5), 'test')



if __name__ == '__main__': #pragma: no cover
    unittest.main()
