SessionPlugin
=============

The :class:`SessionPlugin` provides optional server-side sessions for Bottle
applications. Session data is stored on the server in memory, while the client
receives only a signed session identifier cookie.

The plugin is intentionally lightweight and designed for applications that need
simple session handling without external dependencies.

Installation
------------

Install the plugin on a Bottle application:

.. code-block:: python

    from bottle import Bottle, request, SessionPlugin

    app = Bottle()
    app.install(SessionPlugin(secret='your-secret-key'))

Once installed, each request gains a ``request.session`` object.

Basic Usage
-----------

.. code-block:: python

    @app.get('/')
    def index():
        request.session['visits'] = request.session.get('visits', 0) + 1
        return f"Visits: {request.session['visits']}"

The session behaves like a dictionary. Changes are automatically persisted at
the end of the request.

Configuration
-------------

The plugin accepts the following parameters:

``secret`` (required)
    Secret key used to sign the session identifier cookie.

``cookie_name`` (default: ``'bottle.session'``)
    Name of the session cookie.

``timeout`` (default: ``3600``)
    Idle timeout (seconds) after which sessions expire.

``cleanup_interval`` (default: ``300``)
    Interval (seconds) between background cleanup runs.

``cookie_path`` (default: ``'/'``)
    Cookie path attribute.

``cookie_domain`` (default: ``None``)
    Cookie domain attribute.

``cookie_secure`` (default: ``False``)
    Set the Secure flag on the cookie.

``cookie_httponly`` (default: ``True``)
    Set the HttpOnly flag on the cookie.

``cookie_samesite`` (default: ``'Lax'``)
    SameSite cookie attribute.

``cookie_maxage`` (default: ``None``)
    Cookie max-age attribute.

``digestmod`` (default: ``hashlib.sha256``)
    Digest algorithm used for cookie signing.

Route-level Opt-Out
------------------

Sessions can be disabled for specific routes:

.. code-block:: python

    @app.get('/health', session=False)
    def health():
        return 'ok'

Behavior
--------

* The client cookie contains only a signed session identifier.
* Session data remains on the server.
* A new cookie is sent only when the session is created or modified.
* Expired sessions are removed automatically by a background cleanup thread.

Limitations
-----------

The default implementation stores sessions in process memory. Sessions do not
survive application restarts and are not shared between multiple worker
processes. Applications requiring distributed or persistent sessions should use
an alternative backend.
