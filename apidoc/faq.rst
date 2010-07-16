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

In :ref:`dynamic route syntax <tutorial-dynamic-routes>`, a placeholder token (``:name``) matches everything up to the next slash. This equals to ``[^/]+`` in regular expression syntax. To accept slashes too, you have to add a custom regular pattern to the placeholder. An example: ``/images/:filepath#.*#`` would match ``/images/icons/error.png`` but ``/images/:filename`` won't.






.. rubric:: Footnotes

.. [1] Because they are. See <http://www.ietf.org/rfc/rfc3986.txt>

