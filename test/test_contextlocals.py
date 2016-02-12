# -*- coding: utf-8 -*-
'''
Some objects are context-local, meaning that they have different values depending on the context they are accessed from. A context is currently defined as a thread.
'''

import unittest
import bottle
import threading


def run_thread(func):
    t = threading.Thread(target=func)
    t.start()
    t.join()

class TestThreadLocals(unittest.TestCase):
    def test_request(self):
        e1 = {'PATH_INFO': '/t1'}
        e2 = {'PATH_INFO': '/t2'}

        def run():
            bottle.request.bind(e2)
            self.assertEqual(bottle.request.path, '/t2')

        bottle.request.bind(e1)
        self.assertEqual(bottle.request.path, '/t1')
        run_thread(run)
        self.assertEqual(bottle.request.path, '/t1')

    def test_response(self):

        def run():
            bottle.response.bind()
            bottle.response.content_type='test/thread'
            self.assertEqual(bottle.response.headers['Content-Type'], 'test/thread')

        bottle.response.bind()
        bottle.response.content_type='test/main'
        self.assertEqual(bottle.response.headers['Content-Type'], 'test/main')
        run_thread(run)
        self.assertEqual(bottle.response.headers['Content-Type'], 'test/main')
