# -*- coding: utf-8 -*-
import unittest
import time
import threading

import bottle
from bottle import tob, Session, SessionStore, SessionPlugin
from .tools import ServerTestBase


class TestSession(unittest.TestCase):
    """ Tests for the Session UserDict subclass. """

    def test_dict_access(self):
        s = Session('abc123')
        s['key'] = 'value'
        self.assertEqual(s['key'], 'value')
        self.assertIn('key', s)
        self.assertEqual(len(s), 1)

    def test_get_default(self):
        s = Session('abc123')
        self.assertIsNone(s.get('missing'))
        self.assertEqual(s.get('missing', 42), 42)

    def test_init_with_data(self):
        s = Session('abc123', {'a': 1, 'b': 2})
        self.assertEqual(s['a'], 1)
        self.assertEqual(s['b'], 2)
        self.assertEqual(len(s), 2)

    def test_modified_on_setitem(self):
        s = Session('abc123')
        self.assertFalse(s.modified)
        s['key'] = 'value'
        self.assertTrue(s.modified)

    def test_modified_on_delitem(self):
        s = Session('abc123', {'key': 'value'})
        s._modified = False
        del s['key']
        self.assertTrue(s.modified)

    def test_modified_on_pop(self):
        s = Session('abc123', {'key': 'value'})
        s._modified = False
        s.pop('key')
        self.assertTrue(s.modified)

    def test_modified_on_update(self):
        s = Session('abc123')
        s._modified = False
        s.update({'a': 1})
        self.assertTrue(s.modified)

    def test_modified_on_setdefault_new_key(self):
        s = Session('abc123')
        s._modified = False
        s.setdefault('key', 'default')
        self.assertTrue(s.modified)

    def test_modified_on_setdefault_existing_key(self):
        s = Session('abc123', {'key': 'value'})
        s._modified = False
        s.setdefault('key', 'other')
        self.assertFalse(s.modified)

    def test_modified_on_clear(self):
        s = Session('abc123', {'key': 'value'})
        s._modified = False
        s.clear()
        self.assertTrue(s.modified)
        self.assertEqual(len(s), 0)

    def test_touch_updates_accessed(self):
        s = Session('abc123')
        first = s._accessed
        time.sleep(0.01)
        s.touch()
        self.assertGreater(s._accessed, first)

    def test_is_expired(self):
        s = Session('abc123')
        self.assertFalse(s.is_expired(10))
        s._accessed = time.time() - 20
        self.assertTrue(s.is_expired(10))

    def test_sid_attribute(self):
        s = Session('my-session-id')
        self.assertEqual(s.sid, 'my-session-id')

    def test_new_flag(self):
        s = Session('abc123')
        self.assertTrue(s._new)

    def test_iteration(self):
        s = Session('abc123', {'a': 1, 'b': 2, 'c': 3})
        self.assertEqual(sorted(s.keys()), ['a', 'b', 'c'])
        self.assertEqual(sorted(s.values()), [1, 2, 3])

    def test_equality(self):
        s = Session('abc123', {'x': 10})
        self.assertEqual(s, {'x': 10})

    def test_contains(self):
        s = Session('abc123', {'key': 'val'})
        self.assertIn('key', s)
        self.assertNotIn('other', s)


