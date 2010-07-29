.. highlight:: python
.. currentmodule:: bottle

===========================
Release Notes and Changelog
===========================


Release 0.9 
===========

This changes are not released yet and are only part of the development documentation.

.. rubric:: New Features

* A new hook-API to inject code immediately before or after the execution of handler callbacks.


Bugfix Release 0.8.2
=====================

* Added backward compatibility wrappers and deprecation warnings to some of the API changes.
* Fixed "FileCheckerThread seems to fail on eggs" (Issue #87)
* Fixed "Bottle.get_url() does not return correct path when SCRIPT_NAME is set." (Issue #83)


Release 0.8
===========

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

