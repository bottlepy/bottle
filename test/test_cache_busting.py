import hashlib
import os
import shutil
import sys
import tempfile
import threading
import time
import unittest

import bottle
from bottle import (
    CacheBustingFileManager, Bottle, HTTPError, request, response,
    static_file, tob
)
import wsgiref.util


class TestCacheBustingFileManager(unittest.TestCase):

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        # Create some test files
        self._write('style.css', b'body { color: red; }')
        self._write('app.js', b'console.log("hello");')
        self._write('sub/deep.css', b'.deep { margin: 0; }')
        self._write('noext', b'no extension file')
        self._write('.hidden', b'hidden file')
        self.mgr = CacheBustingFileManager(self.tmpdir)
        # Set up WSGI env for static_file to work
        e = dict()
        wsgiref.util.setup_testing_defaults(e)
        b = Bottle()
        request.bind(e)
        response.bind()

    def tearDown(self):
        shutil.rmtree(self.tmpdir)

    def _write(self, relpath, content):
        abspath = os.path.join(self.tmpdir, relpath.replace('/', os.sep))
        os.makedirs(os.path.dirname(abspath), exist_ok=True)
        with open(abspath, 'wb') as f:
            f.write(content)

    def _hash(self, content, length=12):
        return hashlib.sha256(content).hexdigest()[:length]

    # ------------------------------------------------------------------
    # get_url basic functionality
    # ------------------------------------------------------------------

    def test_get_url_basic(self):
        url = self.mgr.get_url('style.css')
        expected_hash = self._hash(b'body { color: red; }')
        self.assertEqual(url, '/static/style.%s.css' % expected_hash)

    def test_get_url_js(self):
        url = self.mgr.get_url('app.js')
        expected_hash = self._hash(b'console.log("hello");')
        self.assertEqual(url, '/static/app.%s.js' % expected_hash)

    def test_get_url_subdirectory(self):
        url = self.mgr.get_url('sub/deep.css')
        expected_hash = self._hash(b'.deep { margin: 0; }')
        self.assertEqual(url, '/static/sub/deep.%s.css' % expected_hash)

    def test_get_url_no_extension(self):
        url = self.mgr.get_url('noext')
        expected_hash = self._hash(b'no extension file')
        self.assertEqual(url, '/static/noext.%s' % expected_hash)

    def test_get_url_hidden_file(self):
        url = self.mgr.get_url('.hidden')
        expected_hash = self._hash(b'hidden file')
        self.assertEqual(url, '/static/.hidden.%s' % expected_hash)

    def test_get_url_nonexistent_raises(self):
        with self.assertRaises(HTTPError) as ctx:
            self.mgr.get_url('does_not_exist.css')
        self.assertEqual(ctx.exception.status_code, 404)

    def test_get_url_directory_traversal_raises(self):
        with self.assertRaises(HTTPError) as ctx:
            self.mgr.get_url('../../../etc/passwd')
        self.assertEqual(ctx.exception.status_code, 403)

    def test_get_url_double_dot_in_path_raises(self):
        with self.assertRaises(HTTPError) as ctx:
            self.mgr.get_url('sub/../../../etc/passwd')
        self.assertEqual(ctx.exception.status_code, 403)

    def test_get_url_backslash_traversal_raises(self):
        with self.assertRaises(HTTPError) as ctx:
            self.mgr.get_url('..\\..\\etc\\passwd')
        self.assertEqual(ctx.exception.status_code, 403)

    # ------------------------------------------------------------------
    # URL determinism
    # ------------------------------------------------------------------

    def test_url_deterministic(self):
        url1 = self.mgr.get_url('style.css')
        url2 = self.mgr.get_url('style.css')
        self.assertEqual(url1, url2)

    def test_url_changes_with_content(self):
        url_before = self.mgr.get_url('style.css')
        self._write('style.css', b'body { color: blue; }')
        self.mgr.clear()
        url_after = self.mgr.get_url('style.css')
        self.assertNotEqual(url_before, url_after)

    def test_url_changes_detected_without_mtime_change(self):
        """Content change is detected even when mtime does not advance.

        This is the core improvement over mtime-only freshness: a file
        rewritten within the same second (same mtime) must still produce
        a different URL when its content differs.
        """
        url_before = self.mgr.get_url('style.css')
        # Overwrite with different content — do NOT sleep, so mtime may
        # be identical on filesystems with coarse timestamps.
        self._write('style.css', b'body { color: blue; }')
        url_after = self.mgr.get_url('style.css')
        self.assertNotEqual(url_before, url_after)

    def test_url_stable_when_content_unchanged(self):
        """Rewriting the same content produces the same URL."""
        url_before = self.mgr.get_url('style.css')
        self._write('style.css', b'body { color: red; }')  # same bytes
        url_after = self.mgr.get_url('style.css')
        self.assertEqual(url_before, url_after)

    def test_different_files_different_urls(self):
        url_css = self.mgr.get_url('style.css')
        url_js = self.mgr.get_url('app.js')
        self.assertNotEqual(url_css, url_js)

    # ------------------------------------------------------------------
    # Custom prefix
    # ------------------------------------------------------------------

    def test_custom_prefix(self):
        mgr = CacheBustingFileManager(self.tmpdir, prefix='/assets')
        url = mgr.get_url('style.css')
        self.assertTrue(url.startswith('/assets/'))

    def test_prefix_stripped(self):
        mgr = CacheBustingFileManager(self.tmpdir, prefix='///assets///')
        url = mgr.get_url('style.css')
        self.assertTrue(url.startswith('/assets/'))

    def test_empty_prefix(self):
        mgr = CacheBustingFileManager(self.tmpdir, prefix='')
        url = mgr.get_url('style.css')
        self.assertTrue(url.startswith('/style.'))

    # ------------------------------------------------------------------
    # Custom hash_length
    # ------------------------------------------------------------------

    def test_custom_hash_length(self):
        mgr = CacheBustingFileManager(self.tmpdir, hash_length=8)
        url = mgr.get_url('style.css')
        # Extract hash from URL: /static/style.<hash>.css
        parts = url.split('/')[-1]  # style.<hash>.css
        name_hash = parts.split('.')[1]
        self.assertEqual(len(name_hash), 8)

    def test_minimum_hash_length(self):
        mgr = CacheBustingFileManager(self.tmpdir, hash_length=1)
        url = mgr.get_url('style.css')
        parts = url.split('/')[-1]
        name_hash = parts.split('.')[1]
        self.assertEqual(len(name_hash), 4)  # Minimum is 4

    # ------------------------------------------------------------------
    # resolve
    # ------------------------------------------------------------------

    def test_resolve_valid(self):
        url = self.mgr.get_url('style.css')
        versioned_path = url[len('/static/'):]
        result = self.mgr.resolve(versioned_path)
        self.assertEqual(result.status_code, 200)
        self.assertEqual(result.body.read(), b'body { color: red; }')

    def test_resolve_cache_headers(self):
        url = self.mgr.get_url('style.css')
        versioned_path = url[len('/static/'):]
        result = self.mgr.resolve(versioned_path)
        self.assertIn('max-age=31536000', result.headers['Cache-Control'])
        self.assertIn('immutable', result.headers['Cache-Control'])
        self.assertIn('public', result.headers['Cache-Control'])

    def test_resolve_subdirectory(self):
        url = self.mgr.get_url('sub/deep.css')
        versioned_path = url[len('/static/'):]
        result = self.mgr.resolve(versioned_path)
        self.assertEqual(result.status_code, 200)
        self.assertEqual(result.body.read(), b'.deep { margin: 0; }')

    def test_resolve_stale_hash_redirects(self):
        url = self.mgr.get_url('style.css')
        versioned_path = url[len('/static/'):]
        # Change file content
        self._write('style.css', b'body { color: blue; }')
        result = self.mgr.resolve(versioned_path)
        self.assertEqual(result.status_code, 302)
        self.assertIn('Location', result.headers)
        # The redirect should point to the new versioned URL
        new_url = self.mgr.get_url('style.css')
        self.assertEqual(result.headers['Location'], new_url)

    def test_resolve_nonexistent_file_raises(self):
        with self.assertRaises(HTTPError) as ctx:
            self.mgr.resolve('nonexistent.abc123def456.css')
        self.assertEqual(ctx.exception.status_code, 404)

    def test_resolve_no_hash_in_path_raises(self):
        with self.assertRaises(HTTPError) as ctx:
            self.mgr.resolve('style.css')
        self.assertEqual(ctx.exception.status_code, 404)

    def test_resolve_invalid_format_raises(self):
        with self.assertRaises(HTTPError) as ctx:
            self.mgr.resolve('')
        self.assertEqual(ctx.exception.status_code, 404)

    def test_resolve_directory_traversal_raises(self):
        with self.assertRaises(HTTPError) as ctx:
            self.mgr.resolve('../../etc/passwd.abc123def456.txt')
        self.assertEqual(ctx.exception.status_code, 403)

    def test_resolve_no_extension(self):
        url = self.mgr.get_url('noext')
        versioned_path = url[len('/static/'):]
        # File without extension: noext.<hash> — no trailing .ext, so
        # the versioned regex (which requires stem.hash.ext) won't match.
        m = self.mgr._versioned_re.match(versioned_path)
        self.assertIsNone(m)

    # ------------------------------------------------------------------
    # Regex enforces exact digest length
    # ------------------------------------------------------------------

    def test_resolve_rejects_short_hash(self):
        """A hash shorter than hash_length is rejected by the regex."""
        short = 'a' * (self.mgr.hash_length - 1)
        with self.assertRaises(HTTPError) as ctx:
            self.mgr.resolve('style.%s.css' % short)
        self.assertEqual(ctx.exception.status_code, 404)

    def test_resolve_rejects_long_hash(self):
        """A hash longer than hash_length is rejected by the regex."""
        long = 'a' * (self.mgr.hash_length + 1)
        with self.assertRaises(HTTPError) as ctx:
            self.mgr.resolve('style.%s.css' % long)
        self.assertEqual(ctx.exception.status_code, 404)

    def test_resolve_rejects_non_hex_hash(self):
        """Non-hex characters in the hash position are rejected."""
        bad = 'g' * self.mgr.hash_length  # 'g' is not hex
        with self.assertRaises(HTTPError) as ctx:
            self.mgr.resolve('style.%s.css' % bad)
        self.assertEqual(ctx.exception.status_code, 404)

    def test_regex_exact_length_matches(self):
        exact = 'a' * self.mgr.hash_length
        m = self.mgr._versioned_re.match('style.%s.css' % exact)
        self.assertIsNotNone(m)
        self.assertEqual(m.group(2), exact)

    def test_regex_custom_length_enforced(self):
        mgr = CacheBustingFileManager(self.tmpdir, hash_length=8)
        # 8 hex chars should match
        m = mgr._versioned_re.match('style.abcdef01.css')
        self.assertIsNotNone(m)
        # 7 hex chars should not
        m = mgr._versioned_re.match('style.abcdef0.css')
        self.assertIsNone(m)
        # 9 hex chars should not
        m = mgr._versioned_re.match('style.abcdef012.css')
        self.assertIsNone(m)

    # ------------------------------------------------------------------
    # Unified error signaling
    # ------------------------------------------------------------------

    def test_get_url_raises_httperror_not_none(self):
        """get_url raises HTTPError, never returns None."""
        with self.assertRaises(HTTPError):
            self.mgr.get_url('no_such_file.css')

    def test_resolve_raises_httperror_not_returns(self):
        """resolve raises HTTPError for bad input, never returns one."""
        with self.assertRaises(HTTPError):
            self.mgr.resolve('bad_format')

    def test_error_is_catchable_in_bottle_app(self):
        """HTTPError from get_url/resolve can be caught by Bottle error
        handlers like any other routing error."""
        try:
            self.mgr.get_url('missing.css')
            self.fail("Expected HTTPError")
        except HTTPError as e:
            self.assertIn(e.status_code, (403, 404))

    # ------------------------------------------------------------------
    # Path normalization
    # ------------------------------------------------------------------

    def test_normalize_leading_slash(self):
        url = self.mgr.get_url('/style.css')
        expected_hash = self._hash(b'body { color: red; }')
        self.assertEqual(url, '/static/style.%s.css' % expected_hash)

    def test_normalize_backslashes(self):
        url = self.mgr.get_url('sub\\deep.css')
        expected_hash = self._hash(b'.deep { margin: 0; }')
        self.assertEqual(url, '/static/sub/deep.%s.css' % expected_hash)

    def test_normalize_double_slashes(self):
        url = self.mgr.get_url('sub//deep.css')
        expected_hash = self._hash(b'.deep { margin: 0; }')
        self.assertEqual(url, '/static/sub/deep.%s.css' % expected_hash)

    def test_normalize_dot_segments(self):
        url = self.mgr.get_url('sub/./deep.css')
        expected_hash = self._hash(b'.deep { margin: 0; }')
        self.assertEqual(url, '/static/sub/deep.%s.css' % expected_hash)

    # ------------------------------------------------------------------
    # Path-component containment checks
    # ------------------------------------------------------------------
    #
    # These tests verify that containment is decided using path
    # semantics (component-by-component comparison via commonpath +
    # normcase), NOT by string prefix matching (startswith).

    def test_containment_dotdot_into_sibling_directory(self):
        """A ``..`` traversal into a sibling directory whose name shares
        a string prefix with root is blocked.

        Construct:  root  = <tmp>/static
                    file  = <tmp>/staticextra/secret.txt
                    input = ../staticextra/secret.txt

        A naive ``startswith`` on the *string* ``<tmp>/staticextra``
        against ``<tmp>/static`` would incorrectly pass because the
        longer name shares the same prefix.  Component-based containment
        rejects it because ``staticextra`` != ``static``.
        """
        # Build a sibling directory whose name shares a prefix with root
        root_dir = os.path.join(self.tmpdir, 'static')
        sibling_dir = os.path.join(self.tmpdir, 'staticextra')
        os.makedirs(root_dir, exist_ok=True)
        os.makedirs(sibling_dir, exist_ok=True)
        # Put a file in the root we want to protect
        with open(os.path.join(root_dir, 'ok.css'), 'w') as f:
            f.write('body {}')
        # Put a secret file in the sibling directory
        with open(os.path.join(sibling_dir, 'secret.txt'), 'w') as f:
            f.write('secret')
        mgr = CacheBustingFileManager(root_dir)
        # This path escapes root via .. and lands in the sibling
        with self.assertRaises(HTTPError) as ctx:
            mgr._normalize('../staticextra/secret.txt')
        self.assertEqual(ctx.exception.status_code, 403)

    def test_containment_symlink_chain_escape(self):
        """A symlink that logically stays inside root but whose real
        target is outside root is rejected.

        Construct:  root  = <tmp>/webroot
                    real  = <tmp>/outside/leak.txt
                    link  = <tmp>/webroot/innocent.txt  -> <tmp>/outside/leak.txt

        The logical path ``<tmp>/webroot/innocent.txt`` starts with
        ``<tmp>/webroot/`` so a string check would pass, but
        ``realpath`` resolves the symlink to ``<tmp>/outside/leak.txt``
        whose path components diverge from root.
        """
        webroot = os.path.join(self.tmpdir, 'webroot')
        outside = os.path.join(self.tmpdir, 'outside')
        os.makedirs(webroot, exist_ok=True)
        os.makedirs(outside, exist_ok=True)
        leak_file = os.path.join(outside, 'leak.txt')
        with open(leak_file, 'w') as f:
            f.write('leaked')
        link_path = os.path.join(webroot, 'innocent.txt')
        os.symlink(leak_file, link_path)
        mgr = CacheBustingFileManager(webroot)
        with self.assertRaises(HTTPError) as ctx:
            mgr._normalize('innocent.txt')
        self.assertEqual(ctx.exception.status_code, 403)

    def test_containment_case_mismatch(self):
        """On a case-sensitive filesystem, requesting a filename that
        differs only in case from the real file does not trigger a false
        403 from the containment check — it correctly falls through to a
        404 from the hash computation because the file simply does not
        exist under that name.

        A string-prefix containment check applied *after* normcase could
        wrongly reject a valid-looking path with 403 even though the
        real issue is a missing file.  Component-based containment with
        normcase ensures that the case-differing path is still recognized
        as *inside* root (not an escape), and the 404 comes from the
        file-read layer where it belongs.
        """
        # style.css exists, STYLE.CSS does not (on case-sensitive FS)
        # _normalize should NOT raise 403 — the path is inside root.
        # The error should come later, from _compute_hash, as a 404.
        if sys.platform == 'win32' or sys.platform == 'darwin':
            # On case-insensitive filesystems both names resolve to the
            # same file, so get_url should succeed with the same hash.
            url = self.mgr.get_url('STYLE.CSS')
            expected_hash = self._hash(b'body { color: red; }')
            self.assertIn(expected_hash, url)
        else:
            # On case-sensitive Linux: _normalize succeeds (path is
            # inside root), but the file doesn't exist so _compute_hash
            # raises 404.
            normalized = self.mgr._normalize('STYLE.CSS')
            # The normalized name should not have caused a 403 — the
            # path is inside root, just non-existent.
            self.assertIsInstance(normalized, str)
            with self.assertRaises(HTTPError) as ctx:
                self.mgr.get_url('STYLE.CSS')
            self.assertEqual(ctx.exception.status_code, 404)

    def test_containment_valid_nested_path_accepted(self):
        """A legitimate deeply nested path passes component-based
        containment and returns the correct versioned URL.

        Exercises the full normalize -> hash -> URL pipeline for a path
        with multiple directory components, ensuring that the
        component-by-component comparison does not accidentally reject
        valid internal paths.
        """
        self._write('a/b/c/deep.css', b'.deep { padding: 0; }')
        url = self.mgr.get_url('a/b/c/deep.css')
        expected_hash = self._hash(b'.deep { padding: 0; }')
        self.assertEqual(url, '/static/a/b/c/deep.%s.css' % expected_hash)
        # Round-trip: resolve should serve the file
        versioned_path = url[len('/static/'):]
        result = self.mgr.resolve(versioned_path)
        self.assertEqual(result.status_code, 200)
        self.assertEqual(result.body.read(), b'.deep { padding: 0; }')

    def test_symlink_inside_root_allowed(self):
        """A symlink that resolves inside root is accepted."""
        target = os.path.join(self.tmpdir, 'style.css')
        link = os.path.join(self.tmpdir, 'link.css')
        os.symlink(target, link)
        url = self.mgr.get_url('link.css')
        # The URL should reflect the link name, and the hash should match
        # the target content.
        expected_hash = self._hash(b'body { color: red; }')
        self.assertIn(expected_hash, url)

    def test_symlink_outside_root_rejected(self):
        """A symlink whose real target is outside root is rejected."""
        outside_dir = tempfile.mkdtemp()
        try:
            outside_file = os.path.join(outside_dir, 'secret.txt')
            with open(outside_file, 'w') as f:
                f.write('secret')
            link = os.path.join(self.tmpdir, 'escape.txt')
            os.symlink(outside_file, link)
            with self.assertRaises(HTTPError) as ctx:
                self.mgr.get_url('escape.txt')
            self.assertEqual(ctx.exception.status_code, 403)
        finally:
            shutil.rmtree(outside_dir)

    # ------------------------------------------------------------------
    # Cache behavior
    # ------------------------------------------------------------------

    def test_cache_hit(self):
        """Second call should use cached hash (same result, no recompute)."""
        url1 = self.mgr.get_url('style.css')
        url2 = self.mgr.get_url('style.css')
        self.assertEqual(url1, url2)
        # Verify cache has an entry
        self.assertIn('style.css', self.mgr._cache)

    def test_cache_stores_hash_not_tuple(self):
        """Cache values are plain hash strings, not (mtime, hash) tuples."""
        self.mgr.get_url('style.css')
        entry = self.mgr._cache['style.css']
        self.assertIsInstance(entry, str)
        self.assertEqual(len(entry), self.mgr.hash_length)

    def test_cache_clear(self):
        self.mgr.get_url('style.css')
        self.assertIn('style.css', self.mgr._cache)
        self.mgr.clear()
        self.assertEqual(len(self.mgr._cache), 0)
        self.assertEqual(len(self.mgr._cache_order), 0)

    def test_cache_eviction(self):
        """LRU eviction when cache exceeds maxcache."""
        mgr = CacheBustingFileManager(self.tmpdir, maxcache=3)
        # Create 5 files
        for i in range(5):
            self._write('file%d.css' % i, ('content%d' % i).encode())
        # Access all 5 — only last 3 should remain cached
        for i in range(5):
            mgr.get_url('file%d.css' % i)
        self.assertEqual(len(mgr._cache), 3)
        # The first two should have been evicted
        self.assertNotIn('file0.css', mgr._cache)
        self.assertNotIn('file1.css', mgr._cache)
        # The last three should remain
        self.assertIn('file2.css', mgr._cache)
        self.assertIn('file3.css', mgr._cache)
        self.assertIn('file4.css', mgr._cache)

    def test_cache_lru_promotion(self):
        """Accessing a cached item promotes it, preventing eviction."""
        mgr = CacheBustingFileManager(self.tmpdir, maxcache=3)
        for i in range(3):
            self._write('file%d.css' % i, ('content%d' % i).encode())
        # Fill cache
        for i in range(3):
            mgr.get_url('file%d.css' % i)
        # Access file0 again to promote it
        mgr.get_url('file0.css')
        # Now add a 4th file — file1 should be evicted (oldest), not file0
        self._write('file3.css', b'content3')
        mgr.get_url('file3.css')
        self.assertNotIn('file1.css', mgr._cache)
        self.assertIn('file0.css', mgr._cache)
        self.assertIn('file2.css', mgr._cache)
        self.assertIn('file3.css', mgr._cache)

    def test_cache_content_invalidation(self):
        """Changed content causes recomputation even without mtime change."""
        url_before = self.mgr.get_url('style.css')
        self.assertIn('style.css', self.mgr._cache)
        self._write('style.css', b'body { color: green; }')
        url_after = self.mgr.get_url('style.css')
        self.assertNotEqual(url_before, url_after)

    # ------------------------------------------------------------------
    # Thread safety
    # ------------------------------------------------------------------

    def test_concurrent_access(self):
        """Multiple threads can safely call get_url concurrently."""
        # Create many files
        for i in range(20):
            self._write('concurrent%d.css' % i, ('data%d' % i).encode())

        results = {}
        errors = []

        def worker(file_id):
            try:
                name = 'concurrent%d.css' % file_id
                url = self.mgr.get_url(name)
                results[file_id] = url
            except Exception as e:
                errors.append(e)

        threads = []
        for i in range(20):
            t = threading.Thread(target=worker, args=(i,))
            threads.append(t)

        for t in threads:
            t.start()
        for t in threads:
            t.join()

        self.assertEqual(len(errors), 0, "Errors during concurrent access: %s" % errors)
        self.assertEqual(len(results), 20)
        # Verify each result is correct
        for i in range(20):
            expected_hash = self._hash(('data%d' % i).encode())
            expected = '/static/concurrent%d.%s.css' % (i, expected_hash)
            self.assertEqual(results[i], expected)

    def test_concurrent_same_file(self):
        """Multiple threads requesting the same file get the same URL."""
        results = []
        errors = []

        def worker():
            try:
                url = self.mgr.get_url('style.css')
                results.append(url)
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=worker) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        self.assertEqual(len(errors), 0)
        self.assertEqual(len(results), 10)
        # All should be identical
        self.assertEqual(len(set(results)), 1)

    def test_concurrent_eviction(self):
        """Cache eviction under concurrent access does not corrupt state."""
        mgr = CacheBustingFileManager(self.tmpdir, maxcache=5)
        for i in range(50):
            self._write('evict%d.css' % i, ('evict%d' % i).encode())

        errors = []

        def worker(file_id):
            try:
                mgr.get_url('evict%d.css' % file_id)
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=worker, args=(i,)) for i in range(50)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        self.assertEqual(len(errors), 0)
        # Cache should not exceed maxcache
        self.assertLessEqual(len(mgr._cache), 5)
        self.assertLessEqual(len(mgr._cache_order), 5)

    # ------------------------------------------------------------------
    # Root path handling
    # ------------------------------------------------------------------

    def test_root_trailing_slash(self):
        """Root path works with or without trailing slash."""
        mgr1 = CacheBustingFileManager(self.tmpdir)
        mgr2 = CacheBustingFileManager(self.tmpdir + os.sep)
        self.assertEqual(mgr1.get_url('style.css'), mgr2.get_url('style.css'))

    def test_root_absolute(self):
        """Root is always made absolute."""
        self.assertTrue(os.path.isabs(self.mgr.root))

    def test_root_is_realpath(self):
        """Root resolves symlinks to the real filesystem path."""
        link_dir = os.path.join(self.tmpdir, 'link_to_sub')
        real_sub = os.path.join(self.tmpdir, 'sub')
        os.symlink(real_sub, link_dir)
        mgr = CacheBustingFileManager(link_dir)
        self.assertEqual(mgr.root, os.path.join(os.path.realpath(link_dir), ''))

    # ------------------------------------------------------------------
    # Regex pattern coverage
    # ------------------------------------------------------------------

    def test_versioned_re_valid(self):
        exact_hash = 'a' * self.mgr.hash_length
        m = self.mgr._versioned_re.match('style.%s.css' % exact_hash)
        self.assertIsNotNone(m)
        self.assertEqual(m.group(1), 'style')
        self.assertEqual(m.group(2), exact_hash)
        self.assertEqual(m.group(3), '.css')

    def test_versioned_re_subdir(self):
        exact_hash = 'a' * self.mgr.hash_length
        m = self.mgr._versioned_re.match('sub/deep.%s.css' % exact_hash)
        self.assertIsNotNone(m)
        self.assertEqual(m.group(1), 'sub/deep')
        self.assertEqual(m.group(2), exact_hash)
        self.assertEqual(m.group(3), '.css')

    def test_versioned_re_no_hash(self):
        m = self.mgr._versioned_re.match('style.css')
        self.assertIsNone(m)

    def test_versioned_re_multiple_dots(self):
        """File like 'jquery.min.<hash>.js' should work."""
        exact_hash = 'a' * self.mgr.hash_length
        m = self.mgr._versioned_re.match('jquery.min.%s.js' % exact_hash)
        self.assertIsNotNone(m)
        self.assertEqual(m.group(1), 'jquery.min')
        self.assertEqual(m.group(2), exact_hash)
        self.assertEqual(m.group(3), '.js')

    # ------------------------------------------------------------------
    # Integration: round-trip get_url -> resolve
    # ------------------------------------------------------------------

    def test_roundtrip_css(self):
        url = self.mgr.get_url('style.css')
        versioned_path = url[len('/static/'):]
        result = self.mgr.resolve(versioned_path)
        self.assertEqual(result.status_code, 200)
        self.assertEqual(result.body.read(), b'body { color: red; }')

    def test_roundtrip_subdirectory(self):
        url = self.mgr.get_url('sub/deep.css')
        versioned_path = url[len('/static/'):]
        result = self.mgr.resolve(versioned_path)
        self.assertEqual(result.status_code, 200)
        self.assertEqual(result.body.read(), b'.deep { margin: 0; }')

    def test_roundtrip_js(self):
        url = self.mgr.get_url('app.js')
        versioned_path = url[len('/static/'):]
        result = self.mgr.resolve(versioned_path)
        self.assertEqual(result.status_code, 200)
        self.assertEqual(result.body.read(), b'console.log("hello");')

    # ------------------------------------------------------------------
    # split_ext edge cases
    # ------------------------------------------------------------------

    def test_split_ext_normal(self):
        self.assertEqual(self.mgr._split_ext('style.css'), ('style', '.css'))

    def test_split_ext_subdir(self):
        self.assertEqual(self.mgr._split_ext('css/style.css'), ('css/style', '.css'))

    def test_split_ext_no_ext(self):
        self.assertEqual(self.mgr._split_ext('readme'), ('readme', ''))

    def test_split_ext_multiple_dots(self):
        self.assertEqual(self.mgr._split_ext('app.min.js'), ('app.min', '.js'))

    def test_split_ext_dot_in_dir(self):
        self.assertEqual(self.mgr._split_ext('v1.0/style.css'), ('v1.0/style', '.css'))

    def test_split_ext_hidden_file(self):
        self.assertEqual(self.mgr._split_ext('.gitignore'), ('.gitignore', ''))

    def test_split_ext_hidden_with_ext(self):
        self.assertEqual(self.mgr._split_ext('.config.json'), ('.config', '.json'))


if __name__ == '__main__':
    unittest.main()
