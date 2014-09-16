if __name__ != '__main__':
    raise ImportError('This is not a module, but a script.')

import sys, os, socket

test_root = os.path.dirname(os.path.abspath(__file__))
os.chdir(test_root)
sys.path.insert(0, os.path.dirname(test_root))
sys.path.insert(0, test_root)

try:
    server = sys.argv[1]
    port   = int(sys.argv[2])

    if server == 'gevent':
        from gevent import monkey
        monkey.patch_all()
    elif server == 'eventlet':
        import eventlet
        eventlet.monkey_patch()

    try:
        import coverage
        coverage.process_startup()
    except ImportError:
        pass

    from bottle import route, run
    route('/test', callback=lambda: 'OK')
    run(port=port, server=server, quiet=True)

except socket.error:
    sys.exit(3)
except ImportError:
    sys.exit(128)
except KeyboardInterrupt:
    pass

