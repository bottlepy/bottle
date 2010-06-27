.. highlight:: python
.. currentmodule:: bottle

===========================
Release Notes and Changelog
===========================

Release 0.7
===========

.. rubric:: API changes 


These changes may break compatibility with previous versions.

* The build-in Key/Value database is not available anymore. It is marked deprecated since 0.6.4
* The Route syntax and behaviour changed.

  * Regular expressions must be encapsulated with ``#``. In 0.6 all non-alphanumeric characters not present in the regular expression were allowed.
  * Regular expressions not part of a route wildcard are escaped automatically. You don't have to escape dots or other regular control characters anymore. In 0.6 the whole URL was interpreted as a regular expression. You can use anonymous wildcards (``/index:#(\.html)?#``) to achieve a similar behaviour.
  * Wildcards are escaped with a second colon (``/path/::not_a_wildcard``).

* The ``BreakTheBottle`` exception is gone. Use :class:`HTTPResponse`` instead.
* The :class:`SimpleTemplate` engine escapes HTML special characters in ``{{bad_html}}`` expressions automatically. Use the new ``{{!good_html}}`` syntax to get old behaviour (no escaping).
* The :class:`SimpleTemplate` engine returns unicode strings instead of lists of byte strings.
* ``bottle.optimize()`` and the automatic route optimization is obsolete.
* :attr:`Request._environ` was renamed to :attr:`Request.environ`
* The default :func:`redirect` code changed from 307 to 303.
* Removed support for ``@default``. Use ``@error(404)`` instead.
* `default_app()` is obsolete. Use :func:`app` instead.

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

