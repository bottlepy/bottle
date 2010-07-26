.. module:: bottle

==================
Plugin Development
==================

Bottles core features cover most of the common use-cases, but as a micro-framework it has its limits. This is where "Plugins" come into play. Plugins add specific functionality to the framework in a convenient way and are portable and re-usable across applications. Browse the list of :doc:`available plugins <plugins>` and see if someone has solved your problem already. If not, then read ahead. This guide explains the use of middleware, decorators and the hook-api that makes writing plugins for bottle a snap.

.. _best-practise:

Best Practice
=============

These rules are recommendations only, but following them makes it a lot easier for others to use your plugin.

.. rubric:: Initializing Plugins

Importing a plugin-module should not have any side-effects and particularly **never install the plugin automatically**. Instead, plugins should define a class or a function that handles initialization:

The class-constructor or init-function should accept an instance of :class:`Bottle` as its first optional keyword argument and install the plugin to that application. If the `app`-argument is empty, the plugin should default to :func:`default_app`. All other arguments are specific to the plugin and optional.

For consistency, function-names should start with "`init_`" and class-names should end in "`Plugin`". It is ok to add an ``init_*`` alias for a class, but the class itself should conform to PEP8. Example::

    import bottle

    def init_myfeature(app=None):
        if not app:
            app = bottle.default_app()

        @app.hook('before_request')
        def before_hook():
            pass

    class MyFeaturePlugin(object):
        def __init__(app=None):
            self.app = app or bottle.default_app()
            self.app.add_hook('before_request', self.before_hook)

        def before_hook():
            pass

.. rubric:: Plugin Configuration

Plugins should use the :attr:`Bottle.config` dictionary and the ``plugin.[name]`` namespace for their configuration. This way it is possible to pre-configure plugins or change the configuration at runtime in a plugin-independent way. Example::

    import bottle

    class MyFeaturePlugin(object):
        def __init__(app=None):
            self.app = app or bottle.default_app()
            self.app.add_hook('before_request', self.before_hook)
        
        def before_hook():
            value = self.app.config.get('plugins.myfeature.key', 'default')
            ...

.. rubric:: WSGI Middleware

WSGI middleware should not wrap the entire application object, but only the :meth:`Bottle.wsgi` method. This way the app object stays intact and more than one middleware can be applied without conflicts.




Writing Plugins
===============

In most cases, plug-ins are used to alter the the request/response circle in some way. They add, manipulate or remove information from the request and/or alter the data returned to the browser. Some plug-ins do not touch the request itself, but have other side effects such as opening and closing database connections or cleaning up temporary files. Apart from that, you can differentiate plug-ins by the point of contact with the application:

Middleware
    WSGI-middleware wraps an entire application. It is an application itself and calls the wrapped application internally. This way a middleware can alter both the incoming environ-dict and the response iterable before it is returned to the server. This is transparent to the wrapped application and does not require any special support or preparation. The downside of this approach is that the request and response objects are both not available and you have to deal with raw WSGI.

Decorators
    The decorator approach is best for wrapping a small number of routes while leaving all other callbacks untouched. If your application requires session support or database connections for only some of the routes, choose this approach. With a decorator you have full access to the request and response objects and the unfiltered return value of the wrapped callback.

Hooks
    .. versionadded:: 0.9

    With `hooks` you can register functions to be called at specific stages during the request circle. The most interesting hooks are `before_request` and `after_request`. Both affect all routes in an application, have full control over the request and response objects and can manipulate the route-callback return value at will. This new API fills the gap between middleware and decorators and is described in detail further down this guide.

Which technique is best for your plugin depends on the level and scope of interaction you need with the framework and application. Combinations are possible, too. The following table sums it up:

==========================  ========== ===== ==========
Aspect                      Middleware Hooks Decorators
==========================  ========== ===== ==========
Affects whole application   Yes        Yes   No
Access to Bottle features   No         Yes   Yes
==========================  ========== ===== ==========

Writing Middleware
-------------------

WSGI middleware is not specific to Bottle and there are `several <http://www.python.org/dev/peps/pep-0333/#middleware-components-that-play-both-sides>`_ `detailed <http://www.rufuspollock.org/2006/09/28/wsgi-middleware/>`_ `explanations <http://pylonshq.com/docs/en/0.9.7/concepts/#wsgi-middleware>`_ and `collections <http://wsgi.org/wsgi/Middleware_and_Utilities>`_ available. If you want to apply a WSGI middleware, wrap the :class:`Bottle` application object and you're done::

    app = bottle.app()          # Get the WSGI callable from bottle
    app = MyMiddleware(app=app) # Wrap it
    bottle.run(app)             # Run it

This approach works fine, but is not very portable (see :ref:`best-practise`). A more general approach is to define a function that takes care of the plugin initialization and keeps the original application object intact::

    import bottle
    def init_my_middleware(app=None, **config):
        # Default to the global application object
        if not app:
            app = bottle.app()
        # Do not wrap the entire application, but only the WSGI part
        app.wsgi = MyMiddleware(app=app.wsgi, config=config)

