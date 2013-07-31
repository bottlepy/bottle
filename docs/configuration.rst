=====================
Configuration (DRAFT)
=====================

.. currentmodule:: bottle

.. warning::
    This is a draft for a new API. `Tell us <mailto:bottlepy@googlegroups.com>`_ what you think.

Bottle applications can store their configuration in :attr:`Bottle.config`, a dict-like object and central place for application specific settings. This dictionary controls many aspects of the framework, tells (newer) plugins what to do, and can be used to store your own configuration as well.

Configuration Basics
====================

The :attr:`Bottle.config` object behaves a lot like an ordinary dictionary. All the common dict methods work as expected. Let us start with some examples::

    import bottle
    app = bottle.default_app()             # or bottle.Bottle() if you prefer

    app.config['autojson']    = False      # Turns off the "autojson" feature
    app.config['sqlite.db']   = ':memory:' # Tells the sqlite plugin which db to use
    app.config['myapp.param'] = 'value'    # Example for a custom config value.

    # Change many values at once
    app.config.update({
        'autojson': False,
        'sqlite.db': ':memory:',
        'myapp.param': 'value'
    })

    # Add default values
    app.config.setdefault('myapp.param2', 'some default')

    # Receive values
    param  = app.config['myapp.param']
    param2 = app.config.get('myapp.param2', 'fallback value')

    # An example route using configuration values
    @app.route('/about', view='about.rst')
    def about():
        email = app.config.get('my.email', 'nomail@example.com')
        return {'email': email}

The app object is not always available, but as long as you are within a request context, you can use the `request` object to get the current application and its configuration::

    from bottle import request
    def is_admin(user):
        return user == request.app.config['myapp.admin_user']

Naming Convention
=================

To make life easier, plugins and applications should follow some simple rules when it comes to config parameter names:

- All keys should be lowercase strings and follow the rules for python identifiers (no special characters but the underscore).
- Namespaces are separated by dots (e.g. ``namespace.field`` or ``namespace.subnamespace.field``).
- Bottle uses the root namespace for its own configuration. Plugins should store all their variables in their own namespace (e.g. ``sqlite.db`` or ``werkzeug.use_debugger``).
- Your own application should use a separate namespace (e.g. ``myapp.*``).


Loading Configuration from a File
=================================

.. versionadded 0.12

Configuration files are useful if you want to enable non-programmers to configure your application,
or just don't want to hack python module files just to change the database port. A very common syntax for configuration files is shown here:

.. code-block:: ini

    [sqlite]
    db = /tmp/test.db
    commit = auto
 
    [myapp]
    admin_user = defnull

With :meth:`ConfigDict.load_config` you can load these ``*.ini`` style configuration
files from disk and import their values into your existing configuration::

    app.config.load_config('/etc/myapp.conf')

Loading Configuration from a nested :class:`dict`
=================================================

.. versionadded 0.12

Another useful method is :meth:`ConfigDict.load_dict`. This method takes
an entire structure of nested dictionaries and turns it into a flat list of keys and values with namespaced keys::

    # Load an entire dict structure
    app.config.load_dict({
        'autojson': False,
        'sqlite': { 'db': ':memory:' },
        'myapp': {
            'param': 'value',
            'param2': 'value2'
        }
    })
    
    assert app.config['myapp.param'] == 'value'

    # Load configuration from a json file
    with open('/etc/myapp.json') as fp:
        app.config.load_dict(json.load(fp))


Listening to configuration changes
==================================

.. versionadded 0.12

The ``config`` hook on the application object is triggered each time a value in :attr:`Bottle.config` is changed. This hook can be used to react on configuration changes at runtime, for example reconnect to a new database, change the debug settings on a background service or resize worker thread pools. The hook callback receives two arguments (key, new_value) and is called before the value is actually changed in the dictionary. Raising an exception from a hook callback cancels the change and the old value is preserved.

::

  @app.hook('config')
  def on_config_change(key, value):
    if key == 'debug':
        switch_own_debug_mode_to(value)

The hook callbacks cannot *change* the value that is to be stored to the dictionary. That is what filters are for.


.. conf-meta:

Filters and other Meta Data
===========================

.. versionadded 0.12

:class:`ConfigDict` allows you to store meta data along with configuration keys. Two meta fields are currently defined:

help
    A help or description string. May be used by debugging, introspection or
    admin tools to help the site maintainer configuring their application.

filter
    A callable that accepts and returns a single value. If a filter is defined for a key, any new value stored to that key is first passed through the filter callback. The filter can be used to cast the value to a different type, check for invalid values (throw a ValueError) or trigger side effects.

This feature is most useful for plugins. They can validate their config parameters or trigger side effects using filters and document their configuration via ``help`` fields::

    class SomePlugin(object):
        def setup(app):
            app.config.meta_set('some.int', 'filter', int)
            app.config.meta_set('some.list', 'filter',
                lambda val: str(val).split(';'))
            app.config.meta_set('some.list', 'help',
                'A semicolon separated list.')

        def apply(self, callback, route):
            ...

    import bottle
    app = bottle.default_app()
    app.install(SomePlugin())

    app.config['some.list'] = 'a;b;c'     # Actually stores ['a', 'b', 'c']
    app.config['some.int'] = 'not an int' # raises ValueError


API Documentation
=================

.. versionadded 0.12

.. autoclass:: ConfigDict
   :members:
