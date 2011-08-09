==============================
API Reference
==============================

.. module:: bottle
   :platform: Unix, Windows
   :synopsis: WSGI micro framework
.. moduleauthor:: Marcel Hellkamp <marc@gsites.de>

This is a mostly auto-generated API. If you are new to bottle, you might find the
narrative :doc:`tutorial` more helpful. 




Module Contents
=====================================

The module defines several functions, constants, and an exception.

.. autofunction:: debug

.. autofunction:: run

.. autofunction:: load_app

.. autodata:: request

.. autodata:: response

.. autodata:: HTTP_CODES

.. function:: app()
              default_app()

    Return the current :ref:`default-app`. Actually, these are callable instances of :class:`AppStack` and implement a stack-like API.


Routing 
-------------------

Bottle maintains a stack of :class:`Bottle` instances (see :func:`app` and :class:`AppStack`) and uses the top of the stack as a *default application* for some of the module-level functions and decorators.


.. function:: route(path, method='GET', callback=None, **options)
              get(...)
              post(...)
              put(...)
              delete(...)

   Decorator to install a route to the current default application. See :meth:`Bottle.route` for details.

   
.. function:: error(...)

   Decorator to install an error handler to the current default application. See :meth:`Bottle.error` for details.


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

.. autoclass:: WSGIHeaderDict
   :members:

.. autoclass:: AppStack
   :members:

   .. method:: pop()

      Return the current default application and remove it from the stack.


Exceptions
---------------

.. autoexception:: BottleException
   :members:

.. autoexception:: HTTPResponse
   :members:

.. autoexception:: HTTPError
   :members:

.. autoexception:: RouteReset
   :members:




The :class:`Bottle` Class
=========================

.. autoclass:: Bottle
   :members:

.. autoclass:: Route
    :members:


The :class:`Request` Object
===================================================

The :class:`Request` class wraps a WSGI environment and provides helpful methods to parse and access form data, cookies, file uploads and other metadata. Most of the attributes are read-only.

You usually don't instantiate :class:`Request` yourself, but use the module-level :data:`bottle.request` instance. This instance is thread-local and refers to the `current` request, or in other words, the request that is currently processed by the request handler in the current context. `Thread locality` means that you can safely use a global instance in a multithreaded environment.

.. autoclass:: Request
   :members:

.. autoclass:: LocalRequest
   :members:

.. autoclass:: BaseRequest
   :members:




The :class:`Response` Object
===================================================

The :class:`Response` class stores the HTTP status code as well as headers and cookies that are to be sent to the client. Similar to :data:`bottle.request` there is a thread-local :data:`bottle.response` instance that can be used to adjust the `current` response. Moreover, you can instantiate :class:`Response` and return it from your request handler. In this case, the custom instance overrules the headers and cookies defined in the global one.

.. autoclass:: Response
   :members:

.. autoclass:: LocalResponse
   :members:

.. autoclass:: BaseResponse
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

