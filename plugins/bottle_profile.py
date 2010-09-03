# -*- coding: utf-8 -*-
"""
This plugin collects profiling data and displays it in the browser.
To see the stats, add a 'profile' query string parameter to the request URL.

Example::

    import bottle
    bottle.install('profile')

    @bottle.route('/test')
    def test():
        return slow_func_to_profile()

Then call http://.../test?profile in your browser.
...



"""

from __future__ import absolute_import

__autor__ = "Marcel Hellkamp"
__version__ = '0.1'
__licence__ = 'MIT'

import bottle
import cProfile, cStringIO, pstats, threading

class ProfilePlugin(bottle.BasePlugin):
    plugin_name = 'profile'
    def setup(self, app, keyword='profile'):
        self.keyword = keyword
    
    def wrap(self, func):
        def wrapper(*a, **ka):
            if self.keyword in bottle.request.GET:
                p = cProfile.Profile()
                result = p.runcall(func, *a, **ka)
                stream = cStringIO.StringIO()
                stats = pstats.Stats(p, stream=stream)
                stats.sort_stats(bottle.request.GET[self.keyword] or 'time')
                stats.print_stats(25)
                stats.print_callees()
                return '<pre>' + stream.getvalue() + '</pre>'
            else:
                return func(*a, **ka)
        return wrapper
