from __future__ import with_statement
from .tools import chdir
import unittest
import sys, os

try:
    import coverage
    coverage.process_startup()
except ImportError:
    pass

import bottle
bottle.debug(True)

