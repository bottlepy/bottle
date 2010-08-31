==============
Plugins
==============

Bottles core features cover most of the common use-cases, but as a micro-framework it has its limits. This is where "Plugins" come into play. Plugins add specific functionality to the framework in a convenient way and are portable and re-usable across applications.


Using Plugins
==================

Plugins can be installed application-wide or just to some specific routes that need additional functionality. Most plugins are save to be installed to all routes and are smart enough to not add overhead to callbacks that do not need their functionality.

Let us take the 'sqlite' plugin for example. It only affects route callbacks that need a database connection. Other routes are left alone. Because of this, we can install the plugin application-wide with no additional overhead.


Application-wide Installation
-----------------------------

To install a specific plugin to all routes of an application, pass its name or its class to the :func:`install` function and provide additional keyword arguments if the plugin requires configuration. It is important that you do not instantiate the plugin yourself. Bottle does that for you::

    install('sqlite', dbfile='/tmp/test.db')     # install by name
    install(SQLitePlugin, dbfile='/tmp/test.db') # install by class

Of cause you need to import the plugin module before you can pass a class. If you reference the plugin by name, Bottle tries to import it automatically by searching for a module or package with the name ``bottle_<plugin-name>`` and importing it.

.. note::
    To install a plugin to a specific application object instead of the global default, use the :meth:`Bottle.install` method on the application object.

Bottle calls the setup-routine of the plugin and connects it to the application. The plugin is not applied to the route callbacks yet. This is delayed to make sure no routes are missed. You can install plugins first and routes alter, if you want to.



Route-specific Installation
-----------------------------

Plugins that implement the :class:`BasePlugin` API double as configurable decorators. This is useful if you want to install a plugin to only a small number of routes::

    auth_plugin = AuthPlugin(check_user_func=...)

    @route('/private')
    @auth_plugin
    def private_callback():
        user = local.user

Even if this plugin only affects a single route, it is connected to the default application and able to access the app configuration (:attr:`Bottle.config`). To connect the plugin to a different application object, pass it a positional argument during initialisation::

    app = bottle.Bottle()
    auth_plugin = AuthPlugin(app, check_user_func=...)



Plugins Usage example
---------------------

The effects and APIs of plugins are manifold and depend on the specific plugin. The 'sqlite' plugin for example detects callbacks that require a ``db`` keyword argument and creates a fresh database connection object every time the callback is called. This makes it very convenient to use the database::

    install('sqlite', dbfile='/tmp/test.db')

    @route('/show/:post_id')
    def show(db, post_id):
        c = db.execute('SELECT title, content FROM posts WHERE id = ?', (int(post_id),))
        row = c.fetchone()
        return template('show_post', title=row['title'], text=row['content'])

    @route('/contact')
    def contact_page():
        ''' This callback does not need a db connection. Because the 'db'
            keyword argument is missing, the sqlite plugin ignores this callback
            completely. '''
        return template('contact')

Other plugin may populate the thread-save :data:`local` object, change details of the :data:`request`, filter the data returned by the callback or bypass the callback completely. An "auth" plugin for example could check for a valid session and return a login page instead of calling the original callback. What happens exactly depends on the plugin.



Plugin Blacklists
-----------------

You may want to explicitly disable a plugin for a small number of routes. This
is possible using the `skip` parameter of the :func:`route` decorator::

    # Save the return value of install() to get a handle for this plugin
    sqlite_plugin = install('sqlite')

    @route('/open/:db', skip=[sqlite_plugin])
    def open_db(db):
        # The 'db' keyword argument is not touched by the plugin this time.
        if db in ('test', 'test2'):
            # The plugin instance can be used for runtime configuration, too.
            sqlite_plugin.dbfile = '/tmp/%s.db' % db
            return "Database File switched to: /tmp/%s.db" % db
        abort(404, "No such database.")






Writing Plugins
==================

The plugin API follows the concept of configurable decorators that are applied to all or a subset of all routes of an application. Decorators are a very flexible and pythonic way to reduce repetitive work. A common base class (:class:`BasePlugin`) is used to simplify plugin development and ensure portability.

.. rubric:: Short Introduction to Decorators

Basically a decorator is a function that takes a callable object and returns a new one. Most decorators are used to create `wrapper` functions that wrap the original and alter its input and/or output values at runtime. Accordingly, decorator factories are functions or classes that return a decorator::

    def factory(**config):
        def decorator(func):
            def wrapper(*args, **kwargs):
                # Alter args or kwargs
                rv = func(*args, **kwargs) # Call original function
                # Alter return value
                return rv
            return wrapper
        return decorator
    
