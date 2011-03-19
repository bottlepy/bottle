.. module:: bottle

========================
Plugin Development Guide
========================

This guide explains the plugin API and how to write custom plugins. I suggest reading :ref:`plugins` first if you have not done that already. You might also want to have a look at the :doc:`/plugins/index` for some practical examples.

.. note::

    This is a draft. If you see any errors or find that a specific part is not explained clear enough, please tell the `mailing-list <mailto:bottlepy@googlegroups.com>`_ or file a `bug report <https://github.com/defnull/bottle/issues>`_.

How Plugins Work: The Basics
============================

The plugin API builds on the concept of `decorators <http://docs.python.org/glossary.html#term-decorator>`_. To put it briefly, a plugin is a decorator that is applied to every single route of an application. Any decorator that can be applied to a route callback doubles as a plugin.

Of course, this is a simplification. Plugins can do a lot more than just decorating route callbacks, but it is a good starting point. Lets have a look at some code::

    from bottle import response, install
    import time

    def stopwatch(callback):
        def wrapper(*args, **kargs):
            start = time.time()
            rv = callback(*args, **kwargs)
            end = time.time()
            response.headers['X-Exec-Time'] = str(end - start)
            return rv
        return wrapper

    bottle.install(stopwatch)

This plugin measures the execution time for each request and adds an appropriate ``X-Exec-Time`` header to the response. As you can see, the plugin returns a wrapper and the wrapper calls the original callback recursively. This is how decorators usually work.

The last line tells Bottle to install the plugin to the default application. This causes the plugin to be automatically applied to all routes of that application. In other words, ``stopwatch()`` is called once for each route callback and the return value is used as a replacement for the original callback.

Plugins are applied on demand, that is, as soon as a route is requested for the first time. For this to work properly in multi-threaded environments, the plugin needs to be thread-safe. This is not a problem most of the time, but keep it in mind.

Once all plugins are applied to a route, the prepared callback is cached and subsequent requests are handled by the cached version directly. This means that a plugin is usually applied only once to a specific route. That cache, however, is cleared every time the list of installed plugins changes. Your plugin should be able to decorate the same route more than once.

The decorator API is quite limited, though. You don't know anything about the route being decorated or the associated application object and have no way to efficiently store data that is shared among all routes. But fear not! Plugins are not limited to just decorator functions. Bottle accepts anything as a plugin as long as it is callable or implements an extended API. This API is described below and gives you a lot of control over the whole process.



Plugin API
==========

:class:`Plugin` is not a real class (you cannot import it from :mod:`bottle`) but an interface that plugins are expected to implement. Bottle accepts any object of any type as a plugin, as long as it conforms to the following API.

.. class:: Plugin(object)
    
    Plugins must be callable or implement :meth:`apply`. If :meth:`apply` is defined, it is always preferred over calling the plugin directly. All other methods and attributes are optional.
    
    .. attribute:: name
        
        Both :meth:`Bottle.uninstall` and the `skip` parameter of :meth:`Bottle.route()` accept a name string to refer to a plugin or plugin type. This works only for plugins that have a name attribute.
    
    .. method:: setup(app)

        Called as soon as the plugin is installed to an application (see :meth:`Bottle.install`). The only parameter is the associated application object. This method is *not* called on plugins that are applied directly to routes via the :meth:`Bottle.route()` decorator.

    .. method:: __call__(callback)
        
        As long as :meth:`apply` is not defined, the plugin itself is used as a decorator and applied directly to each route callback. The only parameter is the callback to decorate. Whatever is returned by this method replaces the original callback. If there is no need to wrap or replace a given callback, just return the unmodified callback parameter.
        
    .. method:: apply(callback, context)
    
        If defined, this method is used instead of :meth:`__call__` to decorate route callbacks. The additional context parameter is a dictionary that contains any keyword arguments passed to the :meth:`Bottle.route()` decorator, as well as some additional meta-information about the route being decorated. See :ref:`route-context` for details.

    .. method:: close()
    
        Called immediately before the plugin is uninstalled or the application is closed (see :meth:`Bottle.uninstall` or :meth:`Bottle.close`). This method is *not* called on plugins that are applied directly to routes via the :func:`route` decorator.



.. _route-context:

Route Context
=============

The route context dictionary stores meta-information about a specific route. It is passed to :meth:`Plugin.apply` along with the route callback and contains the following values:

===========  =================================================================
Key          Description
===========  =================================================================
rule         The rule string (e.g. ``/wiki/:page``) as it is passed to the
             router.
method       An uppercase HTTP method string (e.g. ``GET``).
callback     The original callback with no plugins or wrappers applied. Useful
             for introspection.
name         The name of the route (if specified) or ``None``.
apply        A list of route-specific plugins (see :meth:`Bottle.route`).
skip         A list of plugins to not apply to this route
             (see :meth:`Bottle.route`).
app          The associated application object.
config       Additional keyword arguments passed to the :meth:`Bottle.route`
             decorator are stored in this dictionary. Used for route-specific
             plugin configuration and meta-data.
id           An internal handle used by bottle to identify a route.
===========  =================================================================

The :meth:`Bottle.route()` decorator accepts multiple rules and methods in a single call, but the context dictionary refers to a specific pair only. :meth:`Plugin.apply` is called once for each combination of ``rule`` and ``method``, even if they all map to the same route callback.
   
Keep in mind that the `config` dictionary is shared between all plugins. It is always a good idea to add a unique prefix or, if your plugin needs a lot of configuration, store it in a separate dictionary within the `config` dictionary. This helps to avoid naming collisions between plugins.

Manipulating the Context Dictionary
-----------------------------------

While the :ref:`route context dictionary <route-context>` is mutable, changes may have unpredictable effects on other plugins. It is most likely a bad idea to monkey-patch a broken configuration instead of providing a helpful error message and let the user fix it properly.

In some rare cases, however, it might be justifiable to break this rule. After you made your changes to the context dictionary, raise :exc:`RouteReset` as an exception. This removes the current route from the callback cache and causes all plugins to be re-applied. The router is not updated, however. Changes to `rule` or `method` values have no effect on the router, but only on plugins. This may change in the future, though.



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
            conf = context['config'].get('sqlite') or {}
            dbfile = conf.get('dbfile', self.dbfile)
            autocommit = conf.get('autocommit', self.autocommit)
            dictrows = conf.get('dictrows', self.dictrows)
            keyword = conf.get('keyword', self.keyword)
            
            # Test if the original callback accepts a 'db' keyword.
            # Ignore it if it does not need a database handle.
            args = inspect.getargspec(context['callback'])[0]
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
    
    @route('/show/:page')
    def show(page, db):
        row = db.execute('SELECT * from pages where name=?', page).fetchone()
        if row:
            return template('showpage', page=row)
        return HTTPError(404, "Page not found")

    @route('/static/:fname#.*#')
    def static(fname):
        return static_file(fname, root='/some/path')

    @route('/admin/set/:db#[a-zA-Z]+#', skip=[sqlite])
    def change_dbfile(db):
        sqlite.dbfile = '/tmp/%s.db' % db
        return "Switched DB to %s.db" % db

The first route needs a database connection and tells the plugin to create a handle by requesting a ``db`` keyword argument. The second route does not need a database and is therefore ignored by the plugin. The third route does expect a 'db' keyword argument, but explicitly skips the sqlite plugin. This way the argument is not overruled by the plugin and still contains the value of the same-named url argument.