Now ``app`` is still an instance of :class:`Bottle` and all methods remain accessible. Other plugins can wrap ``app.wsgi`` again without any conflicts.



Writing Decorators
-------------------

Bottle uses decorators all over the place, so you should already now how to use them. Writing a decorator (or a decorator factory, see below) is not that hard, too. Basically a decorator is a function that takes a function object and returns either the same or a new function object. This way it is possible to `wrap` a function and alter its input and output whenever that function gets called. Decorators are an extremely flexible way to reduce repetitive work::

  from bottle import route

  def integer_id(func):
      ''' Make sure that the ``id`` keyword argument is an integer. '''
      def wrapper(*args, **kwargs):
          if 'id' in kwargs and not isinstance(kwargs['id'], int):
              kwargs['id'] = int(kwargs['id'])
          return func(*args, **kwargs)
      return wrapper
  
  @route('/get/:id#[0-9]+#')
  @integer_id
  def get_object(id, ...):
      ...

.. note::
    Decorators are applied in reverse order (the decorator closest to the 'def' statement is applied first). This is important if you want to apply more than one decorator.

.. rubric:: Decorator factories: Configurable decorators

Let's go one step further: A `decorator factory` is a function that return a decorator. Because inner functions have access to the local variables of the outer function they were defined in, we can use this to configure the behavior of our decorator. Here is an example::

  from bottle import request, response, abort

  def auth_required(users, realm='Secure Area'):
      def decorator(func):
          def wrapper(*args, **kwargs):
              name, password = request.auth()
              if name not in users or users[name] != password:
                  response.headers['WWW-Authenticate'] = 'Basic realm="%s"' % realm
                  abort('401', 'Access Denied. You need to login first.')
              kwargs['user'] = name
              return func(*args, **kwargs)
          return wrapper
      return decorator

  @route('/secure/area')
  @auth_required(users={'Bob':'1234'})
  def secure_area(user):
      print 'Hello %s' % user

Of cause it is a bad idea to store clear passwords in a dictionary. But besides that, this example is actually quite complete and usable as it is. 

Using Hooks
----------------

.. versionadded:: 0.9

As described above, hooks allow you to register functions to be called at specific stages during the request circle. There are currently only two hooks available:

before_request
    This hook is called immediately before each route callback.

after_request
    This hook is called immediately after each route callback.

You can use the :func:`hook` or :meth:`Bottle.hook` decorator to register a function to a hook. This example shows how to open and close a database connection (SQLite 3) with each request::

  import sqlite3
  import bottle

  def init_sqlite(app=None, dbfile=':memory:'):
      if not app:
          app = bottle.app()

      @app.hook('before_request')
      def before_request():
          bottle.local.db = sqlite3.connect(dbfile)

      @app.hook('after_request')
      def after_request():
          bottle.local.db.close()

The :data:`local` object is used to store the database handle during the request. It is a thread-save object (just like :data:`request` and :data:`response` are) even if it looks like a global module variable. Here is an example for an application using this plugin::

  from bottle import default_app, local, route, run
  from plugins.sqlite import init_sqlite # Or whatever you named your plugin

  @route('/wiki/:name')
  @view('wiki_page')
  def show_page(name):
      sql = 'select title, text rom wiki_pages where name = ?'
      cursor = local.db.execute(sql, name)
      entry = cursor.fetch()
      return dict(name=name, title=entry[0], text=entry[1])

  init_sqlite(dbfile='wiki.db') # Install plugin to default app

  if __name__ == '__main__':
      run() # Run default app

.. rubric:: Plugin Classes

The problem with the last example is that you cannot access the plugin or the  database object outside of a running server instance. Let's rewrite the plugin and use a class this time::

  import sqlite3
  import bottle

  class SQlitePlugin(object):
      def __init__(self, app=None, dbfile=':memory:'):
          self.app = app or bottle.app()
          self.dbfile = dbfile

          @self.app.hook('before_request')
          def before_request():
              bottle.local.db = self.connect()

          @self.app.hook('after_request')
          def after_request():
              bottle.local.db.close()

      def connect(self):
          return sqlite3.connect(self.dbfile)

  init_sqlite = SQlitePlugin # Alias for consistency

Now we can access the ``connect()`` method outside of a route callback and even reconfigure the plugin at runtime::

  # [...] same as wiki-app example above
  # but this time, we save the return value of init_sqlite()
  sqlite_plugin = init_sqlite(dbfile='wiki.db')

  if __name__ == '__main__':
      if 'development' in sys.argv:
          sqlite_plugin.dbfile = ':memory:' # reconfigure plugin
          db = sqlite_plugin.connect()      # reuse plugin methods
          db.execfile('test_database.sql')
          db.commit()
          db.close()
      run() # Run default app

Now if we call this script with a ``development`` command-line flag, it uses a memory-mapped test database instead of the real one.

