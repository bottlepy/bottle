from __future__ import with_statement
from .tools import chdir
import unittest
import sys, os

try:
    import coverage
    coverage.process_startup()
except ImportError:
    pass


if 'fast' in sys.argv:
    sys.stderr.write("Warning: The 'fast' keyword skipps server tests.\n")
    os.environ["TEST_FAST"] = "true"

import bottle
bottle.debug(True)

