# -*- coding: utf-8 -*-
''' Tests for the BaseRequest and BaseResponse objects and their subclasses. '''

import unittest
import sys
import bottle
from bottle import request, tob, touni, tonat, json_dumps, HTTPError, parse_date
from test import tools
import wsgiref.util
import base64

from bottle import BaseRequest, BaseResponse, LocalRequest


class TestRequest(unittest.TestCase):

    def test_app_property(self):
        e = {}
        r = BaseRequest(e)
        self.assertRaises(RuntimeError, lambda: r.app)
        e.update({'bottle.app': 5})
        self.assertEqual(r.app, 5)

    def test_route_property(self):
        e = {'bottle.route': 5}
        r = BaseRequest(e)
        self.assertEqual(r.route, 5)

    def test_url_for_property(self):
        e = {}
        r = BaseRequest(e)
        self.assertRaises(RuntimeError, lambda: r.url_args)
        e.update({'route.url_args': {'a': 5}})
        self.assertEqual(r.url_args, {'a': 5})

    def test_path(self):
        """ PATH_INFO normalization. """
        # Legal paths
        tests = [('', '/'), ('x','/x'), ('x/', '/x/'), ('/x', '/x'), ('/x/', '/x/')]
        for raw, norm in tests:
            self.assertEqual(norm, BaseRequest({'PATH_INFO': raw}).path)
        # Strange paths
        tests = [('///', '/'), ('//x','/x')]
        for raw, norm in tests:
            self.assertEqual(norm, BaseRequest({'PATH_INFO': raw}).path)
        # No path at all
        self.assertEqual('/', BaseRequest({}).path)

    def test_method(self):
        self.assertEqual(BaseRequest({}).method, 'GET')
        self.assertEqual(BaseRequest({'REQUEST_METHOD':'GET'}).method, 'GET')
        self.assertEqual(BaseRequest({'REQUEST_METHOD':'GeT'}).method, 'GET')
        self.assertEqual(BaseRequest({'REQUEST_METHOD':'get'}).method, 'GET')
        self.assertEqual(BaseRequest({'REQUEST_METHOD':'POst'}).method, 'POST')
        self.assertEqual(BaseRequest({'REQUEST_METHOD':'FanTASY'}).method, 'FANTASY')

    def test_script_name(self):
        """ SCRIPT_NAME normalization. """
        # Legal paths
        tests = [('', '/'), ('x','/x/'), ('x/', '/x/'), ('/x', '/x/'), ('/x/', '/x/')]
        for raw, norm in tests:
            self.assertEqual(norm, BaseRequest({'SCRIPT_NAME': raw}).script_name)
        # Strange paths
        tests = [('///', '/'), ('///x///','/x/')]
        for raw, norm in tests:
            self.assertEqual(norm, BaseRequest({'SCRIPT_NAME': raw}).script_name)
        # No path at all
        self.assertEqual('/', BaseRequest({}).script_name)

    def test_pathshift(self):
        """ Request.path_shift() """
        def test_shift(s, p, c):
            request = BaseRequest({'SCRIPT_NAME': s, 'PATH_INFO': p})
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
        request = BaseRequest({'HTTP_HOST':'example.com'})
        self.assertEqual('http://example.com/', request.url)
        request = BaseRequest({'SERVER_NAME':'example.com'})
        self.assertEqual('http://example.com/', request.url)
        request = BaseRequest({'SERVER_NAME':'example.com', 'SERVER_PORT':'81'})
        self.assertEqual('http://example.com:81/', request.url)
        request = BaseRequest({'wsgi.url_scheme':'https', 'SERVER_NAME':'example.com'})
        self.assertEqual('https://example.com/', request.url)
        request = BaseRequest({'HTTP_HOST':'example.com', 'PATH_INFO':'/path',
                               'QUERY_STRING':'1=b&c=d', 'SCRIPT_NAME':'/sp'})
        self.assertEqual('http://example.com/sp/path?1=b&c=d', request.url)
        request = BaseRequest({'HTTP_HOST':'example.com', 'PATH_INFO':'/pa th',
                               'SCRIPT_NAME':'/s p'})
        self.assertEqual('http://example.com/s%20p/pa%20th', request.url)

    def test_dict_access(self):
        """ Environ: request objects are environment dicts """
        e = {}
        wsgiref.util.setup_testing_defaults(e)
        request = BaseRequest(e)
        self.assertEqual(list(request), list(e.keys()))
        self.assertEqual(len(request), len(e))
        for k, v in e.items():
            self.assertTrue(k in request)
            self.assertEqual(request[k], v)
            request[k] = 'test'
            self.assertEqual(request[k], 'test')
        del request['PATH_INFO']
        self.assertTrue('PATH_INFO' not in request)

    def test_readonly_environ(self):
        request = BaseRequest({'bottle.request.readonly':True})
        def test(): request['x']='y'
        self.assertRaises(KeyError, test)

    def test_header_access(self):
        """ Environ: Request objects decode headers """
        e = {}
        wsgiref.util.setup_testing_defaults(e)
        e['HTTP_SOME_HEADER'] = 'some value'
        request = BaseRequest(e)
        request['HTTP_SOME_OTHER_HEADER'] = 'some other value'
        self.assertTrue('Some-Header' in request.headers)
        self.assertTrue(request.headers['Some-Header'] == 'some value')
        self.assertTrue(request.headers['Some-Other-Header'] == 'some other value')

    def test_header_access_special(self):
        e = {}
        wsgiref.util.setup_testing_defaults(e)
        request = BaseRequest(e)
        request['CONTENT_TYPE'] = 'test'
        request['CONTENT_LENGTH'] = '123'
        self.assertEqual(request.headers['Content-Type'], 'test')
        self.assertEqual(request.headers['Content-Length'], '123')

    def test_cookie_dict(self):
        """ Environ: Cookie dict """
        t = dict()
        t['a=a']      = {'a': 'a'}
        t['a=a; b=b'] = {'a': 'a', 'b':'b'}
        t['a=a; a=b'] = {'a': 'b'}
        for k, v in t.items():
            request = BaseRequest({'HTTP_COOKIE': k})
            for n in v:
                self.assertEqual(v[n], request.cookies[n])
                self.assertEqual(v[n], request.get_cookie(n))

    def test_get(self):
        """ Environ: GET data """
        qs = tonat(tob('a=a&a=1&b=b&c=c&cn=%e7%93%b6'), 'latin1')
        request = BaseRequest({'QUERY_STRING':qs})
        self.assertTrue('a' in request.query)
        self.assertTrue('b' in request.query)
        self.assertEqual(['a','1'], request.query.getall('a'))
        self.assertEqual(['b'], request.query.getall('b'))
        self.assertEqual('1', request.query['a'])
        self.assertEqual('b', request.query['b'])
        self.assertEqual(tonat(tob('瓶'), 'latin1'), request.query['cn'])
        self.assertEqual(touni('瓶'), request.query.cn)

    def test_post(self):
        """ Environ: POST data """
        sq = tob('a=a&a=1&b=b&c=&d&cn=%e7%93%b6')
        e = {}
        wsgiref.util.setup_testing_defaults(e)
        e['wsgi.input'].write(sq)
        e['wsgi.input'].seek(0)
        e['CONTENT_LENGTH'] = str(len(sq))
        e['REQUEST_METHOD'] = "POST"
        request = BaseRequest(e)
        self.assertTrue('a' in request.POST)
        self.assertTrue('b' in request.POST)
        self.assertEqual(['a','1'], request.POST.getall('a'))
        self.assertEqual(['b'], request.POST.getall('b'))
        self.assertEqual('1', request.POST['a'])
        self.assertEqual('b', request.POST['b'])
        self.assertEqual('', request.POST['c'])
        self.assertEqual('', request.POST['d'])
        self.assertEqual(tonat(tob('瓶'), 'latin1'), request.POST['cn'])
        self.assertEqual(touni('瓶'), request.POST.cn)

    def test_bodypost(self):
        sq = tob('foobar')
        e = {}
        wsgiref.util.setup_testing_defaults(e)
        e['wsgi.input'].write(sq)
        e['wsgi.input'].seek(0)
        e['CONTENT_LENGTH'] = str(len(sq))
        e['REQUEST_METHOD'] = "POST"
        request = BaseRequest(e)
        self.assertEqual('', request.POST['foobar'])

    def test_body_noclose(self):
        """ Test that the body file handler is not closed after request.POST """
        sq = tob('a=a&a=1&b=b&c=&d')
        e = {}
        wsgiref.util.setup_testing_defaults(e)
        e['wsgi.input'].write(sq)
        e['wsgi.input'].seek(0)
        e['CONTENT_LENGTH'] = str(len(sq))
        e['REQUEST_METHOD'] = "POST"
        request = BaseRequest(e)
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
        request = BaseRequest(e)
        self.assertEqual(['a','b','c'], sorted(request.params.keys()))
        self.assertEqual('p', request.params['c'])

    def test_getpostleak(self):
        """ Environ: GET and POST should not leak into each other """
        e = {}
        wsgiref.util.setup_testing_defaults(e)
        e['wsgi.input'].write(tob('b=b'))
        e['wsgi.input'].seek(0)
        e['CONTENT_LENGTH'] = '3'
        e['QUERY_STRING'] = 'a=a'
        e['REQUEST_METHOD'] = "POST"
        request = BaseRequest(e)
        self.assertEqual(['a'], list(request.GET.keys()))
        self.assertEqual(['b'], list(request.POST.keys()))

    def test_body(self):
        """ Environ: Request.body should behave like a file object factory """
        e = {}
        wsgiref.util.setup_testing_defaults(e)
        e['wsgi.input'].write(tob('abc'))
        e['wsgi.input'].seek(0)
        e['CONTENT_LENGTH'] = str(3)
        request = BaseRequest(e)
        self.assertEqual(tob('abc'), request.body.read())
        self.assertEqual(tob('abc'), request.body.read(3))
        self.assertEqual(tob('abc'), request.body.readline())
        self.assertEqual(tob('abc'), request.body.readline(3))

    def test_bigbody(self):
        """ Environ: Request.body should handle big uploads using files """
        e = {}
        wsgiref.util.setup_testing_defaults(e)
        e['wsgi.input'].write(tob('x')*1024*1000)
        e['wsgi.input'].seek(0)
        e['CONTENT_LENGTH'] = str(1024*1000)
        request = BaseRequest(e)
        self.assertTrue(hasattr(request.body, 'fileno'))
        self.assertEqual(1024*1000, len(request.body.read()))
        self.assertEqual(1024, len(request.body.read(1024)))
        self.assertEqual(1024*1000, len(request.body.readline()))
        self.assertEqual(1024, len(request.body.readline(1024)))

    def test_tobigbody(self):
        """ Environ: Request.body should truncate to Content-Length bytes """
        e = {}
        wsgiref.util.setup_testing_defaults(e)
        e['wsgi.input'].write(tob('x')*1024)
        e['wsgi.input'].seek(0)
        e['CONTENT_LENGTH'] = '42'
        request = BaseRequest(e)
        self.assertEqual(42, len(request.body.read()))
        self.assertEqual(42, len(request.body.read(1024)))
        self.assertEqual(42, len(request.body.readline()))
        self.assertEqual(42, len(request.body.readline(1024)))

    def _test_chunked(self, body, expect):
        e = {}
        wsgiref.util.setup_testing_defaults(e)
        e['wsgi.input'].write(tob(body))
        e['wsgi.input'].seek(0)
        e['HTTP_TRANSFER_ENCODING'] = 'chunked'
        if isinstance(expect, str):
            self.assertEqual(tob(expect), BaseRequest(e).body.read())
        else:
            self.assertRaises(expect, lambda: BaseRequest(e).body)

    def test_chunked(self):
        self._test_chunked('1\r\nx\r\nff\r\n' + 'y'*255 + '\r\n0\r\n',
                           'x' + 'y'*255)
        self._test_chunked('8\r\nxxxxxxxx\r\n0\r\n','xxxxxxxx')
        self._test_chunked('0\r\n', '')

    def test_chunked_meta_fields(self):
        self._test_chunked('8 ; foo\r\nxxxxxxxx\r\n0\r\n','xxxxxxxx')
        self._test_chunked('8;foo\r\nxxxxxxxx\r\n0\r\n','xxxxxxxx')
        self._test_chunked('8;foo=bar\r\nxxxxxxxx\r\n0\r\n','xxxxxxxx')

    def test_chunked_not_terminated(self):
        self._test_chunked('1\r\nx\r\n', HTTPError)

    def test_chunked_wrong_size(self):
        self._test_chunked('2\r\nx\r\n', HTTPError)

    def test_chunked_illegal_size(self):
        self._test_chunked('x\r\nx\r\n', HTTPError)

    def test_chunked_not_chunked_at_all(self):
        self._test_chunked('abcdef', HTTPError)

    def test_multipart(self):
        """ Environ: POST (multipart files and multible values per key) """
        fields = [('field1','value1'), ('field2','value2'), ('field2','value3')]
        files = [('file1','filename1.txt','content1'), ('万难','万难foo.py', 'ä\nö\rü')]
        e = tools.multipart_environ(fields=fields, files=files)
        request = BaseRequest(e)
        # File content
        self.assertTrue('file1' in request.POST)
        self.assertTrue('file1' in request.files)
        self.assertTrue('file1' not in request.forms)
        cmp = tob('content1') if sys.version_info >= (3,2,0) else 'content1'
        self.assertEqual(cmp, request.POST['file1'].file.read())
        # File name and meta data
        self.assertTrue('万难' in request.POST)
        self.assertTrue('万难' in request.files)
        self.assertTrue('万难' not in request.forms)
        self.assertEqual('foo.py', request.POST['万难'].filename)
        self.assertTrue(request.files['万难'])
        self.assertFalse(request.files.file77)
        # UTF-8 files
        x = request.POST['万难'].file.read()
        if (3,2,0) > sys.version_info >= (3,0,0):
            x = x.encode('utf8')
        self.assertEqual(tob('ä\nö\rü'), x)
        # No file
        self.assertTrue('file3' not in request.POST)
        self.assertTrue('file3' not in request.files)
        self.assertTrue('file3' not in request.forms)
        # Field (single)
        self.assertEqual('value1', request.POST['field1'])
        self.assertTrue('field1' not in request.files)
        self.assertEqual('value1', request.forms['field1'])
        # Field (multi)
        self.assertEqual(2, len(request.POST.getall('field2')))
        self.assertEqual(['value2', 'value3'], request.POST.getall('field2'))
        self.assertEqual(['value2', 'value3'], request.forms.getall('field2'))
        self.assertTrue('field2' not in request.files)

    def test_json_empty(self):
        """ Environ: Request.json property with empty body. """
        self.assertEqual(BaseRequest({}).json, None)

    def test_json_noheader(self):
        """ Environ: Request.json property with missing content-type header. """
        test = dict(a=5, b='test', c=[1,2,3])
        e = {}
        wsgiref.util.setup_testing_defaults(e)
        e['wsgi.input'].write(tob(json_dumps(test)))
        e['wsgi.input'].seek(0)
        e['CONTENT_LENGTH'] = str(len(json_dumps(test)))
        self.assertEqual(BaseRequest(e).json, None)

    def test_json_tobig(self):
        """ Environ: Request.json property with huge body. """
        test = dict(a=5, tobig='x' * bottle.BaseRequest.MEMFILE_MAX)
        e = {'CONTENT_TYPE': 'application/json'}
        wsgiref.util.setup_testing_defaults(e)
        e['wsgi.input'].write(tob(json_dumps(test)))
        e['wsgi.input'].seek(0)
        e['CONTENT_LENGTH'] = str(len(json_dumps(test)))
        self.assertRaises(HTTPError, lambda: BaseRequest(e).json)

    def test_json_valid(self):
        """ Environ: Request.json property. """
        test = dict(a=5, b='test', c=[1,2,3])
        e = {'CONTENT_TYPE': 'application/json; charset=UTF-8'}
        wsgiref.util.setup_testing_defaults(e)
        e['wsgi.input'].write(tob(json_dumps(test)))
        e['wsgi.input'].seek(0)
        e['CONTENT_LENGTH'] = str(len(json_dumps(test)))
        self.assertEqual(BaseRequest(e).json, test)

    def test_json_forged_header_issue616(self):
        test = dict(a=5, b='test', c=[1,2,3])
        e = {'CONTENT_TYPE': 'text/plain;application/json'}
        wsgiref.util.setup_testing_defaults(e)
        e['wsgi.input'].write(tob(json_dumps(test)))
        e['wsgi.input'].seek(0)
        e['CONTENT_LENGTH'] = str(len(json_dumps(test)))
        self.assertEqual(BaseRequest(e).json, None)

    def test_json_header_empty_body(self):
        """Request Content-Type is application/json but body is empty"""
        e = {'CONTENT_TYPE': 'application/json'}
        wsgiref.util.setup_testing_defaults(e)
        wsgiref.util.setup_testing_defaults(e)
        e['CONTENT_LENGTH'] = "0"
        self.assertEqual(BaseRequest(e).json, None)

    def test_isajax(self):
        e = {}
        wsgiref.util.setup_testing_defaults(e)
        self.assertFalse(BaseRequest(e.copy()).is_ajax)
        e['HTTP_X_REQUESTED_WITH'] = 'XMLHttpRequest'
        self.assertTrue(BaseRequest(e.copy()).is_ajax)

    def test_auth(self):
        user, pwd = 'marc', 'secret'
        basic = touni(base64.b64encode(tob('%s:%s' % (user, pwd))))
        r = BaseRequest({})
        self.assertEqual(r.auth, None)
        r.environ['HTTP_AUTHORIZATION'] = 'basic %s' % basic
        self.assertEqual(r.auth, (user, pwd))
        r.environ['REMOTE_USER'] = user
        self.assertEqual(r.auth, (user, pwd))
        del r.environ['HTTP_AUTHORIZATION']
        self.assertEqual(r.auth, (user, None))

    def test_remote_route(self):
        ips = ['1.2.3.4', '2.3.4.5', '3.4.5.6']
        r = BaseRequest({})
        self.assertEqual(r.remote_route, [])
        r.environ['HTTP_X_FORWARDED_FOR'] = ', '.join(ips)
        self.assertEqual(r.remote_route, ips)
        r.environ['REMOTE_ADDR'] = ips[1]
        self.assertEqual(r.remote_route, ips)
        del r.environ['HTTP_X_FORWARDED_FOR']
        self.assertEqual(r.remote_route, [ips[1]])

    def test_remote_addr(self):
        ips = ['1.2.3.4', '2.3.4.5', '3.4.5.6']
        r = BaseRequest({})
        self.assertEqual(r.remote_addr, None)
        r.environ['HTTP_X_FORWARDED_FOR'] = ', '.join(ips)
        self.assertEqual(r.remote_addr, ips[0])
        r.environ['REMOTE_ADDR'] = ips[1]
        self.assertEqual(r.remote_addr, ips[0])
        del r.environ['HTTP_X_FORWARDED_FOR']
        self.assertEqual(r.remote_addr, ips[1])

    def test_user_defined_attributes(self):
        for cls in (BaseRequest, LocalRequest):
            r = cls()

            # New attributes go to the environ dict.
            r.foo = 'somevalue'
            self.assertEqual(r.foo, 'somevalue')
            self.assertTrue('somevalue' in r.environ.values())

            # Attributes are read-only once set.
            self.assertRaises(AttributeError, setattr, r, 'foo', 'x')

            # Unknown attributes raise AttributeError.
            self.assertRaises(AttributeError, getattr, r, 'somevalue')


