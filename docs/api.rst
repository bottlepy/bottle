==============================
API Reference
==============================

.. module:: bottle
   :platform: Unix, Windows
   :synopsis: WSGI micro framework
.. moduleauthor:: Marcel Hellkamp <marc@gsites.de>

Bottle prides itself on having source code that is easy to read and follow, so most questions about APIs or inner workings can be answered quickly by inspecting sources. Your IDE should give you the same information you'll find on this page, as most of it is auto-generates from docstrings and method signatures anyway. If you are new to bottle, you may find the :doc:`tutorial` more helpful as a starting point.



Global functions
================

The module defines several functions, constants, and an exception.

.. function:: app()
              default_app()

    Return the current :ref:`default-app`. This is actually a callable instances of :class:`AppStack`.

.. autofunction:: debug

.. autofunction:: install

.. autofunction:: uninstall

.. autofunction:: run


Global decorators
=================

Bottle maintains a stack of :class:`Bottle` instances (see :func:`app` and :class:`AppStack`)
and uses the top of the stack as a :ref:`default-app` for some of the module-level functions
and decorators. All of those have a corresponding method on the :class:`Bottle` class.

.. function:: route(path, method='GET', callback=None, **options)
              get(...)
              post(...)
              put(...)
              delete(...)
              patch(...)

   Decorator to install a route to the current default application. See :meth:`Bottle.route` for details.

.. function:: error(...)

   Decorator to install an error handler to the current default application. See :meth:`Bottle.error` for details.

.. autofunction:: hook



Request Context
===============

The global :data:`request` and :data:`response` instances are only valid from within an request handler function and represent the *current* HTTP request or response.

.. autodata:: request

.. autodata:: response


Helper Functions
================

.. autofunction:: abort

.. autofunction:: redirect

.. autofunction:: static_file


Exceptions
==========

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


The :class:`Request` Object
===================================================

The :class:`Request` class wraps a WSGI environment and provides helpful methods to parse and access form data, cookies, file uploads and other metadata. Most of the attributes are read-only.

.. autoclass:: Request
   :members:

.. autoclass:: BaseRequest
   :members:
   :special-members: __setattr__

.. autoclass:: LocalRequest
   :members:


The :class:`Response` Object
============================

The :class:`Response` class stores the HTTP status code as well as headers and cookies that are to be sent to the client. Similar to :data:`bottle.request` there is a thread-local :data:`bottle.response` instance that can be used to adjust the `current` response. Moreover, you can instantiate :class:`Response` and return it from your request handler. In this case, the custom instance overrules the headers and cookies defined in the global one.

.. autoclass:: Response
   :members:

.. autoclass:: BaseResponse
   :members:

.. autoclass:: LocalResponse
   :members:


Data Structures
===============

.. autoclass:: AppStack
   :members:

   .. method:: pop()

      Return the current default application and remove it from the stack.

.. autoclass:: ConfigDict
   :members:

.. autoclass:: MultiDict
   :members:

.. autoclass:: WSGIHeaderDict
   :members:

.. autoclass:: HeaderDict
   :members:

.. autoclass:: FormsDict
   :members:

.. autoclass:: FileUpload
   :members:


Request routing
===============

.. autoclass:: Router
    :members:

.. autoclass:: Route
    :members:


Templating
==========

All template engines supported by :mod:`bottle` implement the :class:`BaseTemplate` API. This way it is possible to switch and mix template engines without changing the application code at all.

.. autoclass:: BaseTemplate
   :members:

.. autofunction:: view

.. autofunction:: template

.. autodata:: TEMPLATE_PATH

   Global search path for templates.


You can write your own adapter for your favourite template engine or use one of the predefined adapters. Currently there are four fully supported template engines:

========================   ==================================   ====================   ========================
Class                      URL                                  Decorator              Render function
========================   ==================================   ====================   ========================
:class:`SimpleTemplate`    :doc:`stpl`                          :func:`view`           :func:`template`
:class:`MakoTemplate`      http://www.makotemplates.org         :func:`mako_view`      :func:`mako_template`
:class:`CheetahTemplate`   http://www.cheetahtemplate.org/      :func:`cheetah_view`   :func:`cheetah_template`
:class:`Jinja2Template`    https://jinja.palletsprojects.com/   :func:`jinja2_view`    :func:`jinja2_template`
========================   ==================================   ====================   ========================

To use :class:`MakoTemplate` as your default template engine, just import its specialised decorator and render function::

  from bottle import mako_view as view, mako_template as template

HTTP utilities
==============

.. autofunction:: parse_date

.. autofunction:: parse_auth

.. autofunction:: cookie_encode

.. autofunction:: cookie_decode

.. autofunction:: cookie_is_encoded

.. autofunction:: path_shift

.. autodata:: HTTP_CODES
  :no-value:

Misc utilities
==============

.. autoclass:: DictProperty

.. autoclass:: cached_property

.. autoclass:: lazy_attribute

.. autofunction:: yieldroutes

.. autofunction:: load

.. autofunction:: load_app
   