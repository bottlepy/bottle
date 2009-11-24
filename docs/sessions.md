# Sessions

There is no build in support for sessions because there is no *right*
way to do it. Depending on requirements and environment I'd use [baeker][]
middleware with a fitting backend or implement it myself.

Here is an example for baeker sessions with a file-based backend.


    #!Python
    import bottle
    from beaker.middleware import SessionMiddleware

    app = bottle.default_app()
    session_opts = {
        'session.type': 'file',
        'session.cookie_expires': 300,
        'session.data_dir': './data'
    }
    app = SessionMiddleware(app, session_opts)

    @bottle.route('/test')
    def test():
      s = bottle.request.environ.get('beaker.session')
      s['test'] = s.get('test',0) + 1
      return 'Test counter: %d' % s['test']

    bottle.run(app=app)



[baeker]: http://beaker.groovie.org/