class TestResponse(unittest.TestCase):

    def test_constructor_body(self):
        self.assertEqual('',
            BaseResponse('').body)

        self.assertEqual('YAY',
            BaseResponse('YAY').body)

    def test_constructor_status(self):
        self.assertEqual(200,
            BaseResponse('YAY', 200).status_code)

        self.assertEqual('200 OK',
            BaseResponse('YAY', 200).status_line)

        self.assertEqual('200 YAY',
            BaseResponse('YAY', '200 YAY').status_line)

        self.assertEqual('200 YAY',
            BaseResponse('YAY', '200 YAY').status_line)

    def test_constructor_headerlist(self):
        from functools import partial
        make_res = partial(BaseResponse, '', 200)

        self.assertEquals('yay', make_res(x_test='yay')['x-test'])

    def test_wsgi_header_values(self):
        def cmp(app, wire):
            rs = BaseResponse()
            rs.set_header('x-test', app)
            result = [v for (h, v) in rs.headerlist if h.lower()=='x-test'][0]
            self.assertEquals(wire, result)

        if bottle.py3k:
            cmp(1, tonat('1', 'latin1'))
            cmp('öäü', 'öäü'.encode('utf8').decode('latin1'))
            # Dropped byte header support in Python 3:
            #cmp(tob('äöü'), 'äöü'.encode('utf8').decode('latin1'))
        else:
            cmp(1, '1')
            cmp('öäü', 'öäü')
            cmp(touni('äöü'), 'äöü')

    def test_set_status(self):
        rs = BaseResponse()

        rs.status = 200
        self.assertEqual(rs.status, rs.status_line)
        self.assertEqual(rs.status_code, 200)
        self.assertEqual(rs.status_line, '200 OK')

        rs.status = 999
        self.assertEqual(rs.status, rs.status_line)
        self.assertEqual(rs.status_code, 999)
        self.assertEqual(rs.status_line, '999 Unknown')

        rs.status = 404
        self.assertEqual(rs.status, rs.status_line)
        self.assertEqual(rs.status_code, 404)
        self.assertEqual(rs.status_line, '404 Not Found')

        def test(): rs.status = -200
        self.assertRaises(ValueError, test)
        self.assertEqual(rs.status, rs.status_line) # last value
        self.assertEqual(rs.status_code, 404) # last value
        self.assertEqual(rs.status_line, '404 Not Found') # last value

        def test(): rs.status = 5
        self.assertRaises(ValueError, test)
        self.assertEqual(rs.status, rs.status_line) # last value
        self.assertEqual(rs.status_code, 404) # last value
        self.assertEqual(rs.status_line, '404 Not Found') # last value

        rs.status = '999 Who knows?' # Illegal, but acceptable three digit code
        self.assertEqual(rs.status, rs.status_line)
        self.assertEqual(rs.status_code, 999)
        self.assertEqual(rs.status_line, '999 Who knows?')

        rs.status = 555 # Strange code
        self.assertEqual(rs.status, rs.status_line)
        self.assertEqual(rs.status_code, 555)
        self.assertEqual(rs.status_line, '555 Unknown')

        rs.status = '404 Brain not Found' # Custom reason
        self.assertEqual(rs.status, rs.status_line)
        self.assertEqual(rs.status_code, 404)
        self.assertEqual(rs.status_line, '404 Brain not Found')

        def test(): rs.status = '5 Illegal Code'
        self.assertRaises(ValueError, test)
        self.assertEqual(rs.status, rs.status_line) # last value
        self.assertEqual(rs.status_code, 404) # last value
        self.assertEqual(rs.status_line, '404 Brain not Found') # last value

        def test(): rs.status = '-99 Illegal Code'
        self.assertRaises(ValueError, test)
        self.assertEqual(rs.status, rs.status_line) # last value
        self.assertEqual(rs.status_code, 404) # last value
        self.assertEqual(rs.status_line, '404 Brain not Found') # last value

        def test(): rs.status = '1000 Illegal Code'
        self.assertRaises(ValueError, test)
        self.assertEqual(rs.status, rs.status_line) # last value
        self.assertEqual(rs.status_code, 404) # last value
        self.assertEqual(rs.status_line, '404 Brain not Found') # last value

        def test(): rs.status = '555' # No reason
        self.assertRaises(ValueError, test)
        self.assertEqual(rs.status, rs.status_line) # last value
        self.assertEqual(rs.status_code, 404) # last value
        self.assertEqual(rs.status_line, '404 Brain not Found') # last value

    def test_content_type(self):
        rs = BaseResponse()
        rs.content_type = 'test/some'
        self.assertEqual('test/some', rs.headers.get('Content-Type'))

    def test_charset(self):
        rs = BaseResponse()
        self.assertEqual(rs.charset, 'UTF-8')
        rs.content_type = 'text/html; charset=latin9'
        self.assertEqual(rs.charset, 'latin9')
        rs.content_type = 'text/html'
        self.assertEqual(rs.charset, 'UTF-8')

    def test_set_cookie(self):
        r = BaseResponse()
        r.set_cookie('name1', 'value', max_age=5)
        r.set_cookie('name2', 'value 2', path='/foo')
        cookies = [value for name, value in r.headerlist
                   if name.title() == 'Set-Cookie']
        cookies.sort()
        self.assertEqual(cookies[0], 'name1=value; Max-Age=5')
        self.assertEqual(cookies[1], 'name2="value 2"; Path=/foo')

    def test_set_cookie_value_long_string(self):
        r = BaseResponse()
        self.assertRaises(ValueError, r.set_cookie, name='test', value='x' * 4097)

    def test_set_cookie_name_long_string(self):
        r = BaseResponse()
        self.assertRaises(ValueError, r.set_cookie, name='x' * 4097, value='simple_value')

    def test_set_cookie_maxage(self):
        import datetime
        r = BaseResponse()
        r.set_cookie('name1', 'value', max_age=5)
        r.set_cookie('name2', 'value', max_age=datetime.timedelta(days=1))
        cookies = sorted([value for name, value in r.headerlist
                   if name.title() == 'Set-Cookie'])
        self.assertEqual(cookies[0], 'name1=value; Max-Age=5')
        self.assertEqual(cookies[1], 'name2=value; Max-Age=86400')

    def test_set_cookie_expires(self):
        import datetime
        r = BaseResponse()
        r.set_cookie('name1', 'value', expires=42)
        r.set_cookie('name2', 'value', expires=datetime.datetime(1970,1,1,0,0,43))
        cookies = sorted([value for name, value in r.headerlist
                   if name.title() == 'Set-Cookie'])
        self.assertEqual(cookies[0], 'name1=value; expires=Thu, 01 Jan 1970 00:00:42 GMT')
        self.assertEqual(cookies[1], 'name2=value; expires=Thu, 01 Jan 1970 00:00:43 GMT')

    def test_set_cookie_secure(self):
        r = BaseResponse()
        r.set_cookie('name1', 'value', secure=True)
        r.set_cookie('name2', 'value', secure=False)
        cookies = sorted([value for name, value in r.headerlist
                   if name.title() == 'Set-Cookie'])
        self.assertEqual(cookies[0].lower(), 'name1=value; secure')
        self.assertEqual(cookies[1], 'name2=value')

    def test_set_cookie_httponly(self):
        if sys.version_info < (2,6,0):
            return
        r = BaseResponse()
        r.set_cookie('name1', 'value', httponly=True)
        r.set_cookie('name2', 'value', httponly=False)
        cookies = sorted([value for name, value in r.headerlist
                   if name.title() == 'Set-Cookie'])
        self.assertEqual(cookies[0].lower(), 'name1=value; httponly')
        self.assertEqual(cookies[1], 'name2=value')

    def test_delete_cookie(self):
        response = BaseResponse()
        response.set_cookie('name', 'value')
        response.delete_cookie('name')
        cookies = [value for name, value in response.headerlist
                   if name.title() == 'Set-Cookie']
        self.assertTrue('Max-Age=-1' in cookies[0])

    def test_set_header(self):
        response = BaseResponse()
        response['x-test'] = 'foo'
        headers = [value for name, value in response.headerlist
                   if name.title() == 'X-Test']
        self.assertEqual(['foo'], headers)
        self.assertEqual('foo', response['x-test'])

        response['X-Test'] = 'bar'
        headers = [value for name, value in response.headerlist
                   if name.title() == 'X-Test']
        self.assertEqual(['bar'], headers)
        self.assertEqual('bar', response['x-test'])

    def test_append_header(self):
        response = BaseResponse()
        response.set_header('x-test', 'foo')
        headers = [value for name, value in response.headerlist
                   if name.title() == 'X-Test']
        self.assertEqual(['foo'], headers)
        self.assertEqual('foo', response['x-test'])

        response.add_header('X-Test', 'bar')
        headers = [value for name, value in response.headerlist
                   if name.title() == 'X-Test']
        self.assertEqual(['foo', 'bar'], headers)
        self.assertEqual('bar', response['x-test'])

    def test_delete_header(self):
        response = BaseResponse()
        response['x-test'] = 'foo'
        self.assertEqual('foo', response['x-test'])
        del response['X-tESt']
        self.assertRaises(KeyError, lambda: response['x-test'])

    def test_non_string_header(self):
        response = BaseResponse()
        response['x-test'] = 5
        self.assertEqual('5', response['x-test'])
        response['x-test'] = None
        self.assertEqual('None', response['x-test'])

    def test_expires_header(self):
        import datetime
        response = BaseResponse()
        now = datetime.datetime.now()
        response.expires = now

        def seconds(a, b):
            td = max(a,b) - min(a,b)
            return td.days*360*24 + td.seconds

        self.assertEqual(0, seconds(response.expires, now))
        now2 = datetime.datetime.utcfromtimestamp(
            parse_date(response.headers['Expires']))
        self.assertEqual(0, seconds(now, now2))