class TestSessionStore(unittest.TestCase):
    """ Tests for the SessionStore. """

    def setUp(self):
        self.store = SessionStore(timeout=5, cleanup_interval=1)

    def tearDown(self):
        self.store.close()

    def test_create_returns_session(self):
        session = self.store.create()
        self.assertIsInstance(session, Session)
        self.assertEqual(len(session.sid), 48)  # 24 bytes * 2 hex chars

    def test_create_unique_ids(self):
        ids = set(self.store.create().sid for _ in range(100))
        self.assertEqual(len(ids), 100)

    def test_get_existing(self):
        session = self.store.create()
        session['data'] = 'hello'
        self.store.save(session)
        retrieved = self.store.get(session.sid)
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved['data'], 'hello')

    def test_get_nonexistent(self):
        self.assertIsNone(self.store.get('nonexistent-id'))

    def test_get_expired(self):
        session = self.store.create()
        session._accessed = time.time() - 10  # Expired (timeout=5)
        self.store.save(session)
        self.assertIsNone(self.store.get(session.sid))

    def test_get_touches_session(self):
        session = self.store.create()
        old_accessed = session._accessed
        time.sleep(0.01)
        self.store.get(session.sid)
        retrieved = self.store.get(session.sid)
        self.assertGreater(retrieved._accessed, old_accessed)

    def test_delete(self):
        session = self.store.create()
        sid = session.sid
        self.store.delete(sid)
        self.assertIsNone(self.store.get(sid))

    def test_delete_nonexistent(self):
        # Should not raise
        self.store.delete('nonexistent-id')

    def test_save_updates_store(self):
        session = self.store.create()
        session['key'] = 'value'
        self.store.save(session)
        retrieved = self.store.get(session.sid)
        self.assertEqual(retrieved['key'], 'value')

    def test_save_clears_modified_flag(self):
        session = self.store.create()
        session['key'] = 'value'
        self.assertTrue(session._modified)
        self.store.save(session)
        self.assertFalse(session._modified)

    def test_save_clears_new_flag(self):
        session = self.store.create()
        self.assertTrue(session._new)
        self.store.save(session)
        self.assertFalse(session._new)

    def test_purge_expired(self):
        s1 = self.store.create()
        s2 = self.store.create()
        s1._accessed = time.time() - 10  # Expired
        self.store.save(s1)
        self.store._purge_expired()
        self.assertIsNone(self.store.get(s1.sid))
        self.assertIsNotNone(self.store.get(s2.sid))

    def test_cleanup_thread(self):
        store = SessionStore(timeout=0.05, cleanup_interval=0.1)
        store.start_cleanup_thread()
        session = store.create()
        sid = session.sid
        time.sleep(0.3)  # Wait for cleanup to run
        self.assertIsNone(store.get(sid))
        store.close()

    def test_thread_safety(self):
        errors = []
        def worker():
            try:
                for _ in range(50):
                    s = self.store.create()
                    s['tid'] = threading.current_thread().name
                    self.store.save(s)
                    retrieved = self.store.get(s.sid)
                    if retrieved is None:
                        errors.append('Session lost')
                    self.store.delete(s.sid)
            except Exception as e:
                errors.append(str(e))

        threads = [threading.Thread(target=worker) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        self.assertEqual(errors, [])

    def test_close_stops_thread(self):
        store = SessionStore(timeout=60, cleanup_interval=0.1)
        store.start_cleanup_thread()
        self.assertTrue(store._cleanup_thread.is_alive())
        store.close()
        time.sleep(0.3)
        self.assertFalse(store._cleanup_thread.is_alive())


class TestSessionPlugin(ServerTestBase):
    """ Integration tests for the SessionPlugin with a Bottle app. """

    def setUp(self):
        super().setUp()
        self.secret = 'test-secret-key-for-sessions'
        self.plugin = SessionPlugin(secret=self.secret, timeout=3600,
                                    cleanup_interval=60)
        self.app.install(self.plugin)

    def tearDown(self):
        self.plugin.close()
        super().tearDown()

    def make_cookie_header(self, result):
        """ Build an HTTP_COOKIE header from a response's Set-Cookie. """
        header = result.get('header', {})
        set_cookie = header.get('Set-Cookie', '')
        # Extract just the cookie name=value before the first ;
        parts = set_cookie.split(';')
        if parts:
            return parts[0].strip()
        return ''

    def test_session_created_on_write(self):
        @self.app.route('/test')
        def handler():
            bottle.request.session['key'] = 'value'
            return 'ok'

        result = self.urlopen('/test')
        self.assertEqual(result['code'], 200)
        self.assertIn('Set-Cookie', result['header'])

    def test_no_cookie_on_read_only_existing_session(self):
        @self.app.route('/write')
        def write():
            bottle.request.session['key'] = 'value'
            return 'ok'

        @self.app.route('/read')
        def read():
            return bottle.request.session.get('key', 'none')

        # First request writes, gets a cookie
        r1 = self.urlopen('/write')
        cookie = self.make_cookie_header(r1)

        # Second request only reads - no Set-Cookie needed
        r2 = self.urlopen('/read', env={'HTTP_COOKIE': cookie})
        self.assertEqual(r2['body'], tob('value'))
        self.assertNotIn('Set-Cookie', r2['header'])

    def test_session_persistence(self):
        @self.app.route('/set')
        def set_handler():
            bottle.request.session['user'] = 'alice'
            return 'set'

        @self.app.route('/get')
        def get_handler():
            return bottle.request.session.get('user', 'none')

        # First request: set session data
        result1 = self.urlopen('/set')
        self.assertEqual(result1['code'], 200)
        cookie = self.make_cookie_header(result1)

        # Second request: get session data with the same cookie
        result2 = self.urlopen('/get', env={'HTTP_COOKIE': cookie})
        self.assertEqual(result2['body'], tob('alice'))

    def test_new_session_sets_cookie(self):
        @self.app.route('/test')
        def handler():
            bottle.request.session['data'] = 'new'
            return 'ok'

        result = self.urlopen('/test')
        self.assertIn('Set-Cookie', result['header'])

    def test_session_invalid_cookie(self):
        @self.app.route('/test')
        def handler():
            bottle.request.session['data'] = 'fresh'
            return bottle.request.session.get('data', 'new')

        # Send a forged/invalid cookie - a new session is created
        result = self.urlopen('/test', env={
            'HTTP_COOKIE': 'bottle.session=invalid-session-id'
        })
        self.assertEqual(result['body'], tob('fresh'))
        self.assertIn('Set-Cookie', result['header'])

    def test_session_opt_out(self):
        @self.app.route('/no-session', session=False)
        def handler():
            env = bottle.request.environ
            return 'has_session' if 'bottle.request.ext.session' in env else 'no_session'

        result = self.urlopen('/no-session')
        self.assertEqual(result['body'], tob('no_session'))

    def test_session_dict_operations(self):
        @self.app.route('/ops')
        def handler():
            s = bottle.request.session
            s['a'] = 1
            s['b'] = 2
            s['c'] = 3
            del s['b']
            s.update({'d': 4})
            result = sorted(s.keys())
            return ','.join(str(k) for k in result)

        result = self.urlopen('/ops')
        self.assertEqual(result['body'], tob('a,c,d'))

    def test_session_httponly_cookie(self):
        result = self._make_session_request()
        set_cookie = result['header'].get('Set-Cookie', '')
        self.assertIn('httponly', set_cookie.lower())

    def test_session_samesite_cookie(self):
        result = self._make_session_request()
        set_cookie = result['header'].get('Set-Cookie', '')
        self.assertIn('samesite=lax', set_cookie.lower())

    def test_session_path_cookie(self):
        result = self._make_session_request()
        set_cookie = result['header'].get('Set-Cookie', '')
        self.assertIn('Path=/', set_cookie)

    def _make_session_request(self):
        @self.app.route('/cookie-test')
        def handler():
            bottle.request.session['x'] = 1
            return 'ok'
        return self.urlopen('/cookie-test')

    def test_plugin_requires_secret(self):
        with self.assertRaises(bottle.PluginError):
            SessionPlugin(secret=None)

    def test_plugin_requires_nonempty_secret(self):
        with self.assertRaises(bottle.PluginError):
            SessionPlugin(secret='')

    def test_session_with_redirect(self):
        @self.app.route('/redirect')
        def handler():
            bottle.request.session['before_redirect'] = True
            bottle.redirect('/target')

        @self.app.route('/target')
        def target():
            return 'target'

        result = self.urlopen('/redirect')
        # redirect raises HTTPResponse, session should still be saved
        self.assertIn(result['code'], (302, 303))
        self.assertIn('Set-Cookie', result['header'])

    def test_session_with_abort(self):
        @self.app.route('/abort')
        def handler():
            bottle.request.session['before_abort'] = True
            bottle.abort(403, 'Forbidden')

        result = self.urlopen('/abort')
        self.assertEqual(result['code'], 403)
        self.assertIn('Set-Cookie', result['header'])

    def test_multiple_requests_same_session(self):
        @self.app.route('/increment')
        def handler():
            s = bottle.request.session
            s['count'] = s.get('count', 0) + 1
            return str(s['count'])

        # First request
        r1 = self.urlopen('/increment')
        self.assertEqual(r1['body'], tob('1'))
        cookie = self.make_cookie_header(r1)

        # Second request with same cookie
        r2 = self.urlopen('/increment', env={'HTTP_COOKIE': cookie})
        self.assertEqual(r2['body'], tob('2'))

        # Third request with same cookie
        r3 = self.urlopen('/increment', env={'HTTP_COOKIE': cookie})
        self.assertEqual(r3['body'], tob('3'))

    def test_plugin_close(self):
        plugin = SessionPlugin(secret='close-test', cleanup_interval=0.1)
        app = bottle.Bottle()
        app.install(plugin)
        @app.route('/x')
        def handler():
            return 'x'
        self.assertIsNotNone(plugin.store)
        plugin.close()
        self.assertTrue(plugin.store._closed)

    def test_session_clear_empties_data(self):
        @self.app.route('/fill')
        def fill():
            bottle.request.session['a'] = 1
            bottle.request.session['b'] = 2
            return 'filled'

        @self.app.route('/clear')
        def clear():
            bottle.request.session.clear()
            return str(len(bottle.request.session))

        r1 = self.urlopen('/fill')
        cookie = self.make_cookie_header(r1)
        r2 = self.urlopen('/clear', env={'HTTP_COOKIE': cookie})
        self.assertEqual(r2['body'], tob('0'))

    def test_no_write_without_modification(self):
        """ Verify that _save_session skips store.save when session is
            neither new nor modified. """
        @self.app.route('/noop')
        def handler():
            # Access session but don't modify it
            _ = bottle.request.session.get('nonexistent')
            return 'noop'

        @self.app.route('/init')
        def init():
            bottle.request.session['setup'] = True
            return 'init'

        # Create a session
        r1 = self.urlopen('/init')
        cookie = self.make_cookie_header(r1)

        # Read-only request - should not produce Set-Cookie
        r2 = self.urlopen('/noop', env={'HTTP_COOKIE': cookie})
        self.assertEqual(r2['body'], tob('noop'))
        self.assertNotIn('Set-Cookie', r2['header'])


if __name__ == '__main__':
    unittest.main()
