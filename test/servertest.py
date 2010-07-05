import sys, os
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
    server = getattr(bottle, sys.argv[1])
    port   = int(sys.argv[2])
    try:
        run(port=port, server=server)
    except ImportError:
        print "Warning: Could not test %s. Import error." % server

    if 'coverage' in sys.argv:
        cov.stop()
        cov.save()

