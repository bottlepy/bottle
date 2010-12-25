# -*- coding: utf-8 -*-
import unittest
import bottle
import urllib2
import time
from tools import tob
import sys
import os
import signal
import socket
from subprocess import Popen, PIPE

serverscript = os.path.join(os.path.dirname(__file__), 'servertest.py')

def ping(server, port):
    ''' Check if a server accepts connections on a specific TCP port '''
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((server, port))
        s.close()
        return True
    except socket.error, e:
        return False

class TestServer(unittest.TestCase):
    server = 'wsgiref'

    def setUp(self):
        # Find a free port
        for port in range(8800, 8900):
            self.port = port
            if not ping('127.0.0.1', port): break
        else:
            raise ValueError("Could not find a free port to test networking.")
        # Start servertest.py in a subprocess
        cmd = [sys.executable, serverscript, self.server, str(self.port)]
        cmd += sys.argv[1:] # pass cmdline arguments to subprocesses
        self.p = Popen(cmd, stdout=PIPE, stderr=PIPE)
        # Wait for the socket to accept connections
        for i in xrange(100):
            time.sleep(0.1)
            # Check if the process has died for some reason
            if self.p.poll() != None: break
            if ping('127.0.0.1', self.port): break
        else:
            raise AssertionError("Server took to long to start up.")

    def tearDown(self):
        while self.p.poll() is None:
            os.kill(self.p.pid, signal.SIGINT)
            time.sleep(0.1)
            if self.p.poll() is None:
                os.kill(self.p.pid, signal.SIGTERM)
        for stream in (self.p.stdout, self.p.stderr):
            for line in stream:
                if tob('Warning') in line \
                or tob('Error') in line or True:
                    print line.strip().decode('utf8')

    def fetch(self, url):
        try:
            return urllib2.urlopen('http://127.0.0.1:%d/%s' % (self.port, url)).read()
        except Exception, e:
            return repr(e)

    def test_test(self):
        ''' Test a simple static page with this server adapter. '''
        if self.p.poll() == None:
            self.assertEqual(tob('OK'), self.fetch('test'))
        #else:
        #    self.assertTrue(False, "Server process down")


class TestCherryPyServer(TestServer):
    server = 'cherrypy'

class TestPasteServer(TestServer):
    server = 'paste'

class TestTornadoServer(TestServer):
    server = 'tornado'

class TestTwistedServer(TestServer):
    server = 'twisted'

class TestDieselServer(TestServer):
    server = 'diesel'

class TestGunicornServer(TestServer):
    server = 'gunicorn'

class TestGeventServer(TestServer):
    server = 'gevent'

class TestEventletServer(TestServer):
    server = 'eventlet'

class TestRocketServer(TestServer):
    server = 'rocket'

class TestFapwsServer(TestServer):
    server = 'fapws3'

class TestFapwsServer(TestServer):
    server = 'meinheld'

class TestBjoernServer(TestServer):
    server = 'bjoern'

if __name__ == '__main__': #pragma: no cover
    unittest.main()