class TestRedirect(unittest.TestCase):

    def assertRedirect(self, target, result, query=None, status=303, **args):
        env = {'SERVER_PROTOCOL': 'HTTP/1.1'}
        for key in list(args):
            if key.startswith('wsgi'):
                args[key.replace('_', '.', 1)] = args[key]
                del args[key]
        env.update(args)
        request.bind(env)
        bottle.response.bind()
        try:
            bottle.redirect(target, **(query or {}))
        except bottle.HTTPResponse as E:
            self.assertEqual(status, E.status_code)
            self.assertTrue(E.headers)
            self.assertEqual(result, E.headers['Location'])

    def test_absolute_path(self):
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

    def test_relative_path(self):
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

    def test_host_http_1_0(self):
        # No HTTP_HOST, just SERVER_NAME and SERVER_PORT.
        self.assertRedirect('./test.html', 'http://example.com/test.html',
                            SERVER_NAME='example.com',
                            SERVER_PROTOCOL='HTTP/1.0', status=302)
        self.assertRedirect('./test.html', 'http://127.0.0.1:81/test.html',
                            SERVER_PORT='81',
                            SERVER_PROTOCOL='HTTP/1.0', status=302)

    def test_host_http_1_1(self):
        self.assertRedirect('./test.html', 'http://example.com/test.html',
                            HTTP_HOST='example.com')
        self.assertRedirect('./test.html', 'http://example.com:81/test.html',
                            HTTP_HOST='example.com:81')
        # Trust HTTP_HOST over SERVER_NAME and PORT.
        self.assertRedirect('./test.html', 'http://example.com:81/test.html',
                            HTTP_HOST='example.com:81', SERVER_NAME='foobar')
        self.assertRedirect('./test.html', 'http://example.com:81/test.html',
                            HTTP_HOST='example.com:81', SERVER_PORT='80')

    def test_host_http_proxy(self):
        # Trust proxy headers over original header.
        self.assertRedirect('./test.html', 'http://example.com/test.html',
                            HTTP_X_FORWARDED_HOST='example.com',
                            HTTP_HOST='127.0.0.1')

    def test_specialchars(self):
        ''' The target URL is not quoted automatically. '''
        self.assertRedirect('./te st.html',
                            'http://example.com/a%20a/b%20b/te st.html',
                            HTTP_HOST='example.com', SCRIPT_NAME='/a a/', PATH_INFO='/b b/')

    def test_redirect_preserve_cookies(self):
        env = {'SERVER_PROTOCOL':'HTTP/1.1'}
        request.bind(env)
        bottle.response.bind()
        try:
            bottle.response.set_cookie('xxx', 'yyy')
            bottle.redirect('...')
        except bottle.HTTPResponse as E:
            h = [v for (k, v) in E.headerlist if k == 'Set-Cookie']
            self.assertEqual(h, ['xxx=yyy'])

class TestWSGIHeaderDict(unittest.TestCase):
    def setUp(self):
        self.env = {}
        self.headers = bottle.WSGIHeaderDict(self.env)

    def test_empty(self):
        self.assertEqual(0, len(bottle.WSGIHeaderDict({})))

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
