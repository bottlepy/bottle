import sys, os, socket
test_root = os.path.dirname(os.path.abspath(__file__))
os.chdir(test_root)
sys.path.insert(0, os.path.dirname(test_root))
sys.path.insert(0, test_root)

import bottle
from bottle import route, run

if 'coverage' in sys.argv:
    import coverage
    cov = coverage.coverage(data_suffix=True, branch=True)
    cov.start()

@route()
def test():
    return "OK"

if __name__ == '__main__':
    server = sys.argv[1]
    port   = int(sys.argv[2])
    try:
        run(port=port, server=server, quiet=True)
    except socket.error:
        sys.exit(1)
    except ImportError:
        sys.exit(128)
    except KeyboardInterrupt:
        pass

    if 'coverage' in sys.argv:
        cov.stop()
        cov.save()

