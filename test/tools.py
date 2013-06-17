# -*- coding: utf-8 -*-
import bottle
import sys
import unittest
import wsgiref
import wsgiref.util
import wsgiref.validate

import mimetypes
import uuid

from bottle import tob, BytesIO

def warn(msg):
    sys.stderr.write('WARNING: %s\n' % msg.strip())

def tobs(data):
    ''' Transforms bytes or unicode into a byte stream. '''
    return BytesIO(tob(data))

def api(introduced, deprecated=None, removed=None):
    current    = tuple(map(int, bottle.__version__.split('-')[0].split('.')))
    introduced = tuple(map(int, introduced.split('.')))
    deprecated = tuple(map(int, deprecated.split('.'))) if deprecated else (99,99)
    removed    = tuple(map(int, removed.split('.')))    if removed    else (99,100)
    assert introduced < deprecated < removed

    def decorator(func):
        if   current < introduced:
            return None
        elif current < deprecated:
            return func
        elif current < removed:
            func.__doc__ = '(deprecated) ' + (func.__doc__ or '')
            return func
        else:
            return None
    return decorator

class ServerTestBase(unittest.TestCase):
    def setUp(self):
        ''' Create a new Bottle app set it as default_app '''
        self.port = 8080
        self.host = 'localhost'
        self.app = bottle.app.push()
        self.wsgiapp = wsgiref.validate.validator(self.app)

    def urlopen(self, path, method='GET', post='', env=None):
        result = {'code':0, 'status':'error', 'header':{}, 'body':tob('')}
        def start_response(status, header):
            result['code'] = int(status.split()[0])
            result['status'] = status.split(None, 1)[-1]
            for name, value in header:
                name = name.title()
                if name in result['header']:
                    result['header'][name] += ', ' + value
                else:
                    result['header'][name] = value
        env = env if env else {}
        wsgiref.util.setup_testing_defaults(env)
        env['REQUEST_METHOD'] = method.upper().strip()
        env['PATH_INFO'] = path
        env['QUERY_STRING'] = ''
        if post:
            env['REQUEST_METHOD'] = 'POST'
            env['CONTENT_LENGTH'] = str(len(tob(post)))
            env['wsgi.input'].write(tob(post))
            env['wsgi.input'].seek(0)
        response = self.wsgiapp(env, start_response)
        for part in response:
            try:
                result['body'] += part
            except TypeError:
                raise TypeError('WSGI app yielded non-byte object %s', type(part))
        if hasattr(response, 'close'):
            response.close()
            del response
        return result

    def postmultipart(self, path, fields, files):
        env = multipart_environ(fields, files)
        return self.urlopen(path, method='POST', env=env)

    def tearDown(self):
        bottle.app.pop()

    def assertStatus(self, code, route='/', **kargs):
        self.assertEqual(code, self.urlopen(route, **kargs)['code'])

    def assertBody(self, body, route='/', **kargs):
        self.assertEqual(tob(body), self.urlopen(route, **kargs)['body'])

    def assertInBody(self, body, route='/', **kargs):
        result = self.urlopen(route, **kargs)['body']
        if tob(body) not in result:
            self.fail('The search pattern "%s" is not included in body:\n%s' % (body, result))

    def assertHeader(self, name, value, route='/', **kargs):
        self.assertEqual(value, self.urlopen(route, **kargs)['header'].get(name))

    def assertHeaderAny(self, name, route='/', **kargs):
        self.assertTrue(self.urlopen(route, **kargs)['header'].get(name, None))

    def assertInError(self, search, route='/', **kargs):
        bottle.request.environ['wsgi.errors'].errors.seek(0)
        err = bottle.request.environ['wsgi.errors'].errors.read()
        if search not in err:
            self.fail('The search pattern "%s" is not included in wsgi.error: %s' % (search, err))

def multipart_environ(fields, files):
    boundary = str(uuid.uuid1())
    env = {'REQUEST_METHOD':'POST',
           'CONTENT_TYPE':  'multipart/form-data; boundary='+boundary}
    wsgiref.util.setup_testing_defaults(env)
    boundary = '--' + boundary
    body = ''
    for name, value in fields:
        body += boundary + '\n'
        body += 'Content-Disposition: form-data; name="%s"\n\n' % name
        body += value + '\n'
    for name, filename, content in files:
        mimetype = mimetypes.guess_type(filename)[0] or 'application/octet-stream'
        body += boundary + '\n'
        body += 'Content-Disposition: file; name="%s"; filename="%s"\n' % \
             (name, filename)
        body += 'Content-Type: %s\n\n' % mimetype
        body += content + '\n'
    body += boundary + '--\n'
    if hasattr(body, 'encode'):
        body = body.encode('utf8')
    env['CONTENT_LENGTH'] = str(len(body))
    env['wsgi.input'].write(body)
    env['wsgi.input'].seek(0)
    return env
