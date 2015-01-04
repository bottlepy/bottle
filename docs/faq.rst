.. module:: bottle

.. _paste: http://pythonpaste.org/modules/evalexception.html
.. _pylons: http://pylonshq.com/
.. _mod_python: http://www.modpython.org/
.. _mod_wsgi: http://code.google.com/p/modwsgi/

==========================
Frequently Asked Questions
==========================

About Bottle
============

Is bottle suitable for complex applications?
---------------------------------------------

Bottle is a *micro* framework designed for prototyping and building small web applications and services. It stays out of your way and allows you to get things done fast, but misses some advanced features and ready-to-use solutions found in other frameworks (MVC, ORM, form validation, scaffolding, XML-RPC). Although it *is* possible to add these features and build complex applications with Bottle, you should consider using a full-stack Web framework like pylons_ or paste_ instead.


Common Problems and Pitfalls
============================





"Template Not Found" in mod_wsgi/mod_python
--------------------------------------------------------------------------------

Bottle searches in ``./`` and ``./views/`` for templates. In a mod_python_ or mod_wsgi_ environment, the working directory (``./``) depends on your Apache settings. You should add an absolute path to the template search path::

    bottle.TEMPLATE_PATH.insert(0,'/absolut/path/to/templates/')

so bottle searches the right paths.

Dynamic Routes and Slashes
--------------------------------------------------------------------------------

In :ref:`dynamic route syntax <tutorial-dynamic-routes>`, a placeholder token (``<name>``) matches everything up to the next slash. This equals to ``[^/]+`` in regular expression syntax. To accept slashes too, you have to add a custom regular pattern to the placeholder. An example: ``/images/<filepath:path>`` would match ``/images/icons/error.png`` but ``/images/<filename>`` won't.

Problems with reverse proxies
--------------------------------------------------------------------------------

Redirects and url-building only works if bottle knows the public address and location of your application. If you run bottle locally behind a reverse proxy or load balancer, some information might get lost along the way. For example, the ``wsgi.url_scheme`` value or the ``Host`` header might reflect the local request by your proxy, not the real request by the client. Here is a small WSGI middleware snippet that helps to fix these values::

  def fix_environ_middleware(app):
    def fixed_app(environ, start_response):
      environ['wsgi.url_scheme'] = 'https'
      environ['HTTP_X_FORWARDED_HOST'] = 'example.com'
      return app(environ, start_response)
    return fixed_app

  app = bottle.default_app()    
  app.wsgi = fix_environ_middleware(app.wsgi)
  






