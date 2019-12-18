# -*- coding: utf-8 -*-
import unittest
import time
import sys
import os
import signal
import socket
from subprocess import Popen, PIPE
from . import tools
from bottle import server_names, tob

try:
    from urllib.request import urlopen
except:
    from urllib2 import urlopen

serverscript = os.path.join(os.path.dirname(__file__), 'servertest.py')


def ping(server, port):
    ''' Check if a server accepts connections on a specific TCP port '''
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect((server, port))
        return True
    except socket.error:
        return False
    finally:
        s.close()


class TestServer(unittest.TestCase):
    server = 'wsgiref'
    skip   = False

    def setUp(self):
        self.skip = self.skip or 'fast' in sys.argv
        if self.skip: return
        # Find a free port
        for port in range(8800, 8900):
            self.port = port
            # Start servertest.py in a subprocess
            cmd = [sys.executable, serverscript, self.server, str(port)]
            cmd += sys.argv[1:] # pass cmdline arguments to subprocesses
            self.p = Popen(cmd, stdout=PIPE, stderr=PIPE)
            # Wait for the socket to accept connections
            for i in range(100):
                time.sleep(0.1)
                # Accepts connections?
                if ping('127.0.0.1', port): return
                # Server died for some reason...
                if not self.p.poll() is None: break
            rv = self.p.poll()
            if rv is None:
                raise AssertionError("Server took too long to start up.")
            if rv is 128: # Import error
                if os.environ.get('CI') != 'true' or \
                        os.environ.get('TRAVIS_PYTHON_VERSION') not in ('2.7', '3.6'):
                    tools.warn("Skipping %r test (ImportError)." % self.server)
                    self.skip = True
                    return
            if rv is 3: # Port in use
                continue
            raise AssertionError("Server exited with error code %d" % rv)
        raise AssertionError("Could not find a free port to test server.")

    def tearDown(self):
        if self.skip: return

        if self.p.poll() == None:
            os.kill(self.p.pid, signal.SIGINT)
            time.sleep(0.5)
        if self.p.poll() == None:
            os.kill(self.p.pid, signal.SIGTERM)
            time.sleep(0.5)
        while self.p.poll() == None:
            tools.warn("Trying to kill server %r with pid %d." %
                       (self.server, self.p.pid))
            os.kill(self.p.pid, signal.SIGKILL)
            time.sleep(1)

        lines = [line for stream in (self.p.stdout, self.p.stderr) for line in stream]
        for line in lines:
            if tob('warning') in line.lower():
               tools.warn(line.strip().decode('utf8'))
            elif tob('error') in line.lower():
                raise AssertionError(line.strip().decode('utf8'))

    def fetch(self, url):
        try:
            return urlopen('http://127.0.0.1:%d/%s' % (self.port, url), None, 5).read()
        except Exception as E:
            return repr(E)

    def test_simple(self):
        ''' Test a simple static page with this server adapter. '''
        if self.skip: return
        self.assertEqual(tob('OK'), self.fetch('test'))


blacklist = ['cgi', 'flup', 'gae', 'wsgiref']

if sys.version_info.major == 2:
    blacklist += [
        'aiohttp',
        'uvloop',
    ]
else:
    blacklist += [
        'bjoern',
        'diesel',
        'fapws3',
        'flup',
        'gevent',
    ]


for name in set(server_names) - set(blacklist):
    classname = 'TestServerAdapter_'+name
    setattr(sys.modules[__name__], classname,
            type(classname, (TestServer,), {'server': name}))
