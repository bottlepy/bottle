.. module:: bottle


========================
Plugin Development Guide
========================

This guide explains the plugin API and how to write custom plugins. I suggest reading :ref:`plugins` first if you have not done that already. You might also want to have a look at the :doc:`/plugins/index` for some practical examples.

.. note::

    This is a draft. If you see any errors or find that a specific part is not explained clear enough, please tell the `mailing-list <mailto:bottlepy@googlegroups.com>`_ or file a `bug report <https://github.com/bottlepy/bottle/issues>`_.


How Plugins Work: The Basics
============================

The plugin API builds on the concept of `decorators <http://docs.python.org/glossary.html#term-decorator>`_. To put it briefly, a plugin is a decorator applied to every single route callback of an application.

This is just a simplification. Plugins can do a lot more than just decorating route callbacks, but it is a good starting point. Lets have a look at some code::

    from bottle import response, install
    import time

    def stopwatch(callback):
        def wrapper(*args, **kwargs):
            start = time.time()
            body = callback(*args, **kwargs)
            end = time.time()
            response.headers['X-Exec-Time'] = str(end - start)
            return body
        return wrapper

    install(stopwatch)

This plugin measures the execution time for each request and adds an appropriate ``X-Exec-Time`` header to the response. As you can see, the plugin returns a wrapper and the wrapper calls the original callback recursively. This is how decorators usually work.

The last line tells Bottle to install the plugin to the default application. This causes the plugin to be automatically applied to all routes of that application. In other words, ``stopwatch()`` is called once for each route callback and the return value is used as a replacement for the original callback.

Plugins are applied on demand, that is, as soon as a route is requested for the first time. For this to work properly in multi-threaded environments, the plugin should be thread-safe. This is not a problem most of the time, but keep it in mind.

Once all plugins are applied to a route, the wrapped callback is cached and subsequent requests are handled by the cached version directly. This means that a plugin is usually applied only once to a specific route. That cache, however, is cleared every time the list of installed plugins changes. Your plugin should be able to decorate the same route more than once.

The decorator API is quite limited, though. You don't know anything about the route being decorated or the associated application object and have no way to efficiently store data that is shared among all routes. But fear not! Plugins are not limited to just decorator functions. Bottle accepts anything as a plugin as long as it is callable or implements an extended API. This API is described below and gives you a lot of control over the whole process.


Plugin API
==========

:class:`Plugin` is not a real class (you cannot import it from :mod:`bottle`) but an interface that plugins are expected to implement. Bottle accepts any object of any type as a plugin, as long as it conforms to the following API.

.. class:: Plugin(object)

    Plugins must be callable or implement :meth:`apply`. If :meth:`apply` is defined, it is always preferred over calling the plugin directly. All other methods and attributes are optional.

    .. attribute:: name

        Both :meth:`Bottle.uninstall` and the `skip` parameter of :meth:`Bottle.route()` accept a name string to refer to a plugin or plugin type. This works only for plugins that have a name attribute.

    .. attribute:: api

        The Plugin API is still evolving. This integer attribute tells bottle which version to use. If it is missing, bottle defaults to the first version. The current version is ``2``. See :ref:`plugin-changelog` for details.

    .. method:: setup(self, app)

        Called as soon as the plugin is installed to an application (see :meth:`Bottle.install`). The only parameter is the associated application object.

    .. method:: __call__(self, callback)

        As long as :meth:`apply` is not defined, the plugin itself is used as a decorator and applied directly to each route callback. The only parameter is the callback to decorate. Whatever is returned by this method replaces the original callback. If there is no need to wrap or replace a given callback, just return the unmodified callback parameter.

    .. method:: apply(self, callback, route)

        If defined, this method is used in favor of :meth:`__call__` to decorate route callbacks. The additional `route` parameter is an instance of :class:`Route` and provides a lot of meta-information and context for that route. See :ref:`route-context` for details.

    .. method:: close(self)

        Called immediately before the plugin is uninstalled or the application is closed (see :meth:`Bottle.uninstall` or :meth:`Bottle.close`).


Both :meth:`Plugin.setup` and :meth:`Plugin.close` are *not* called for plugins that are applied directly to a route via the :meth:`Bottle.route()` decorator, but only for plugins installed to an application.


.. _plugin-changelog:

Plugin API changes
------------------

The Plugin API is still evolving and changed with Bottle 0.10 to address certain issues with the route context dictionary. To ensure backwards compatibility with 0.9 Plugins, we added an optional :attr:`Plugin.api` attribute to tell bottle which API to use. The API differences are summarized here.

* **Bottle 0.9 API 1** (:attr:`Plugin.api` not present)

  * Original Plugin API as described in the 0.9 docs.

* **Bottle 0.10 API 2** (:attr:`Plugin.api` equals 2)

  * The `context` parameter of the :meth:`Plugin.apply` method is now an instance of :class:`Route` instead of a context dictionary.

.. _route-context:


The Route Context
=================

The :class:`Route` instance passed to :meth:`Plugin.apply` provides detailed informations about the associated route. The most important attributes are summarized here:

===========  =================================================================
Attribute    Description
===========  =================================================================
app          The application object this route is installed to.
rule         The rule string (e.g. ``/wiki/<page>``).
method       The HTTP method as a string (e.g. ``GET``).
callback     The original callback with no plugins applied. Useful for
             introspection.
name         The name of the route (if specified) or ``None``.
plugins      A list of route-specific plugins. These are applied in addition to
             application-wide plugins. (see :meth:`Bottle.route`).
