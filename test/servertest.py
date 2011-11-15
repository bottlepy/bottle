if __name__ != '__main__':
    raise ImportError('This is not a module, but a script.')

import sys, os, socket
test_root = os.path.dirname(os.path.abspath(__file__))
os.chdir(test_root)
sys.path.insert(0, os.path.dirname(test_root))
sys.path.insert(0, test_root)

if 'coverage' in sys.argv:
    import coverage
    cov = coverage.coverage(data_suffix=True, branch=True)
    cov.start()

try:
    server = sys.argv[1]
    port   = int(sys.argv[2])

    if server == 'gevent':
        from gevent import monkey
        monkey.patch_all()

    from bottle import route, run
    route('/test', callback=lambda: 'OK')
    run(port=port, server=server, quiet=True)

except socket.error:
    sys.exit(1)
except ImportError:
    sys.exit(128)
except KeyboardInterrupt:
    pass
finally:
    if 'coverage' in sys.argv:
        cov.stop()
        cov.save()

