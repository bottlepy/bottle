.. highlight:: python
.. currentmodule:: bottle

=============
Release Notes
=============

This project loosly follows Semantic Versioning (``major.minor.patch``), with
the exception that changes are allowed in minor releases as long as the change
is necessary to match documentation, specification or expectation. 
In other words: Bugfixes do not count as backward incompatible changes, even if
they technically change something from *incorrect* to *correct* and may break
applications that rely on *incorrect*, *undefined* or *undocumented* behavior.

As long as the major version is still ``0.x``, breaking API changes are also
allowed in minor releases, but we try our best to provide fallbacks and emit
deprecation warnings for at least one minor release circle.

.. rubric:: How to upgrade

* Upgrade to the most recent patch release available for your current minor
  release. (e.g. ``0.12.3`` to ``0.12.25``)
* Read the release notes for the next minor release, run your tests and fix all
  deprecation warnings.
* Upgrade to the next minor release (e.g. ``0.12.25`` to ``0.13.2``), run test
  again, fix all warnings and continue.

.. rubric:: Support for old releases

Bugs and security issues are usually fixed in the latest minor release of the
two most recent major releases (named stable and old-stable). With each new major
release, stable becomes old-stable and the old old-stable will no longer receive
regular updates. LTS releases (e.g. 0.12) are an exception. Those will continue
to receive updates on a best-effort basis.

Release 0.14 (in development)
=============================

.. rubric:: Removed APIs (deprecated since 0.13)

* Removed the ``RouteReset`` exception and associated logic.
* Removed the `bottle.py` console script entrypoint in favour of the new `bottle` script. You can still execute `bottle.py` directly or via `python -m bottle`. The only change is that the command installed by pip or similar tools into the bin/Scripts folder of the (virtual) environment is now called `bottle` to avoid circular import errors.

.. rubric:: Changes

* ``bottle.HTTPError`` raised on Invalid JSON now include the underlying exception in their ``exception`` field.


Release 0.13
==============

.. warning:: This release contains breaking changers, please read the notes below

.. rubric:: Dropped support for Python versions that reached their end-of-life.

Bottle up to 0.12 supported an absurd range of Python versions (2.5 to 3.12) and
keeping support for Python versions as ancient as 2.5 required a ton of workarounds
and compromises, but served no real purpose. If you need support for older Python
versions, you can stay on bottle 0.12. The updated list of tested and supported python
releases is as follows:

 * Python 2 >= 2.7.3
 * Python 3 >= 3.8

Support for Python 2.5 was marked as deprecated since 0.12. We decided to go a step further
and also remove support for 2.6 and 3.1 to 3.7 even if it was never deprecated explicitly
in bottle. This means that this release is *not* backwards compatible in Python <2.7.3 or
<3.8 environments. Maintainers for distributions or systems that still use these old python
versions should not update to Bottle 0.13 and stick with 0.12 instead.

.. rubric:: Stabilized APIs

* The documented API of the :class:`ConfigDict` class is now considered stable and ready to use.

.. rubric:: Deprecated APIs

* Python 2 support is now deprecated and will be dropped with the next release.
* The command line executable installed along with bottle will be renamed from `bottle.py` to just `bottle`. You can still execute bottle directly as a script (e.g. `./bottle.py` or `python3 bottle.py`) or as a module (via `python3 -m bottle`). Just the executable installed by your packaging tool (e.g. `pip`) into the `bin` folder of your (virtual) environment will change.
* The old route syntax (``/hello/:name``) is deprecated in favor of the more readable and flexible ``/hello/<name>`` syntax.
* :meth:`Bottle.mount` now recognizes Bottle instance and will warn about parameters that are not compatible with the new mounting behavior. The old behavior (mount applications as WSGI callable) still works and is used as a fallback automatically.
* The undocumented :func:`local_property` helper is now deprecated.
* The server adapter for google app engine is not useful anymore and marked as deprecated.
* Bottle uses pickle to store arbitrary objects into signed cookies. This is safe, as long as the signature key remains a secret. Unfortunately, people tend to push code with signature keys to github all the time, so we decided to remove pickle-support from bottle. Signed cookies will now issue a deprecation warning if the value is not a string, and support for non-string values will be removed in 0.14. The global :func:`cookie_encode`, :func:`cookie_decode` and :func:`is_cookie_encoded` are now also deprecated. If you are using this feature, think about using json to serialize your objects before storing them into cookies, or switch to a session system that stores data server-side instead of client-side.

