import unittest
import sys, os.path
import bottle
import urllib2
from StringIO import StringIO
import thread
import time
from tools import ServerTestBase
from bottle import tob, touni, tonat, Bottle

class TestWsgi(ServerTestBase):
    ''' Tests sub-application support. '''
    
    def test_mount_no_plugins(self):
        def plugin(func):
            def wrapper(*a, **ka):
                return 'Plugin'
            return wrapper
        self.app.install(plugin)
        app = Bottle()
        self.app.mount(app, '/prefix')
        app.route('/foo', callback=lambda: 'bar')
        self.app.route('/foo', callback=lambda: 'baz')
        self.assertBody('Plugin', '/foo')
        self.assertBody('bar', '/prefix/foo')

if __name__ == '__main__': #pragma: no cover
    unittest.main()
