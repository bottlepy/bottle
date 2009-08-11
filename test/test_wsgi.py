import unittest
import sys, os.path
import bottle
from wsgiref.util import setup_testing_defaults



def wsgi_status(**kargs):
    return test_all(**kargs)[0]

def wsgi_header(**kargs):
    return test_all(**kargs)[1]
    
def wsgi_body(**kargs):
    return test_all(**kargs)[2]

            
class TestWsgi(unittest.TestCase):

    def setUp(self):
        self.wsgi = bottle.Bottle()

    def simulate(self, url, **kargs):
        environ = {}
        meta = {}
        out = ''
        url = url.split('?')
        environ['PATH_INFO'] = url[0]
        if len(url) > 1: environ['QUERY_STRING'] = url[1]
        environ.update(kargs)
        setup_testing_defaults(environ)
        def start_response(status, header):
            meta['status'] = int(status.split()[0])
            meta['header'] = dict(header)
        for part in self.wsgi(environ, start_response):
            out += part
        return meta['status'], meta['header'], out

    def test_404(self):
        """ WSGI: 404 """
        self.wsgi.add_route('/post/only', lambda: 'test', method='POST')
        self.assertEqual(404, self.simulate('/not/found')[0])
        self.assertEqual(404, self.simulate('/post/only')[0])
        
    def test_500(self):
        """ WSGI: 500 """
        self.wsgi.add_route('/error/500', lambda: 1/0)
        self.assertEqual(500, self.simulate('/error/500')[0])
        
    def test_200(self):
        """ WSGI: 200 """
        self.wsgi.add_route('/page1', lambda: 'test')
        self.wsgi.add_route('/page2', lambda: ['t','e','st'])
        self.assertEqual(200, self.simulate('/page1')[0])
        self.assertEqual(200, self.simulate('/page2')[0])
        self.assertEqual('test', self.simulate('/page1')[2])
        self.assertEqual('test', self.simulate('/page2')[2])
     
    def test_json(self):
        """ WSGI: json """
        self.wsgi.add_route('/json', lambda: {'a':1})
        self.assertEqual(200, self.simulate('/json')[0])
        self.assertEqual('application/json', self.simulate('/json')[1].get('Content-Type',''))
        self.assertEqual(r'{"a": 1}', self.simulate('/json')[2])


suite = unittest.TestSuite()
suite.addTest(unittest.makeSuite(TestWsgi))

if __name__ == '__main__':
    unittest.main()