.. rubric:: Removed APIs (deprecated since 0.12)

* Plugins with the old API (``api=1`` or no api attribute) will no longer work.
* Parameter order of :meth:`Bottle.mount` changed in 0.10. The old order will now result in an error instead of a warning.
* The :class:`ConfigDict` class was introduced in 0.11 and changed during 0.12. These changes are now final.

  * Attribute access and assignment was removed due to high overhead and limited usability.
  * Namespaced sub-instance creation was removed. ``config["a"]["b"]`` has a high overhead and little benefit over ``config["a.b"]``.
  * :class:`ConfigDict` instances are no longer callable. This was a shortcut for :meth:`ConfigDict.update`.
  * :class:`ConfigDict` constructor no longer accepts any parameters. Use the `load_*` methods instead.

* Bottle 0.12 changed some aspects of the Simple Template Engine. These changes are now final and the old syntax will now longer work.

  * The magic ``{{rebase()}}`` call was replaced by a ``base`` variable. Example: ``{{base}}``
  * In STPL Templates, the ``rebase`` and ``include`` keywords were replaced with functions in 0.12.
  * PEP-263 encoding strings are no longer recognized. Templates are always utf-8.

* The 'geventSocketIO' server adapter was removed without notice. It did not work anyway.

.. rubric:: Changes

These changes might require special care when updating.

* Signed cookies now use a stronger HMAC algorithm by default. This will result in old cookies to appear invalid after the update. Pass an explicit ``digestmod=hashlib.md5`` to :meth:`Request.get_cookie <BaseRequest.get_cookie>` and :meth:`Response.set_cookie <BaseResponse.set_cookie>` to get the old behavior.
* Bottle now ships with its own multipart form data parser (borrowed from `multipart <https://pypi.org/project/multipart/>`_) and no longer relies on ``cgi.FieldStorage``, which was removed in Python 3.13. This may change the way broken (non-standard) form submissions are parsed. The new parser is more strict and correct than ohe old one.
* Installing bottle with `pip` or similar tools will now install an additional command line executable named `bottle` into the `bin` folder of your (virtual) environment. This will replace the now deprecated `bottle.py` executable in a later release. See above.

.. rubric:: Other Improvements

* :class:`Bottle` instances are now context managers. If used in a with-statement, the default application changes to the specific instance and the shortcuts for many instance methods can be used.
* Added support for ``PATCH`` requests and the :meth:`Bottle.patch` decorator.
* Added `aiohttp <http://aiohttp.readthedocs.io/en/stable/>`_ and `uvloop <https://github.com/MagicStack/uvloop>`_ server adapters.
* Added command-line arguments for config from json or ini files.
* :meth:`Bottle.mount` now recognizes instances of :class:`Bottle` and mounts them with significantly less overhead than other WSGI applications.
* The :attr:`Request.json <BaseRequest.json>` property now accepts ``application/json-rpc`` requests.
* :func:`static_file` gained support for ``ETag`` headers. It will generate ETags and recognizes ``If-None-Match`` headers.
* :func:`static_file` will now guess the mime type of ``*.gz`` and other compressed files correctly (e.g. ``application/gzip``) and NOT set the ``Content-Encoding`` header.
* Jinja2 templates will produce better error messages than before.



Release 0.12
==============

* New SimpleTemplate parser implementation

  * Support for multi-line code blocks (`<% ... %>`).
  * The keywords `include` and `rebase` are functions now and can accept variable template names.

* The new :attr:`Request.route <BaseRequest.route>` property returns the :class:`Route` that originally matched the request.
* Removed the ``Request.MAX_PARAMS`` limit. The hash collision bug in CPythons dict() implementation was fixed over a year ago. If you are still using Python 2.5 in production, consider upgrading or at least make sure that you get security fixed from your distributor.
* New :class:`ConfigDict` API (see :doc:`configuration`)

