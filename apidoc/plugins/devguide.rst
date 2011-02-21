========================
Plugin Development Guide
========================

.. module:: bottle




Plugin API
==========

:class:`Plugin` is not a real class (you cannot import it from :mod:`bottle`) but an interface that plugins are expected to implement. Bottle accepts any object of any type as a plugin, as long as it conforms to the following API.

.. class:: Plugin(object)
    
    Plugins must be callable or implement :meth:`apply`. If :meth:`apply` is defined, it is always preferred over calling the plugin directly. All other methods are optional.
    
    .. attribute:: name
        
        Both :meth:`Bottle.uninstall` and the `skip` parameter of :meth:`Bottle.route()` accept a name string to refer to a plugin or plugin type. This works only for plugins that define a name attribute.
    
    .. method:: setup(app)

        Called as soon as the plugin is installed to an application (see :meth:`Bottle.install`). The only parameter is the associated application object. This method is *not* called on plugins that are applied directly to routes via the :meth:`Bottle.route()` decorator.

    .. method:: __call__(callback)
        
        As long as :meth:`apply` is not defined, the plugin itself is used as a decorator and applied directly to each route callback. The only parameter is the callback to decorate. Whatever is returned by this method replaces the original callback. If there is no need to wrap or replace a given callback, just return the unmodified callback parameter.
        
    .. method:: apply(callback, context)
    
        If defined, this method is used instead of :meth:`__call__` to decorate route callbacks. The additional context parameter is a dictionary that contains any keyword arguments passed to the :meth:`Bottle.route()` decorator, as well as some additional meta-information about the route being decorated. See :ref:`route-context` for details.

    .. method:: close()
    
        Called immediately before the plugin is uninstalled or the application is closed (see :meth:`Bottle.uninstall` or :meth:`Bottle.close`). This method is *not* called on plugins that are applied directly to routes via the :func:`route` decorator.


Plugins are applied on demand, that is, as soon as a route is requested for the first time. For this to work properly in multi-threaded environments, :meth:`Plugin.__call__` and :meth:`Plugin.apply` must be thread-save.

Once all plugins are applied to a route, the prepared callback is cached and subsequent requests call the cached version directly. This means that a plugin is usually applied only once to a specific route. The cache, however, is cleared every time the list of installed plugins changes. Your plugin should be able to decorate the same route more than once.

.. _route-context:

Route Context
=============

The route context dictionary stores meta-information about a specific route. It is passed to :meth:`Plugin.apply` along with the route callback and contains the following values:

===========  ===================================================================
Key          Description
===========  ===================================================================
rule         The rule string (e.g. ``/wiki/:page``) as it is passed to the
             router.
method       An uppercase HTTP method string (e.g. ``GET``).
callback     The original callback with no plugins or wrappers applied. Useful
             for introspection.
name         The name of the route (if specified) or ``None``.
apply        A list of route-specific plugins (see :meth:`Bottle.route`).
skip         A list of plugins to not apply to this route
             (see :meth:`Bottle.route`).
app          The associated application object.
config       Additional keyword arguments passed to the :meth:`Bottle.route`
             decorator are stored in this dictionary. Used for route-specific
             plugin configuration and meta-data.
===========  ===================================================================

.. note::

    While the :meth:`Bottle.route()` decorator accepts multiple rules and methods in a single call, the context dictionary only contains a specific pair. :meth:`Plugin.apply` is called once for each combination of ``rule`` and ``method``, even if they all map to the same route callback.
   
Keep in mind that the `config` dictionary is shared between all plugins. It is always a good idea to add a unique prefix or, if your plugin needs a lot of configuration, store it in a separate dictionary within the `config` dictionary. This helps to avoid naming collisions and incompatibilities between plugins.

Manipulating the Context Dictionary
------------------------------------

While the :ref:`route context dictionary <route-context>` is mutable, changes may have unpredictable effects on other plugins. It is most likely a bad idea to monkey-patch a broken configuration on the fly instead of providing a helpful error message and let the user fix it properly.

In some rare cases, however, it might be justifiable to break this rule. After you made your changes to the context dictionary, raise :exc:`RouteReset` as an exception. This removes the current route from the callback cache and causes all plugins to be re-applied. The router is not updated, however. Changes to `rule` or `method` values have no effect on the router, but only on plugins. This may change in the future, though.

