.. highlight:: python
.. currentmodule:: bottle

===========================
Release Notes and Changelog
===========================


Release 0.9
===========

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


.. rubric:: Thanks to

Thanks to all the people who found bugs, sent patches, spread the word, helped each other on the mailing-list and made this release possible. You are awesome :) Really, you are.

I hope the following (alphabetically sorted) list is complete. If you miss your name on that list (or want your name removed) please :doc:`tell me <contact>`.

    Adam R. Smith, Alexey Borzenkov, 'apheage', 'BillMa', Brandon Gilmore, Branko Vukelic, Damien Degois, David Buxton, Duane Johnson, Frank Murphy, Ian Davis, Itamar Nabriski, 'iurisilvio', Jeff Nichols, Jeremy Kelley, 'joegester', Jonas Haag, 'Karl', 'Kraken', Kyle Fritz, 'm35', 'masklinn', `reddit <http://reddit.com/r/python>`_, Santiago Gala, Sean M. Collins, 'Seth', Sigurd Høgsbro, Stuart Rackham, Sun Ning, Tomás A. Schertel, Tristan Zajonc, 'voltron' and Wieland Hoffmann

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