More information can be found in this `development blog post <http://blog.bottlepy.org/2013/07/19/preview-bottle-012.html>`_.


Release 0.11
==============

* Native support for Python 2.x and 3.x syntax. No need to run 2to3 anymore.
* Support for partial downloads (``Range`` header) in :func:`static_file`.
* The new :class:`ResourceManager` interface helps locating files bundled with an application.
* Added a server adapter for `waitress <http://docs.pylonsproject.org/projects/waitress/en/latest/>`_.
* New :meth:`Bottle.merge` method to install all routes from one application into another.
* New :attr:`Request.app <BaseRequest.app>` property to get the application object that handles a request.
* Added :meth:`FormsDict.decode()` to get an all-unicode version (needed by WTForms).
* :class:`MultiDict` and subclasses are now pickle-able.

.. rubric:: API Changes

* :attr:`Response.status <BaseResponse.status>` is a read-write property that can be assigned either a numeric status code or a status string with a reason phrase (``200 OK``). The return value is now a string to better match existing APIs (WebOb, werkzeug). To be absolutely clear, you can use the read-only properties :attr:`Response.status_code <BaseResponse.status_code>` and :attr:`Response.status_line <BaseResponse.status_line>`.

.. rubric:: API Deprecations

* :class:`SimpleTALTemplate` is now deprecating. There seems to be no demand.

Release 0.10
==============

* Plugin API v2

  * To use the new API, set :attr:`Plugin.api` to ``2``.
  * :meth:`Plugin.apply` receives a :class:`Route` object instead of a context dictionary as second parameter. The new object offers some additional information and may be extended in the future.
  * Plugin names are considered unique now. The topmost plugin with a given name on a given route is installed, all other plugins with the same name are silently ignored.

* The Request/Response Objects

  * Added :attr:`Request.json <BaseRequest.json>`, :attr:`Request.remote_route <BaseRequest.remote_route>`, :attr:`Request.remote_addr <BaseRequest.remote_addr>`, :attr:`Request.query <BaseRequest.query>` and :attr:`Request.script_name <BaseRequest.script_name>`.
  * Added :attr:`Response.status_line <BaseResponse.status_line>` and :attr:`Response.status_code <BaseResponse.status_code>` attributes. In future releases, :attr:`Response.status <BaseResponse.status>` will return a string (e.g. ``200 OK``) instead of an integer to match the API of other common frameworks. To make the transition as smooth as possible, you should use the verbose attributes from now on.
  * Replaced :class:`MultiDict` with a specialized :class:`FormsDict` in many places. The new dict implementation allows attribute access and handles unicode form values transparently.

* Templates

  * Added three new functions to the SimpleTemplate default namespace that handle undefined variables: :func:`stpl.defined`, :func:`stpl.get` and :func:`stpl.setdefault`.
  * The default escape function for SimpleTemplate now additionally escapes single and double quotes.

* Routing

  * A new route syntax (e.g. ``/object/<id:int>``) and support for route wildcard filters.
  * Four new wildcard filters: `int`, `float`, `path` and `re`.

* Other changes

  * Added command line interface to load applications and start servers.
  * Introduced a :class:`ConfigDict` that makes accessing configuration a lot easier (attribute access and auto-expanding namespaces).
  * Added support for raw WSGI applications to :meth:`Bottle.mount`.
  * :meth:`Bottle.mount` parameter order changed.
  * :meth:`Bottle.route` now accepts an import string for the ``callback`` parameter.
  * Dropped Gunicorn 0.8 support. Current supported version is 0.13.
  * Added custom options to Gunicorn server.
  * Finally dropped support for type filters. Replace with a custom plugin of needed.


Release 0.9
============

.. rubric:: Whats new?

