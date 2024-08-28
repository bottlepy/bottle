.. currentmodule:: bottle

.. _plugins:

=============
Using Plugins
=============

.. versionadded:: 0.9

Bottle's core features cover most common use-cases, but as a micro-framework it has its limits. This is where "Plugins" come into play. Plugins add missing functionality to the framework, integrate third party libraries, or just automate some repetitive work.

We have a growing list of :doc:`/plugins/list` and most plugins are designed to be portable and re-usable across applications. Maybe your problem has already been solved and a ready-to-use plugin exists. If not, write your own. See :doc:`/plugins/dev` for details.

.. _plugin-basics:

Plugin Basics
=============

Bottles Plugin system builds on the concept of `decorators <http://docs.python.org/glossary.html#term-decorator>`_. To put it briefly, a plugin is a decorator applied to all route callback in an application. Plugins can do more than just decorating route callbacks, but it is still a good starting point to understand the concept. Lets have a look at a practical example::

    from bottle import response

    def stopwatch(callback):
        def wrapper(*args, **kwargs):
            start = time.time()
            result = callback(*args, **kwargs)
            end = time.time()
            response.headers['X-Exec-Time'] = str(end - start)
            return result
        return wrapper

This "stopwatch" decorator measures the execution time of the wrapped function and then writes the result in the non-standard ``X-Exec-Time`` response header. You could just manually apply this decorator to all your route callbacks and call it a day::
    
    from bottle import route

    @route("/timed")
    @stopwatch  # <-- This works, but do not do this
    def timed():
        time.sleep(1)
        return "DONE"

But we wouldn't be talking about a plugin system if there wasn't a better way to do this!

Managing Plugins
================

Explicitly applying decorators to every single route in a growing application quickly becomes tedious and error-prone. If you really want to apply something to *all* routes, there is a simpler way::

    from bottle import route, install

    install(stopwatch)

    @route("/timed")
    def timed():
        ...

The :func:`install` method registries a plugin to be automatically applied to all routes in an application. It does not matter if you call :func:`install` before or after binding routes, all plugins are always applied to all routes. The order of :func:`install` calls is important though. If there are multiple plugins, they are applied in the same order the were installed.

Any callable object that works as a route callback decorator is a valid plugin. This includes normal decorators, classes, callables instances, but also plugins that implement the extended :class:`Plugin` API. See :ref:`plugindev` for details. 

You can also :func:`uninstall` a previously installed plugin by name, class or instance::

    sqlite_plugin = SQLitePlugin(dbfile='/tmp/test.db')
    install(sqlite_plugin)

    uninstall(sqlite_plugin) # uninstall a specific plugin
    uninstall(SQLitePlugin)  # uninstall all plugins of that type
    uninstall('sqlite')      # uninstall all plugins with that name
    uninstall(True)          # uninstall all plugins at once

Plugins can be installed and also removed at any time, even at runtime while serving requests. They are applied on-demand, that is, as soon as the route is requested for the first time. This enables some neat tricks (e.g. installing slow debugging or profiling plugins only when needed) but should not be overused. Each time the list of plugins changes, the route cache is flushed and all plugins need to be re-applied.

.. note::
    The module-level :func:`install` and :func:`uninstall` functions affect the :ref:`default application <default-app>`. To manage plugins for a specific application, use the corresponding methods on a :class:`Bottle` instance.

Selectively apply or skip Plugins
---------------------------------

Most plugins are smart enough to ignore routes that do not need their functionality and do not add any overhead to those routes, but you can also apply or skip specific plugins per route if you need to.

To apply a decorator or plugin to just a single route, do not :func:`install` it, but use the ``apply`` keyword of the :func:`route` decorator instead::

    @route('/timed', apply=[stopwatch])
    def timed():
        ...

Route-level plugins are applied first (before application-wide plugins) but handled exactly like normal plugins otherwise.

You can also explicitly disable an installed plugin for a number of routes. The :func:`route` decorator has a ``skip`` parameter for this purpose::

    install(stopwatch)

    @route('/notime', skip=[stopwatch])
    def no_time():
        pass

The ``skip`` parameter accepts a single value or a list of values. You can use a plugin name, class or instance to identify the plugin that should be skipped. Set ``skip=True`` to skip all plugins at once.


Plugins and :meth:`Bottle.mount`
--------------------------------

Most plugins are specific to the application they were installed to and should not affect sub-applications mounted with :meth:`Bottle.mount`. Here is an example::

    root = Bottle()
    root.install(plugins.WTForms())
    root.mount('/blog', apps.blog)

    @root.route('/contact')
    def contact():
        return template('contact', email='contact@example.com')

When mounting an application, Bottle creates a proxy-route on the mounting application that forwards all requests to the mounted application. Plugins are disabled for this kind of proxy-route by default. Our (fictional) ``WTForms`` plugin affects the ``/contact`` route, but does not affect the routes of the ``/blog`` sub-application.

This behavior is intended as a sane default, but can be overridden. The following example re-activates all plugins for a specific proxy-route::

    root.mount('/blog', apps.blog, skip=None)

Note that a plugin sees the whole sub-application as a single route, namely the proxy-route mentioned above. To wrap each individual route of the sub-application, you have to install the plugin to the mounted application directly.

Configuring Plugins
===================

Most plugins accept configuration as parameters passed to their constructor. This is the easiest and most obvious way to configure a plugin, e.g. to tell a database plugin which database to connect to::

    install(SQLitePlugin(dbfile='/tmp/test.db', ...))

Newer plugins may also read values from :attr:`Bottle.config` (see :doc:`../configuration`). This is useful for configuration that should be easy to change or override for a specific deployment. This pattern even supports runtime changes using :ref:`config hooks <conf-hook>`::

    app.config["sqlite.db"] = '/tmp/test.db'
    app.install(SQLitePlugin())

Plugins can also inspect the routes they are applied to and change their behavior for individual routes. Plugin authors have full access to the undecorated route callback as well as parameters passed to the :meth:`route` decorator, including custom parameters that are otherwise ignored by bottle. This allows for a great level of flexibility. Common patterns include:

* A database plugin may automatically start a transaction if the route callback accepts a ``db`` keyword.
* A forms plugin may ignore routes that do not listen to ``POST`` requests.
* An access control plugin may check for a custom ``roles_allowed`` parameter passed to the :meth:`route` decorator.

In any case, check the plugin documentation for details. If you want to write your own plugins, check out :doc:`dev`.