[TOC]

Frequently Asked Questions
==========================


## How to Ignore Tailing Slashes?

Bottle does not ignore tailing slashes by default. 
To handle URLs like `/example` and `/example/` the same, 
you could add two `@route` decorators (fast when using static routes)

    #!Python
    @route('/test')
    @route('/test/')
    def test(): pass

or use dynamic routes

    #!Python
    @route('/test/?')
    def test(): pass

or add a WSGI middleware that strips tailing '/' from URLs

    #!Python
    class StripPathMiddleware(object):
      def __init__(self, app):
        self.app = app
      def __call__(self, e, h):
        e['PATH_INFO'] = e['PATH_INFO'].rstrip('/')
        return self.app(e,h)
    
    app = bottle.default_app()
    app = StripPathMiddleware(app)
    bottle.run(app=app)





## Apache/mod_python and Template Not Found?

Templates are searched in "./" or "./views/" but Apaches mod_python 
changes your working directory. You can use

    bottle.TEMPLATE_PATH.insert(0,'/absolut/path/to/templates/%s.tpl')

to add an absolute search path.
