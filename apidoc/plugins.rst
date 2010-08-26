==============
Plugins
==============

Bottles core features cover most of the common use-cases, but as a micro-framework it has its limits. This is where "Plugins" come into play. Plugins add specific functionality to the framework in a convenient way and are portable and re-usable across applications.

Common Uses Cases
======================

This is an incomplete list of thinks a plugin can do.

* Execute code before and/or after each request.
* Open a database connection before each request and close it afterwards.
* Create, load and update user sessions.
* Log, change or remove keyword arguments passed to a callback.
* Manage a cache for frequently accessed pages.
* Cache, filter or manipulate the output of callbacks.

Installing Plugins
==================

Plugins can be installed application-wide or just to some specific routes that need additional functionality. The sqlite Plugin for example is smart enough to only affect callbacks with a 'db' keyword argument. Because of this, we can install the plugin application-wide with no additional overhead. Callbacks that do not need a database connection are skipped by the plugin and not touched at all.

Application-wide Installation
-----------------------------

To install a specific plugin to all routes of an application, pass its name or its class object to the :func:`install` function and provide additional keyword arguments if the plugin requires configuration. It is important that you do not instantiate the plugin yourself. Bottle does that for you at a later point::

    install('sqlite', dbfile='/tmp/test.db')     # install by name
    install(SQLitePlugin, dbfile='/tmp/test.db') # install by class

The example above adds the plugin to the default application. If you want to install the plugin to a separate application object, use the :meth:`Bottle.install` method instead of the global shortcut::

    # Create a new application object
    app = bottle.Bottle()
    # Install plugin to this application
    app.install('sqlite', dbfile='/tmp/test.db')

Bottle calls the setup-routine of the plugin and connects it to the application. The plugin is not applied to the route callbacks yet. This is delayed to make sure no routes are missed. You can install plugins first and routes alter, if you want to.

.. rubric:: Plugins Usage example

The effects and APIs of plugins are manifold and depend on the specific plugin. The 'sqlite' plugin for example detects callbacks that require a ``db`` keyword argument and creates a fresh database connection object every time the callback is called. This makes it very convenient to use the database::

    install('sqlite', dbfile='/tmp/test.db')

    @route('/show/:post_id')
    def show(db, post_id):
        c = db.execute('SELECT title, content FROM posts WHERE id = ?',
                       (int(post_id),))
        row = c.fetchone()
        return template('show_post', title=row['title'], text=row['content'])

    @route('/contact')
    def contact_page():
        ''' This callback does not need a db connection. Because the 'db'
            keyword argument is missing, the sqlite plugin ignores this callback
            completely. '''
        return template('contact')

Other plugin may populate the thread-save :data:`local` object, change details of the :data:`request`, filter the data returned by the callback or bypass the callback completely. An "auth" plugin for example may check for a valid session and return a login page instead of calling the original callback. What happens exactly depends on the plugin.

.. rubric:: Skip or Disable Plugins

You may want to explicitly disable a plugin for a small number of routes. This
is possible using the `disable` option of the :func:`route` decorator::

    # Save the return value of install() to get a handle for this plugin
    plugin_instance = install('sqlite')

    @route('/open/:db', disable=[plugin_instance])
    def open_db(db):
        # The 'db' keyword argument is not replaced by the plugin this time.
        if db in ('test', 'test2'):
            # The plugin instance can be used for runtime configuration, too.
            plugin_instance.dbfile = '/tmp/%s.db' % db
            return "Database File switched to: /tmp/%s.db" % db
        abort(404, "No such database.")



Route-specific Installation
-----------------------------

Plugins that implement the :class:`BasePlugin` API double as decorators. This is useful if you want to install a plugin only to a small number of routes or need a different configuration for different routes::

    sqlite_mem  = SQLitePlugin(dbfile=':memory:')
    sqlite_disk = SQLitePlugin(dbfile='/some/path')

    @route('/chat')
    @sqlite_mem
    def chat_callback(db):
        ''' Uses memory mapped data '''
        db.execute(...)

    @route('/forum')
    @sqlite_disc
    def forum_handler(db):
        ''' Uses persistent data '''
        db.execute(...)

This example connects two plugins to the default application but does not automatically installs them to any routes. Instead, you can now control which callbacks are affected by decorating them with the plugin manually.

To connect to an application other than the default one, pass the application object to the plugin during initialisation::

    app = bottle.Bottle()
    app_bound_plugin = SQLitePlugin(app, dbfile=':memory:')

Just a note: The sqlite plugin offers a better way to access multiple databases. It let you configure the name of the keyword argument it looks for::

    install('sqlite', dbfile=':memory:', keyword='cache')
    install('sqlite', dbfile='/some/path', keyword='db')

    @route('/chat')
    def chat_callback(cache):
        cache.execute(...)

    @route('/forum')
    def forum_handler(db):
        db.execute(...)








Writing Plugins
==================

The plugin API follows the concept of configurable decorators: A plugin class creates a callable object that is later applied to all or a subset of all routes of an application. Once you understand how decorators work, writing plugins is a snap.

A common base class (:class:`BasePlugin`) is used to simplify plugin development and ensure portability. All plugins inherit from :class:`BasePlugin` and override the :meth:`BasePlugin.setup` and :meth:`BasePlugin.wrap` methods as needed.

This example shows a minimal plugin implementation and is a good starting point for new plugins::

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


Hook-Based Plugins
------------------


::

    class HookPlugin(BasePlugin):
        plugin_name = 'hook'

        def setup(self, app, **config):
            self.app = app
            self.app.add_hook('before_request', self.before_request)
            self.app.add_hook('after_request', self.after_request)

        def before_request(self):
            pass

        def after_request(self):
            pass

Middleware Plugins
------------------

::

    class MiddlewarePlugin(BasePlugin):
        plugin_name = 'middleware'

        def setup(self, app, **config):
            self.app.wsgi = SomeMiddleware(self.app.wsgi, **config)


Plugin Example: SqlitePlugin
============================

OK, lets write a plugin that actually does something useful::

    import sqlite3
    import inspect

    def accepts_keyword(func, name):
        ''' Return True if it is save to pass a named keyword argument to
            func. This works even on functions that were previously wrapped
            with another BasePlugin based decorator.
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
