#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
    import coverage
    coverage.process_startup()
except ImportError:
    pass

import bottle
bottle.debug(True)