Inner functions have access to the local variables of the outer function they were defined in. This is why the ``wrapper()`` function in this example is able to call ``func`` internally or access the config-dict passed to the factory.


Common Plugin Interface: :class:`BasePlugin` 
--------------------------------------------

All plugins inherit from :class:`BasePlugin` and override the :meth:`BasePlugin.setup` and :meth:`BasePlugin.wrap` methods as needed. This example shows a minimal plugin implementation and is a good starting point for new plugins::

    class DummyPlugin(BasePlugin):
        ''' This plugin does nothing useful. '''
        plugin_name = 'dummy' # Don't forget to name your plugin

        def setup(self, app, **config):
            ''' This is called only once during plugin initialisation. '''
            self.app = app
            self.config = config

        def wrap(self, callback):
            ''' This decorator is applied to each route callback just before
                the server is started. '''
            # @functools.wraps(func) is not needed. Bottle does that for you.
            def wrapper(*a, **ka):
                # Do stuff before the callback is called
                return_value = callback(*a, **ka) # Call the callback
                # Do stuff after the callback is called
                return return_value # Return something
            return wrapper # Return the wrapped callback

* The plugin class name should end in 'Plugin' to make clear what it is.
* The :attr:`BasePlugin.plugin_name` attribute is used for name-based plugin referencing and must be unique to your plugin.
* The :meth:`BasePlugin.setup` method is called once during plugin initialisation. The first parameter is an instance of :class:`Bottle` and equals the default application if the user did not specify a different one. Additional parameters may be accepted or required for configuration.
* The :meth:`BasePlugin.wrap` method is called once for each installed route callback and receives the callback as its only argument. It should return a callable and double as a decorator.
* You may add additional methods and attributes as needed. Just make sure that the ``__init__`` and ``__call__`` methods of the base class remain available.



.. rubric:: Middleware Plugins

You do not need the plugin API to install WSGI Middleware to a Bottle application, but is can still be useful::

    class SomeMiddlewarePlugin(BasePlugin):
        plugin_name = 'some_middleware'

        def setup(self, app, **config):
            app.wsgi = SomeMiddleware(app.wsgi, **config)

WSGI middleware should not wrap the entire application object, but only the :meth:`Bottle.wsgi` method. This way the app object stays intact and more than one middleware can be applied without conflicts.



Plugin Example: SqlitePlugin
============================

OK, lets write a plugin that actually does something useful::

    import sqlite3
    import inspect

    def accepts_keyword(func, name):
        ''' Return True if it is save to pass a named keyword argument to
            func. This works even on functions that were previously wrapped
            by another BasePlugin based decorator.
        '''
        while func:
            args, varargs, varkw, defaults = inspect.getargspec(func)
            if name not in args and not varkw:
                return False
            func = getattr(func, '_bottle_wrapped', None)
        return True

    class SQLitePlugin(BasePlugin):
        plugin_name = 'sqlite'

        def setup(self, app, dbfile=':memory:', keyword='db',
                             commit=True, dictrows=True):
            self.dbfile = app.config.get('plugin.sqlite.dbfile', dbfile)
            self.keyword = app.config.get('plugin.sqlite.keyword', keyword)
            self.commit = app.config.get('plugin.sqlite.commit', commit)
            self.dictrows = app.config.get('plugin.sqlite.dictrows', dictrows)

        def wrap(self, callback):
            # Do not wrap callbacks that do not expect a 'db' keyword argument
            if not accepts_keyword(callback, self.keyword):
                return callback
            def wrapper(*args, **kwargs):
                # Connect to the database
                db = self.get_connection()
                # Add the connection handle to the dict of keyword arguments.
                kwargs[self.keyword] = db
                try:
                    rv = callback(*args, **kwargs)
                    if self.commit: db.commit() # Auto-commit
                finally:
                    # Be sure to close the connection.
                    db.close()
                return rv
            return wrapper

        def get_connection(self):
            con = sqlite3.connect(self.dbfile)
            # This allows column access by name: row['column_name']
            if self.dictrows: con.row_factory = sqlite3.Row
            return con

This plugin passes a sqlite3 database handle to callbacks that expect a
`db` parameter. If the callback does not define that parameter, no
connection is made. Not bad for less than 50 lines of code :)

