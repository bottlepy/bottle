Cache Busting for Static Assets
===============================

Modern browsers and CDNs cache CSS and JavaScript very aggressively. When a new
deployment changes asset contents but keeps the same URL, users may get a broken
or outdated layout until their caches expire.

Bottle includes :class:`CacheBustingFileManager` to generate deterministic,
content-hash versioned URLs for static assets. The URL itself becomes the cache
key. When the file changes, the URL changes, and clients fetch the new version.

Overview
--------

Versioned URLs embed a truncated content hash in the filename::

    style.css  ->  /static/style.a1b2c3d4e5f6.css

This allows you to serve assets with long-lived cache headers (e.g. one year)
without risking stale deployments.

Basic usage
-----------

Create a manager pointing at your static root:

.. code-block:: python

    from bottle import Bottle, CacheBustingFileManager

    app = Bottle()
    assets = CacheBustingFileManager('/srv/app/static', prefix='/static')

Generate versioned URLs for templates or helpers:

.. code-block:: python

    # returns "/static/css/style.<hash>.css"
    url = assets.get_url('css/style.css')

Serve versioned assets with a normal Bottle route:

.. code-block:: python

    from bottle import HTTPError

    @app.get('/static/<versioned_path:path>')
    def static(versioned_path):
        # Returns static_file(...) with strong cache headers, or raises HTTPError.
        return assets.resolve(versioned_path)

Caching behavior
----------------

When a versioned URL is requested, Bottle serves it with aggressive caching
headers suitable for CDNs and immutable assets.

If a request uses a stale hash (e.g. an old HTML page referencing the previous
deployment), :meth:`CacheBustingFileManager.resolve` returns a ``302`` redirect
to the current versioned URL. This makes rollouts more forgiving while still
keeping the main caching model URL-based.

Configuration
-------------

``root`` (required)
    Absolute path to the directory containing static assets.

``prefix`` (default: ``/static``)
    URL path prefix used by :meth:`get_url`.

``maxcache`` (default: ``1024``)
    Maximum number of cached hash entries (LRU). Bounds memory usage.

``hash_length`` (default: ``12``)
    Number of hex characters embedded in the URL. Shorter values increase the
    probability of collisions; the default is intended to be safe for practical
    asset sets.

Security notes
--------------

The manager validates paths using filesystem semantics (realpath containment)
instead of string prefix checks. This prevents directory traversal and symlink
escapes, even in edge cases where naive string checks would be fooled.

Limitations
-----------

The hash cache is in-memory and process-local. This is typically sufficient
because the content hash is deterministic and can be recomputed at any time.
If you run multiple worker processes, each worker maintains its own small cache.
