.. module:: bottle

=========================
List of available Plugins
=========================

The plugin API is extremely flexible and most plugins are designed to be portable and re-usable across applications. Below is an incomplete list of available plugins, all tested with the latest version of bottle and ready to use.

Have a look at :ref:`plugins` for general questions about plugins (installation, usage). If you plan to develop a new plugin, the :doc:`/plugindev` may help you.


* :doc:`sqlite`: Adds support for `SQLite` databases.
* :doc:`werkzeug`: Integrates the `werkzeug` library (alternative request and response objects, advanced debugging middleware and more).
* :doc:`profile`: This plugin collects profiling data and displays it in the browser.

.. toctree::
    :glob:
    :hidden:
    
    /plugins/*
