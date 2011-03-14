.. module:: bottle

=========================
List of available Plugins
=========================

The plugin API is extremely flexible and most plugins are designed to be portable and re-usable across applications. Below is an incomplete list of available plugins, all tested with the latest version of bottle and ready to use.

Have a look at :ref:`plugins` for general questions about plugins (installation, usage). If you plan to develop a new plugin, the :doc:`/plugindev` may help you.


SQLite Plugin
----------------------

* **Author:** Marcel Hellkamp
* **License:** MIT
* **Installation:** Included
* **Documentation:** :doc:`/plugins/sqlite`
* **Description:** Provides an sqlite database connection handle to callbacks that request it.


Werkzeug Plugin
----------------------

* **Author:** Marcel Hellkamp
* **License:** MIT
* **Installation:** ``pip install bottle-werkzeug``
* **Documentation:** :doc:`/plugins/werkzeug`
* **Description:** Integrates the "werkzeug" library (alternative request and response objects, advanced debugging middleware and more).


Profile Plugin
----------------------

* **Author:** Marcel Hellkamp
* **License:** MIT
* **Installation:** ``pip install bottle-profile``
* **Documentation:** :doc:`/plugins/profile`
* **Description:** This plugin collects profiling data and displays it in the browser.

