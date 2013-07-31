================================================================================
Request Routing
================================================================================

Bottle uses a powerful routing engine to find the right callback for each request. The :ref:`tutorial <tutorial-routing>` shows you the basics. This document covers advanced techniques and rule mechanics in detail.

Rule Syntax
--------------------------------------------------------------------------------

The :class:`Router` distinguishes between two basic types of routes: **static routes** (e.g. ``/contact``) and **dynamic routes** (e.g. ``/hello/<name>``). A route that contains one or more *wildcards* it is considered dynamic. All other routes are static.

.. versionchanged:: 0.10

The simplest form of a wildcard consists of a name enclosed in angle brackets (e.g. ``<name>``). The name should be unique for a given route and form a valid python identifier (alphanumeric, starting with a letter). This is because wildcards are used as keyword arguments for the request callback later.

Each wildcard matches one or more characters, but stops at the first slash (``/``). This equals a regular expression of ``[^/]+`` and ensures that only one path segment is matched and routes with more than one wildcard stay unambiguous.

The rule ``/<action>/<item>`` matches as follows:

============ =========================================
Path         Result
============ =========================================
/save/123    ``{'action': 'save', 'item': '123'}``
/save/123/   `No Match`
/save/       `No Match`
//123        `No Match`
============ =========================================

You can change the exact behaviour in many ways using filters. This is described in the next section.

Wildcard Filters
--------------------------------------------------------------------------------

.. versionadded:: 0.10

Filters are used to define more specific wildcards, and/or transform the matched part of the URL before it is passed to the callback. A filtered wildcard is declared as ``<name:filter>`` or ``<name:filter:config>``. The syntax for the optional config part depends on the filter used.

The following standard filters are implemented:

* **:int** matches (signed) digits and converts the value to integer.
* **:float** similar to :int but for decimal numbers.
* **:path** matches all characters including the slash character in a non-greedy way and may be used to match more than one path segment.
* **:re[:exp]** allows you to specify a custom regular expression in the config field. The matched value is not modified.

You can add your own filters to the router. All you need is a function that returns three elements: A regular expression string, a callable to convert the URL fragment to a python value, and a callable that does the opposite. The filter function is called with the configuration string as the only parameter and may parse it as needed::

    app = Bottle()

    def list_filter(config):
        ''' Matches a comma separated list of numbers. '''
        delimiter = config or ','
        regexp = r'\d+(%s\d)*' % re.escape(delimiter)

        def to_python(match):
            return map(int, match.split(delimiter))
        
        def to_url(numbers):
            return delimiter.join(map(str, numbers))
        
        return regexp, to_python, to_url

    app.router.add_filter('list', list_filter)

    @app.route('/follow/<ids:list>')
    def follow_users(ids):
        for id in ids:
            ...


Legacy Syntax
--------------------------------------------------------------------------------

.. versionchanged:: 0.10

The new rule syntax was introduce in **Bottle 0.10** to simplify some common use cases, but the old syntax still works and you can find lot code examples still using it. The differences are best described by example:

=================== ====================
Old Syntax          New Syntax
=================== ====================
``:name``           ``<name>``
``:name#regexp#``   ``<name:re:regexp>``
``:#regexp#``       ``<:re:regexp>``
``:##``             ``<:re>``
=================== ====================

Try to avoid the old syntax in future projects if you can. It is not currently deprecated, but will be eventually.



Explicit routing configuration
--------------------------------------------------------------------------------

Route decorator can also be directly called as method. This way provides flexibility in complex setups, allowing you to directly control, when and how routing configuration done.

Here is a basic example of explicit routing configuration for default bottle application::

    def setup_routing():
        bottle.route('/', 'GET', index)
        bottle.route('/edit', ['GET', 'POST'], edit)

In fact, any :class:`Bottle` instance routing can be configured same way::

    def setup_routing(app):
        app.route('/new', ['GET', 'POST'], form_new)
        app.route('/edit', ['GET', 'POST'], form_edit)

    app = Bottle()
    setup_routing(app)