* A brand new plugin-API. See :doc:`plugins/index` and :doc:`plugins/dev` for details.
* The :func:`route` decorator got a lot of new features. See :meth:`Bottle.route` for details.
* New server adapters for `gevent <http://www.gevent.org/>`_, `meinheld <http://meinheld.org/>`_ and `bjoern <https://github.com/jonashaag/bjoern>`_.
* Support for SimpleTAL templates.
* Better runtime exception handling for mako templates in debug mode.
* Lots of documentation, fixes and small improvements.
* A new :data:`Request.urlparts <BaseRequest.urlparts>` property.

.. rubric:: Performance improvements

* The :class:`Router` now special-cases ``wsgi.run_once`` environments to speed up CGI.
* Reduced module load time by ~30% and optimized template parser. See `8ccb2d </commit/8ccb2d>`_, `f72a7c </commit/f72a7c>`_ and `b14b9a </commit/b14b9a>`_ for details.
* Support for "App Caching" on Google App Engine. See `af93ec </commit/af93ec>`_.
* Some of the rarely used or deprecated features are now plugins that avoid overhead if the feature is not used.

.. rubric:: API changes

This release is mostly backward compatible, but some APIs are marked deprecated now and will be removed for the next release. Most noteworthy:

* The ``static`` route parameter is deprecated. You can escape wild-cards with a backslash.
* Type-based output filters are deprecated. They can easily be replaced with plugins.


Release 0.8
============

.. rubric:: API changes

These changes may break compatibility with previous versions.

* The built-in Key/Value database is not available anymore. It is marked deprecated since 0.6.4
* The Route syntax and behaviour changed.

  * Regular expressions must be encapsulated with ``#``. In 0.6 all non-alphanumeric characters not present in the regular expression were allowed.
  * Regular expressions not part of a route wildcard are escaped automatically. You don't have to escape dots or other regular control characters anymore. In 0.6 the whole URL was interpreted as a regular expression. You can use anonymous wildcards (``/index:#(\.html)?#``) to achieve a similar behaviour.

* The ``BreakTheBottle`` exception is gone. Use :class:`HTTPResponse` instead.
* The :class:`SimpleTemplate` engine escapes HTML special characters in ``{{bad_html}}`` expressions automatically. Use the new ``{{!good_html}}`` syntax to get old behaviour (no escaping).
* The :class:`SimpleTemplate` engine returns unicode strings instead of lists of byte strings.
* ``bottle.optimize()`` and the automatic route optimization is obsolete.
* Some functions and attributes were renamed:

  * :attr:`Request._environ <BaseRequest._environ>` is now :attr:`Request.environ <BaseRequest.environ>`
  * :attr:`Response.header <BaseResponse.header>` is now :attr:`Response.headers <BaseResponse.headers>`
  * :func:`default_app` is obsolete. Use :func:`app` instead.

* The default :func:`redirect` code changed from 307 to 303.
* Removed support for ``@default``. Use ``@error(404)`` instead.

.. rubric:: New features


This is an incomplete list of new features and improved functionality.

* The :class:`Request` object got new properties: :attr:`Request.body <BaseRequest.body>`, :attr:`Request.auth <BaseRequest.auth>`, :attr:`Request.url <BaseRequest.url>`, :attr:`Request.header <BaseRequest.header>`, :attr:`Request.forms <BaseRequest.forms>`, :attr:`Request.files <BaseRequest.files>`.
* The :meth:`Response.set_cookie <BaseResponse.set_cookie>` and :meth:`Request.get_cookie <BaseRequest.get_cookie>` methods are now able to encode and decode python objects. This is called a *secure cookie* because the encoded values are signed and protected from changes on client side. All pickle-able data structures are allowed.
* The new :class:`Router` class drastically improves performance for setups with lots of dynamic routes and supports named routes (named route + dict = URL string).
* It is now possible (and recommended) to return :exc:`HTTPError` and :exc:`HTTPResponse` instances or other exception objects instead of raising them.
* The new function :func:`static_file` equals :func:`send_file` but returns a :exc:`HTTPResponse` or :exc:`HTTPError` instead of raising it. :func:`send_file` is deprecated.
* New :func:`get`, :func:`post`, :func:`put` and :func:`delete` decorators.
* The :class:`SimpleTemplate` engine got full unicode support.
* Lots of non-critical bugfixes.

