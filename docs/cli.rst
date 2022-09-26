Command Line Interface
--------------------------------------------------------------------------------

.. versionadded: 0.10

Starting with version 0.10 you can use bottle as a command-line tool:

.. code-block:: console

    $ python -m bottle

    usage: /home/fede/projects/bottle/bottle.py [options] package.module:app

    positional arguments:
      app                   WSGI app entry point.

    optional arguments:
      -h, --help            show this help message and exit
      --version             show version number.
      -b ADDRESS, --bind ADDRESS
                            bind socket to ADDRESS.
      -s SERVER, --server SERVER
                            use SERVER as backend.
      -p PLUGIN, --plugin PLUGIN
                            install additional plugin/s.
      -c FILE, --conf FILE  load config values from FILE.
      -C NAME=VALUE, --param NAME=VALUE
                            override config values.
      --debug               start server in debug mode.
      --reload              auto-reload on file changes.

The `ADDRESS` field takes an IP address or an IP:PORT pair and defaults to ``localhost:8080``. The other parameters should be self-explanatory.

Both plugins and applications are specified via import expressions. These consist of an import path (e.g. ``package.module``) and an expression to be evaluated in the namespace of that module, separated by a colon. See :func:`load` for details. Here are some examples:

.. code-block:: console

    # Grab the 'app' object from the 'myapp.controller' module and
    # start a paste server on port 80 on all interfaces.
    python -m bottle -server paste -bind 0.0.0.0:80 myapp.controller:app

    # Start a self-reloading development server and serve the global
    # default application. The routes are defined in 'test.py'
    python -m bottle --debug --reload test

    # Install a custom debug plugin with some parameters
    python -m bottle --debug --reload --plugin 'utils:DebugPlugin(exc=True)'' test

    # Serve an application that is created with 'myapp.controller.make_app()'
    # on demand.
    python -m bottle 'myapp.controller:make_app()'