skiplist     A list of plugins to not apply to this route (again, see
             :meth:`Bottle.route`).
config       Additional keyword arguments passed to the :meth:`Bottle.route`
             decorator are stored in this dictionary. Used for route-specific
             configuration and meta-data.
===========  =================================================================

For your plugin, :attr:`Route.config` is probably the most important attribute. Keep in mind that this dictionary is local to the route, but shared between all plugins. It is always a good idea to add a unique prefix or, if your plugin needs a lot of configuration, store it in a separate namespace within the `config` dictionary. This helps to avoid naming collisions between plugins.


Changing the :class:`Route` object
----------------------------------

While some :class:`Route` attributes are mutable, changes may have unwanted effects on other plugins. It is most likely a bad idea to monkey-patch a broken route instead of providing a helpful error message and let the user fix the problem.

In some rare cases, however, it might be justifiable to break this rule. After you made your changes to the :class:`Route` instance, raise :exc:`RouteReset` as an exception. This removes the current route from the cache and causes all plugins to be re-applied. The router is not updated, however. Changes to `rule` or `method` values have no effect on the router, but only on plugins. This may change in the future, though.


Runtime optimizations
=====================

Once all plugins are applied to a route, the wrapped route callback is cached to speed up subsequent requests. If the behavior of your plugin depends on configuration, and you want to be able to change that configuration at runtime, you need to read the configuration on each request. Easy enough.

For performance reasons, however, it might be worthwhile to choose a different wrapper based on current needs, work with closures, or enable or disable a plugin at runtime. Let's take the built-in HooksPlugin as an example: If no hooks are installed, the plugin removes itself from all affected routes and has virtually no overhead. As soon as you install the first hook, the plugin activates itself and takes effect again.

To achieve this, you need control over the callback cache: :meth:`Route.reset` clears the cache for a single route and :meth:`Bottle.reset` clears all caches for all routes of an application at once. On the next request, all plugins are re-applied to the route as if it were requested for the first time.

Both methods won't affect the current request if called from within a route callback, of cause. To force a restart of the current request, raise :exc:`RouteReset` as an exception.


Plugin Example: SQLitePlugin
============================

This plugin provides an sqlite3 database connection handle as an additional keyword argument to wrapped callbacks, but only if the callback expects it. If not, the route is ignored and no overhead is added. The wrapper does not affect the return value, but handles plugin-related exceptions properly. :meth:`Plugin.setup` is used to inspect the application and search for conflicting plugins.

::

    import sqlite3
    import inspect

    class SQLitePlugin(object):
        ''' This plugin passes an sqlite3 database handle to route callbacks
        that accept a `db` keyword argument. If a callback does not expect
        such a parameter, no connection is made. You can override the database
        settings on a per-route basis. '''

        name = 'sqlite'
        api = 2

        def __init__(self, dbfile=':memory:', autocommit=True, dictrows=True,
                     keyword='db'):
             self.dbfile = dbfile
             self.autocommit = autocommit
             self.dictrows = dictrows
             self.keyword = keyword

        def setup(self, app):
            ''' Make sure that other installed plugins don't affect the same
                keyword argument.'''
            for other in app.plugins:
                if not isinstance(other, SQLitePlugin): continue
                if other.keyword == self.keyword:
                    raise PluginError("Found another sqlite plugin with "\
                    "conflicting settings (non-unique keyword).")

        def apply(self, callback, context):
            # Override global configuration with route-specific values.
            conf = context.config.get('sqlite') or {}
            dbfile = conf.get('dbfile', self.dbfile)
            autocommit = conf.get('autocommit', self.autocommit)
            dictrows = conf.get('dictrows', self.dictrows)
            keyword = conf.get('keyword', self.keyword)

            # Test if the original callback accepts a 'db' keyword.
            # Ignore it if it does not need a database handle.
            args = inspect.getargspec(context.callback)[0]
            if keyword not in args:
                return callback

            def wrapper(*args, **kwargs):
                # Connect to the database
                db = sqlite3.connect(dbfile)
                # This enables column access by name: row['column_name']
                if dictrows: db.row_factory = sqlite3.Row
                # Add the connection handle as a keyword argument.
                kwargs[keyword] = db

                try:
                    rv = callback(*args, **kwargs)
                    if autocommit: db.commit()
                except sqlite3.IntegrityError, e:
                    db.rollback()
                    raise HTTPError(500, "Database Error", e)
                finally:
                    db.close()
                return rv

            # Replace the route callback with the wrapped one.
            return wrapper

This plugin is actually useful and very similar to the version bundled with Bottle. Not bad for less than 60 lines of code, don't you think? Here is a usage example::

    sqlite = SQLitePlugin(dbfile='/tmp/test.db')
    bottle.install(sqlite)

    @route('/show/<page>')
    def show(page, db):
        row = db.execute('SELECT * from pages where name=?', page).fetchone()
        if row:
            return template('showpage', page=row)
        return HTTPError(404, "Page not found")

    @route('/static/<fname:path>')
    def static(fname):
        return static_file(fname, root='/some/path')

    @route('/admin/set/<db:re:[a-zA-Z]+>', skip=[sqlite])
    def change_dbfile(db):
        sqlite.dbfile = '/tmp/%s.db' % db
        return "Switched DB to %s.db" % db

The first route needs a database connection and tells the plugin to create a handle by requesting a ``db`` keyword argument. The second route does not need a database and is therefore ignored by the plugin. The third route does expect a 'db' keyword argument, but explicitly skips the sqlite plugin. This way the argument is not overruled by the plugin and still contains the value of the same-named url argument.

