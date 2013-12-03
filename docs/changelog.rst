.. highlight:: python
.. currentmodule:: bottle

===========================
Release Notes and Changelog
===========================



Release 0.12
==============

* New SimpleTemplate parser implementation
  * Support for multi-line code blocks (`<% ... %>`).
  * The keywords `include` and `rebase` are functions now and can accept variable template names.
* The new :meth:`BaseRequest.route` property returns the :class:`Route` that originally matched the request.
* Removed the ``BaseRequest.MAX_PARAMS`` limit. The hash collision bug in CPythons dict() implementation was fixed over a year ago. If you are still using Python 2.5 in production, consider upgrading or at least make sure that you get security fixed from your distributor.
* New :class:`ConfigDict` API (see :doc:`configuration`)

More information can be found in this `development blog post <http://blog.bottlepy.org/2013/07/19/preview-bottle-012.html>`_.


Release 0.11
==============

* Native support for Python 2.x and 3.x syntax. No need to run 2to3 anymore.
* Support for partial downloads (``Range`` header) in :func:`static_file`.
* The new :class:`ResourceManager` interface helps locating files bundled with an application.
* Added a server adapter for `waitress <http://docs.pylonsproject.org/projects/waitress/en/latest/>`_.
* New :meth:`Bottle.merge` method to install all routes from one application into another.
* New :attr:`BaseRequest.app` property to get the application object that handles a request.
* Added :meth:`FormsDict.decode()` to get an all-unicode version (needed by WTForms).
* :class:`MultiDict` and subclasses are now pickle-able.

.. rubric:: API Changes

* :attr:`Response.status` is a read-write property that can be assigned either a numeric status code or a status string with a reason phrase (``200 OK``). The return value is now a string to better match existing APIs (WebOb, werkzeug). To be absolutely clear, you can use the read-only properties :attr:`BaseResponse.status_code` and :attr:`BaseResponse.status_line`.

.. rubric:: API Deprecations

* :class:`SimpleTALTemplate` is now deprecating. There seems to be no demand.

Release 0.10
==============

* Plugin API v2

  * To use the new API, set :attr:`Plugin.api` to ``2``.
  * :meth:`Plugin.apply` receives a :class:`Route` object instead of a context dictionary as second parameter. The new object offers some additional information and may be extended in the future.
  * Plugin names are considered unique now. The topmost plugin with a given name on a given route is installed, all other plugins with the same name are silently ignored.

* The Request/Response Objects

  * Added :attr:`BaseRequest.json`, :attr:`BaseRequest.remote_route`, :attr:`BaseRequest.remote_addr`, :attr:`BaseRequest.query` and :attr:`BaseRequest.script_name`.
  * Added :attr:`BaseResponse.status_line` and :attr:`BaseResponse.status_code` attributes. In future releases, :attr:`BaseResponse.status` will return a string (e.g. ``200 OK``) instead of an integer to match the API of other common frameworks. To make the transition as smooth as possible, you should use the verbose attributes from now on.
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
  * :meth:`Bottle.route` now accpets an import string for the ``callback`` parameter.
  * Dropped Gunicorn 0.8 support. Current supported version is 0.13.
  * Added custom options to Gunicorn server.
  * Finally dropped support for type filters. Replace with a custom plugin of needed.


Release 0.9
============

.. rubric:: Whats new?

* A brand new plugin-API. See :ref:`plugins` and :doc:`plugindev` for details.
* The :func:`route` decorator got a lot of new features. See :meth:`Bottle.route` for details.
* New server adapters for `gevent <http://www.gevent.org/>`_, `meinheld <http://meinheld.org/>`_ and `bjoern <https://github.com/jonashaag/bjoern>`_.
* Support for SimpleTAL templates.
* Better runtime exception handling for mako templates in debug mode.
* Lots of documentation, fixes and small improvements.
* A new :data:`Request.urlparts` property.

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

  * :attr:`Request._environ` is now :attr:`Request.environ`
  * :attr:`Response.header` is now :attr:`Response.headers`
  * :func:`default_app` is obsolete. Use :func:`app` instead.

* The default :func:`redirect` code changed from 307 to 303.
* Removed support for ``@default``. Use ``@error(404)`` instead.

.. rubric:: New features


This is an incomplete list of new features and improved functionality.

* The :class:`Request` object got new properties: :attr:`Request.body`, :attr:`Request.auth`, :attr:`Request.url`, :attr:`Request.header`, :attr:`Request.forms`, :attr:`Request.files`.
* The :meth:`Response.set_cookie` and :meth:`Request.get_cookie` methods are now able to encode and decode python objects. This is called a *secure cookie* because the encoded values are signed and protected from changes on client side. All pickle-able data structures are allowed.
* The new :class:`Router` class drastically improves performance for setups with lots of dynamic routes and supports named routes (named route + dict = URL string).
* It is now possible (and recommended) to return :exc:`HTTPError` and :exc:`HTTPResponse` instances or other exception objects instead of raising them.
* The new function :func:`static_file` equals :func:`send_file` but returns a :exc:`HTTPResponse` or :exc:`HTTPError` instead of raising it. :func:`send_file` is deprecated.
* New :func:`get`, :func:`post`, :func:`put` and :func:`delete` decorators.
* The :class:`SimpleTemplate` engine got full unicode support.
* Lots of non-critical bugfixes.



============
Contributors
============

.. include:: ../AUTHORS
