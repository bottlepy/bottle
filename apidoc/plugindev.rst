.. module:: bottle

================
Writing Plugins
================

Bottles core features cover most of the common use-cases, but as a micro-framework it has its limits. This is where "Plugins" come into play. Plugins add specific functionality to the framework in a convenient way and are portable and re-usable across applications. Browse the list of :doc:`available plugins <plugins>` and see if someone has solved your problem already. If not, then read ahead. This guide explains the use of middleware, decorators and the hook-api that makes writing plugins for bottle a snap.

.. rubric:: The different Types of Extensions

In most cases, plug-ins are used to alter the the request/response circle in some way. They add, manipulate or remove information from the request and/or alter the data returned to the browser. Some plug-ins do not touch the request itself, but have other side effects such as opening and closing database connections or cleaning up temporary files. Apart from that, you can differentiate plug-ins by the point of contact with the application:

Decorators
    The decorator approach is best for wrapping a small number of routes while leaving all other callbacks untouched. If your application requires session support or database connections for only some of the registered routes, choose this approach. With a decorator you have full access to the request and response objects and the unfiltered return value of the wrapped callback.

Middleware
    WSGI-middleware wraps an entire application. It is an application itself and calls the wrapped application internally. This way a middleware can alter both the incoming environ-dict and the response iterable before it is returned to the server. This is transparent to the wrapped application and does not require any special support or preparation. The downside of this approach is that the request and response objects are both not available and you have to deal with raw WSGI.

Hooks
    .. versionadded:: 0.9
    With `hooks` you can register functions to be called during specific stages of the request circle. The most interesting hooks are `before_request` and `after_request`. Apart from decorators, hooks affect all routes in an application but you still have full control over the request and response objects and can manipulate the callback return value at will. This technique is described in detail further down this guide.


The following table sums it up:

==========================  ========== ===== =========
Aspect                      Middleware Hooks Decorator
==========================  ========== ===== =========
Affects whole application   Yes        Yes   No
Access to Bottle features   No         Yes   Yes
==========================  ========== ===== =========

Writing Middleware
==================

WSGI-Middleware is not specific to Bottle and there are `several <http://www.python.org/dev/peps/pep-0333/#middleware-components-that-play-both-sides>`_ `detailed <http://www.rufuspollock.org/2006/09/28/wsgi-middleware/>`_ `explanations <http://pylonshq.com/docs/en/0.9.7/concepts/#wsgi-middleware>`_ and `collections <http://wsgi.org/wsgi/Middleware_and_Utilities>`_ available. If you want to apply a WSGI middleware, wrap the :class:`Bottle` application object and you're done::

    app = bottle.app()          # Get the WSGI callable from bottle
    app = MyMiddleware(app=app) # Wrap it
    bottle.run(app)             # Run it

Just one little trick. Instead of wrapping the entire :class:`Bottle` application object, you can do this instead::

    app = bottle.app()
    app.wsgi = MyMiddleware(app=app.wsgi)
    bottle.run(app)

Now ``app`` is still an instance of :class:`Bottle` and all methods remain accessible.

Writing Decorators
==================

Bottle uses decorators all over the place, so you should already now how to use them. Writing a decorator (or a decorator factory, see below) is not that hard, too. Basically a decorator is a function that takes a function object and returns either the same or a new function object. This way it is possible to `wrap` a function and alter its input and output whenever that function gets called::

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

Let's go one step further: A `decorator factory` is a function that return a decorator. Because inner functions have access to the local variables of the outer function they were defined in, we can use this to configure the behaviour of our decorator. Here is an example::

  from bottle import request, response, abort

  def auth_required(users, realm='Secure Area'):
      def decorator(func):
          def wrapper(*args, **kwargs):
              name, password = request.auth()
              if name not in users or users[name] != password:
                  response.headers['WWW-Authenticate'] = 'Basic realm="%s"' % realm
                  abort('401', 'Access Denied')
              kwargs['user'] = name
              return func(*args, **kwargs)
          return wrapper
      return decorator

  @route('/secure/area')
  @auth_required(users={'Bob':'1234'})
  def secure_area(user):
      print 'Hello %s' % user

Of cause it is a bad idea to store clear passwords in a dictionary. Apart from that this example is actually quite complete and usable. 

Writing Hooks
================

.. versionadded:: 0.9
As described above, hooks allow you to register functions to be called during specific stages of the request circle. There are currently three hooks available:

before_request
    This hook is called immediately before each route callback.

after_request
    This hook is called immediately after each route callback.

You can use the :func:`hook` or :meth:`Bottle.hook` decorator to register a hook-callback. This example shows how to open and close a database connection (SQLite 3) with each request::


    import sqlite3
    import bottle

    def init_sqlite3(app = None, dbfile=':memory:'):
        if not app:
            app = bottle.app()

        @app.hook('before_request')
        def before_request():
            bottle.local.db = sqlite3.connect(dbfile)

        @app.hook('after_request')
        def after_request():
            bottle.local.db.close()

