# -*- coding: utf-8 -*-
""" This is a command line tool to load and serve bottle.py web applications.
"""

import bottle
import logging
import sys
from optparse import OptionParser
import os
import subprocess
import time
import thread
import tempfile
import inspect

logging.basicConfig()
log = logging.getLogger('bottle.starter')

servernames = ['AutoServer']
servernames.extend(x.__name__ for x in bottle.AutoServer.adapters)
reloading_servernames = ['WSGIRefServer']


parser = OptionParser(usage="usage: %prog [options] module1 [module2 ...]")
parser.add_option("-s", "--server",
    type="choice",
    choices=servernames,
    default=servernames[0],
    help='Server backend: %s (default), %s or %s'
        % (servernames[0], ", ".join(servernames[1:-1]), servernames[-1]))
parser.add_option("-a", "--host",
    default='localhost',
    help="Host address or name to bind to (default: localhost)")
parser.add_option("-r", "--reload",
    default=False,
    action='store_true',
    help="Use auto reloading? (default: off)")
parser.add_option("-p", "--port",
    type="int",
    default=8080,
    help="TCP Port to bind to (default: 8080)")
parser.add_option("-l", "--log",
    help="Path to the logfile (default: stderr)")
parser.add_option("-d", "--debug",
    action="store_true",
    help="Log debug messages and include a stacktrace to HTTP-500 error pages (dangerous on public servers)")
parser.add_option("-v", "--verbose",
    action="store_true",
    help="Same as -d")


def terminate(process):
    """ Kills a subprocess. """
    if hasattr(process, 'terminate'):
        return process.terminate()
    try:
        import win32process
        return win32process.TerminateProcess(process._handle, -1)
    except ImportError:
        import os
        import signal
        return os.kill(process.pid, signal.SIGTERM)


def set_exit_handler(func):
    try:
        import win32api
        win32api.SetConsoleCtrlHandler(func, True)
    except ImportError:
        import signal
        signal.signal(signal.SIGTERM, func)


class ModuleChecker(object):
    def __init__(self):
        self.files = {}
        self.changed = []
        for module in sys.modules.values():
            try:
                path = inspect.getsourcefile(module)
                self.add(path)
            except TypeError:
                continue

    def add(self, path):
        self.files[path] = self.mtime(path)

    def mtime(self, path):
        return os.path.getmtime(path) if os.path.exists(path) else 0

    def check(self):
        for path, mtime in self.files.iteritems():
            newtime = self.mtime(path)
            if mtime != newtime:
                self.changed.append(path)
                self.files[path] = newtime
        return self.changed

    def reset(self):
        self.changed = []

    def loop(self, interval, callback):
        while not self.check():
            time.sleep(interval)
        callback()


def run_child(**runargs):
    """ Run as a child process and check for changed files in a separate thread.
        As soon as a file change is detected, KeyboardInterrupt is thrown in
        the main thread to exit the server loop. """
    checker = ModuleChecker()
    thread.start_new_thread(checker.loop, (1, thread.interrupt_main), {})
    bottle.run(**runargs) # This blocks until KeyboardInterrupt
    if checker.changed:
        log.info("Changed files: %s; Reloading...", ', '.join(checker.changed))
        return 3
    return 0


def run_observer():
    """ The observer loop: Start a child process and wait for it to terminate.
        If the return code equals 3, restart it. Exit otherwise.
        On an exception or SIGTERM, kill the child the hard way. """
    global child
    child_argv = [sys.executable] + sys.argv
    child_environ = os.environ.copy()
    child_environ['BOTTLE_CHILD'] = 'true'

    def onexit(*argv):
        if child.poll() == None:
            terminate(child)

    set_exit_handler(onexit)

    while True: # Child restart loop
        child = subprocess.Popen(child_argv, env=child_environ)
        try:
            code = child.wait()
            if code != 3:
                log.info("Child terminated with exit code %d. We do the same", code)
                return code
        except KeyboardInterrupt:
            log.info("User exit. Waiting for Child to terminate...")
            return child.wait()
        except OSError, e:
            # This happens on SIGTERM during child.wait(). We ignore it
            onexit()
            return child.wait()
        except Exception, e:
            onexit()
            log.exception("Uh oh...")
            raise


def main(argv):
    opt, args = parser.parse_args(argv)

    # Logging
    if opt.log:
        log.addHandler(logging.handlers.FileHandler(opt.log))
    else:
        logging.basicConfig()

    # DEBUG mode
    if opt.verbose or opt.debug:
        bottle.debug(True)
        log.setLevel(logging.DEBUG)

    # Importing modules
    sys.path.append('./')
    if not args:
        log.error("No modules specified")
        return 1
    for mod in args:
        try:
            __import__(mod)
        except ImportError:
            log.exception("Failed to import module '%s' (ImportError)", mod)
            return 1
    
    # First case: We are a reloading observer process
    if opt.reload and not os.environ.get('BOTTLE_CHILD'):
        return run_observer()

    # Arguments for bottle.run()
    runargs = {}
    runargs['server'] = getattr(bottle, opt.server) 
    runargs['port'] = int(opt.port)
    runargs['host'] = opt.host

    # Second case: We are a reloading child process
    if os.environ.get('BOTTLE_CHILD'):
        if runargs['server'] != bottle.WSGIRefServer:
            log.warning("Currently only WSGIRefServer is known to support reloading")
            runargs['server'] = bottle.WSGIRefServer
        return run_child(**runargs)

    # Third case: We are not reloading a all
    bottle.run(**runargs)
    return 0




if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
