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

logging.basicConfig()
log = logging.getLogger('bottle.starter')

servernames = ['AutoServer']
servernames.extend(x.__name__ for x in bottle.AutoServer.adapters)

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
    if sys.platform == 'win32':
        import win32process
        return win32process.TerminateProcess(process._handle, -1)
    else:
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


def get_modulefiles():
    """ Return all module files currently loaded"""
    files = set()
    for module in sys.modules.values():
        file_path = getattr(module, '__file__', None)
        if file_path and os.path.isfile(file_path):
            file_split = os.path.splitext(file_path)
            if file_split[1] in ('.py', '.pyc', '.pyo'):
                files.add(file_split[0] + '.py')
    return list(files)


def run_child(**runargs):
    """ Run as a child process and check for changed files in a separate thread.
        As soon as a file change is detected, KeyboardInterrupt is thrown in
        the main thread to exit the server loop. """
    watchlist = dict((name, os.stat(name).st_mtime) for name in get_modulefiles())
    lockfile = os.environ.get('BOTTLE_CHILD')
    watchlist[lockfile] = os.stat(lockfile).st_mtime
    changed = set()
    def checker():
        while 1:
            time.sleep(1)
            for path, mtime in watchlist.iteritems():
                if not os.path.exists(path) or mtime != os.stat(path).st_mtime:
                    changed.add(path)
            if changed:
                thread.interrupt_main()
    thread.start_new_thread(checker, tuple(), dict())
    bottle.run(**runargs) # This blocks until KeyboardInterrupt
    if changed:
        log.info("Changed files: %s; Reloading...", ', '.join(changed))
        return 3
    return 0


def run_observer():
    """ The observer loop: Start a child process and wait for it to terminate.
        If the return code equals 3, restart it. Exit otherwise.
        On an exception or SIGTERM, kill the child the hard way. """
    global child
    lockfile = tempfile.NamedTemporaryFile()
    child_argv = [sys.executable] + sys.argv
    child_environ = os.environ.copy()
    child_environ['BOTTLE_CHILD'] = lockfile.name

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
            os.utime(lockfile.name, None) # Not needed at all? wtf?
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
    log.debug("Starting with command line options: %s", ' '.join(argv))
    opt, args = parser.parse_args(argv)

    # Logging
    if opt.log:
        log.addHandler(logging.handlers.FileHandler(opt.log))
        log.debug("Opening logfile %s", opt.logfile)
    else:
        logging.basicConfig()

    # DEBUG mode
    if opt.verbose or opt.debug:
        bottle.debug(True)
        log.setLevel(logging.DEBUG)
        log.debug("Startng in debug mode")

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
    # Arguments for bottle.run()
    runargs = {}
    runargs['server'] = getattr(bottle, opt.server)
    runargs['port'] = int(opt.port)
    runargs['host'] = opt.host

    # First case: We are not reloading a all
    if not opt.reload:
        bottle.run(**runargs)
        return 0

    # Second case: We are a reloading child process
    if os.environ.get('BOTTLE_CHILD'):
        return run_child(**runargs)

    # Third case: We are a reloading observer process
    return run_observer()


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
