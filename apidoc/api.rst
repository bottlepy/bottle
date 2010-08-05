==============================
API Reference
==============================

.. module:: bottle
   :platform: Unix, Windows
   :synopsis: WSGI micro framework
.. moduleauthor:: Marcel Hellkamp <marc@paws.de>

This is an API reference, NOT documentation. If you are new to bottle, have a look at the :doc:`tutorial`.

Module Contents
=====================================
The module defines several functions, constants, and an exception.

.. function:: app()

   Return the current *default application* (see :class:`Bottle`).
   Actually, this is a callable instance of :class:`AppStack` and implements a stack-like API.

.. autofunction:: debug

.. autofunction:: run

.. autofunction:: load_app

.. autodata:: request

.. autodata:: response

.. autodata:: HTTP_CODES


Routing 
-------------------

Bottle maintains a stack of :class:`Bottle` instances (see :func:`app` and :class:`AppStack`) and
uses the top of the stack as a *default application* for some of the module-level functions
and decorators.

.. function:: route(path, method='GET', name=None)

   Decorator to bind a function to a path. This equals :meth:`Bottle.route` using the current default application.

.. function:: get(...)
              post(...)
              put(...)
              delete(...)

   These are equal to :func:`route` with the `method` parameter set to the corresponding verb.

.. function:: error(...)

   Calls :meth:`Bottle.error` using the default application.

.. function:: url(...)

   Calls :meth:`Bottle.url` using the default application.

WSGI and HTTP Utilities
----------------------------

.. autofunction:: parse_date

.. autofunction:: parse_auth

.. autofunction:: cookie_encode

.. autofunction:: cookie_decode

.. autofunction:: cookie_is_encoded

.. autofunction:: yieldroutes

.. autofunction:: path_shift


Data Structures
----------------------

.. autoclass:: MultiDict
   :members:

.. autoclass:: HeaderDict
   :members:
   
.. autoclass:: AppStack
   :members:

Exceptions
---------------

.. autoexception:: BottleException
   :members:

.. autoexception:: HTTPResponse
   :members:

.. autoexception:: HTTPError
   :members:



The :class:`Bottle` Class
=========================

.. autoclass:: Bottle
   :members:

HTTP :class:`Request` and :class:`Response` objects
===================================================

The :class:`Request` class wraps a WSGI environment and provides helpful methods to parse and access form data, cookies, file uploads and other metadata. Most of the attributes are read-only.

The :class:`Response` class on the other hand stores header and cookie data that is to be sent to the client.

.. note::

   You usually don't instantiate :class:`Request` or :class:`Response` yourself, but use the module-level instances :data:`bottle.request` and :data:`bottle.response` only. These hold the context for the current request cycle and are updated on every request. Their attributes are thread-local, so it is safe to use the global instance in multi-threaded environments too.

.. autoclass:: Request
   :members:

.. autoclass:: Response
   :members:







Templates
=========

All template engines supported by :mod:`bottle` implement the :class:`BaseTemplate` API. This way it is possible to switch and mix template engines without changing the application code at all. 

.. autoclass:: BaseTemplate
   :members:
   
   .. automethod:: __init__

.. autofunction:: view

.. autofunction:: template

You can write your own adapter for your favourite template engine or use one of the predefined adapters. Currently there are four fully supported template engines:

========================   ===============================   ====================   ========================
Class                      URL                               Decorator              Render function
========================   ===============================   ====================   ========================
:class:`SimpleTemplate`    :doc:`stpl`                       :func:`view`           :func:`template`
:class:`MakoTemplate`      http://www.makotemplates.org      :func:`mako_view`      :func:`mako_template`
:class:`CheetahTemplate`   http://www.cheetahtemplate.org/   :func:`cheetah_view`   :func:`cheetah_template`
:class:`Jinja2Template`    http://jinja.pocoo.org/           :func:`jinja2_view`    :func:`jinja2_template`
========================   ===============================   ====================   ========================

To use :class:`MakoTemplate` as your default template engine, just import its specialised decorator and render function::

  from bottle import mako_view as view, mako_template as template

