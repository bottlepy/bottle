=====================
Configuration (DRAFT)
=====================

.. currentmodule:: bottle

.. warning::
    This is a draft for a new API. `Tell us <mailto:bottlepy@googlegroups.com>`_ what you think.

Bottle applications can store their configuration in :attr:`Bottle.conf`, a dict-like object and central place for application specific settings. This dictionary controls many aspects of the framework, tells (newer) plugins what to do, and can be used to store your own configuration as well.

Configuration Basics
====================

The :attr:`Bottle.conf` object behaves a lot like an ordinary dictionary. All the common dict methods work as expected. Let us start with some examples::

    import bottle
    app = bottle.default_app()           # or bottle.Bottle() if you prefer

    app.conf['autojson']    = False      # Turns off the "autojson" feature
    app.conf['sqlite.db']   = ':memory:' # Tells the sqlite plugin which db to use
    app.conf['myapp.param'] = 'value'    # Example for a custom config value.

    # Change many values at once
    app.conf.update({
        'autojson': False,
        'sqlite.db': ':memory:',
        'myapp.param': 'value'
    })

    # Add default values
    app.conf.setdefault('myapp.param2', 'some default')

    # Receive values
    param  = app.conf['myapp.param']
    param2 = app.conf.get('myapp.param2', 'fallback value')

    # An example route using configuration values
    @app.route('/about', view='about.rst')
    def about():
        email = app.conf.get('my.email', 'nomail@example.com')
        return {'email': email}

The app object is not always available, but as long as you are within a request context, you can use the `request` object to get the current application and its configuration::

    from bottle import request
    def is_admin(user):
        return user == request.app.conf['myapp.admin_user']

Naming Convention
=================

To make life easier, plugins and applications should follow some simple rules when it comes to config parameter names:

- All keys should be lowercase strings and follow the rules for python identifiers (no special characters but the underscore).
- Namespaces are separated by dots (e.g. ``namespace.field`` or ``namespace.subnamespace.field``.
- Bottle uses the root namespace for its own configuration. Plugins should store all their variables in their own namespace (e.g. ``sqlite.db`` or ``werkzeug.use_debugger``).
- Your own application should use a separate namespace (e.g. ``myapp.*``).


Loading Configuration from a File
==================================

There is currently no built-in way to read configuration from a file, but it is quite easy to build your own configuration loader. Python provides a parser for the ``*.ini`` file format in its standard library. The config file looks like this:

.. code-block:: ini

    [sqlite]
    db = /tmp/test.db
    commit = auto

    [myapp]
    admin_user = defnull

And the code to read such a file can be seen here::

    from configparser import SaveConfigParser
    def load_config(app, inifile):
        ini = SaveConfigParser()
        ini.read(inifile)
        for section in ini.sections():
            app.conf.update(section, ini.items(section))

This example uses a little trick: If the first parameter of the :meth:`ConfDict.update` method is a string, all keys are stored in that namespace.

Listening to configuration changes
==================================

.. versionadded 0.12

The ``config`` hook on the application object is triggered each time a value in :attr:`Bottle.conf` is changed. This hook can be used to react on configuration changes at runtime, for example reconnect to a new database, change the debug settings on a background service or resize worker thread pools. The hook callback receives two arguments (key, new_value) and is called before the value is actually changed in the dictionary. Raising an exception from a hook callback cancels the change and the old value is preserved.

::

  @app.hook('config')
  def on_config_change(key, value):
    if key == 'debug':
        switch_own_debug_mode_to(value)

The hook callbacks cannot *change* the value that is to be stored to the dictionary. That is what filters are for.

.. conf-meta:

Filters and other Meta Data
===========================

:class:`ConfDict` allows you to store meta data along with configuration keys. Two meta fields are currently defined:

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

    app.conf['some.list'] = 'a;b;c'     # Actually stores ['a', 'b', 'c']
    app.conf['some.int'] = 'not an int' # raises ValueError


API Documentation
=================

.. autoclass:: ConfDict
   :members:
