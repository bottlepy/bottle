
.. currentmodule:: bottle

.. _plugindev:

===============
Writing Plugins
===============

This guide explains the plugin API and how to write custom plugins. I suggest reading :ref:`plugin-basics` first if you have not done so already. You might also want to have a look at the :doc:`/plugins/index` for some practical examples.

Plugin API
==========

Any callable that accepts a function and returns a function is a valid plugin. This simple approach has its limits, though. Plugins that need more context and control can implement the extended :class:`Plugin` interface and hook into advanced features. Note that this is not a real class you can import from :mod:`bottle`, just a contract that plugins must implement to be recognized as extended plugins.

.. class:: Plugin

    Plugins must be callable or implement :meth:`apply`. If :meth:`apply` is defined, it is always preferred over calling the plugin directly. All other methods and attributes are optional.

    .. attribute:: name

        Both :meth:`Bottle.uninstall` and the `skip` parameter of :meth:`Bottle.route()` accept a name string to refer to a plugin or plugin type. This works only for plugins that have a name attribute.

    .. attribute:: api

        The Plugin API is still evolving. This integer attribute tells bottle which version to use. If it is missing, bottle defaults to the first version. The current version is ``2``. See :ref:`plugin-changelog` for details.

    .. method:: setup(self, app: Bottle)

        Called as soon as the plugin is installed to an application via :meth:`Bottle.install`. The only parameter is the application object the plugin is installed to. This method is *not* called for plugins that were applied to routes via `apply`, but only for plugins installed to an application.

    .. method:: __call__(self, callback)

        As long as :meth:`apply` is not defined, the plugin itself is used as a decorator and applied directly to each route callback. The only parameter is the callback to be decorated. Whatever is returned by this method replaces the original callback. If there is no need to wrap or replace a given callback, just return the unmodified callback parameter.

    .. method:: apply(self, callback, route: Route)

        If defined, this method is used in favor of :meth:`__call__` to decorate route callbacks. The additional `route` parameter is an instance of :class:`Route` and provides a lot of context and meta-information and about the route to be decorated. See :ref:`route-context` for details.

    .. method:: close(self)

        Called as soon as the plugin is uninstalled or the application is closed (see :meth:`Bottle.uninstall` or :meth:`Bottle.close`). This method is *not* called for plugins that were applied to routes via `apply`, but only for plugins installed to an application.


.. _plugin-changelog:

Plugin API Versions
-------------------

The Plugin API is still evolving and changed with Bottle 0.10 to address certain issues with the route context dictionary. To ensure backwards compatibility with 0.9 Plugins, we added an optional :attr:`Plugin.api` attribute to tell bottle which API to use. The API differences are summarized here.

* **Bottle 0.9 API 1** (:attr:`Plugin.api` not present)

  * Original Plugin API as described in the 0.9 docs.

* **Bottle 0.10 API 2** (:attr:`Plugin.api` equals 2)

  * The `context` parameter of the :meth:`Plugin.apply` method is now an instance of :class:`Route` instead of a context dictionary.


.. _route-context:

The Route Context
=================

The :class:`Route` instance passed to :meth:`Plugin.apply` provides detailed information about the to-be-decorated route, the original route callback and route specific configuration.

Keep in mind that :attr:`Route.config` is local to the route, but shared between all plugins. It is always a good idea to add a unique prefix or, if your plugin needs a lot of configuration, store it in a separate namespace within the `config` dictionary. This helps to avoid naming collisions between plugins.

While some :class:`Route` attributes are mutable, changes may have unwanted effects on other plugins and also only affect plugins that were not applied yet. If you need to make changes to the route that are recognized by all plugins, call :meth:`Route.reset` afterwards. This will clear the route cache and apply all plugins again next time the route is called, giving all plugins a chance to adapt to the new config. The router is not updated, however. Changes to `rule` or `method` values have no effect on the router, only on plugins. This may change in the future.


Runtime optimizations
=====================

Once all plugins are applied to a route, the wrapped route callback is cached to speed up subsequent requests. If the behavior of your plugin depends on configuration, and you want to be able to change that configuration at runtime, you need to read the configuration on each request. Easy enough.

For performance reasons however, it might be worthwhile to return a different wrapper based on current needs, work with closures, or enable or disable a plugin at runtime. Let's take the built-in ``HooksPlugin`` as an example: If no hooks are installed, the plugin removes itself from all routes and has virtually no overhead. As soon as you install the first hook, the plugin activates itself and takes effect again.

To achieve this, you need control over the callback cache: :meth:`Route.reset` clears the cache for a single route and :meth:`Bottle.reset` clears all caches for all routes of an application at once. On the next request, all plugins are re-applied to the route as if it were requested for the first time.


Common patterns
===============

.. rubric:: Dependency or resource injection

Plugins may checks if the callback accepts a specific keyboard parameter and only apply themselves if that parameter is present. For example, route callbacks that expect a ``db`` keyword argument need a database connection. Routes that do not expect such a parameter can be skipped and not decorated. The paramneter name should be configurable to avoid conflicts with other plugins or route parameters.

.. rubric:: Request context properties

Plugins may add new request-local properties to the current :data:`request`, for example ``request.session`` for a durable session or ``request.user`` for logged in users. See :class:`Request.__setattr__ <BaseRequest.__setattr__>`.

.. rubric:: Response type mapping

Plugins may check the return value of the wrapped callback and transform or serialize the output to a new type. The bundled :class:`JsonPlugin` does exactly that.

.. rubric:: Zero overhead plugins

Plugins that are not needed on a specific route should return the callback unchanged. If they want to remove themselves from a route at runtime, they can call :meth:`Route.reset` and skip the route the next time it is triggered.

.. rubric:: Before / after each request

Plugins can be a convenient alternative to ``before_request`` or ``after_request`` hooks (see :meth:`Bottle.add_hook`), especially if both are needed. 


Plugin Example: SQLitePlugin
============================

This plugin provides an sqlite3 database connection handle as an additional keyword argument to wrapped callbacks, but only if the callback expects it. If not, the route is ignored and no overhead is added. The wrapper does not affect the return value, but handles plugin-related exceptions properly. :meth:`Plugin.setup` is used to inspect the application and search for conflicting plugins.

::

    import sqlite3
    import inspect

    class SQLitePlugin:

        name = 'sqlite'
        api = 2

        def __init__(self,
                     dbfile=':memory:',
                     autocommit=True,
                     dictrows=True,
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

        def apply(self, callback, route):
            # Override global configuration with route-specific values.
            conf = route.config.get('sqlite') or {}
            dbfile = conf.get('dbfile', self.dbfile)
            autocommit = conf.get('autocommit', self.autocommit)
            dictrows = conf.get('dictrows', self.dictrows)
            keyword = conf.get('keyword', self.keyword)

            # Test if the original callback accepts a 'db' keyword.
            # Ignore it if it does not need a database handle.
            args = inspect.getargspec(route.callback)[0]
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

This plugin is just an example, but actually usable::

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

The first route needs a database connection and tells the plugin to create a handle by accepting a ``db`` keyword argument. The second route does not need a database and is therefore ignored by the plugin. The third route does expect a 'db' keyword argument, but explicitly skips the sqlite plugin. This way the argument is not overruled by the plugin and still contains the value of the same-named url argument.

