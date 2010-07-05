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
    ''' Check if a server acccepts connections on a specific TCP port '''
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((server, port))
        s.close()
        return True
    except socket.error, e:
        return False

class TestServer(unittest.TestCase):
    server = 'WSGIRefServer'
    port = 12643

    def setUp(self):
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

    def tearDown(self):
        while self.p.poll() is None:
            os.kill(self.p.pid, signal.SIGINT)
            time.sleep(0.1)
            if self.p.poll() is None:
                os.kill(self.p.pid, signal.SIGTERM)
        for stream in (self.p.stdout, self.p.stderr):
            for line in stream:
                if tob('Warning') in line \
                or tob('Error') in line:
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
    server = 'CherryPyServer'

class TestPasteServer(TestServer):
    server = 'PasteServer'

class TestTornadoServer(TestServer):
    server = 'TornadoServer'

class TestTwistedServer(TestServer):
    server = 'TwistedServer'

class TestDieselServer(TestServer):
    server = 'DieselServer'

class TestGunicornServer(TestServer):
    server = 'GunicornServer'

class TestGeventServer(TestServer):
    server = 'GeventServer'

class TestEventletServer(TestServer):
    server = 'EventletServer'

class TestRocketServer(TestServer):
    server = 'RocketServer'

class TestFapwsServer(TestServer):
    server = 'FapwsServer'

if __name__ == '__main__': #pragma: no cover
    unittest.main()
