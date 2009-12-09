Bottle Web Framework
====================

<div style="float: right; padding: 0px 0px 2em 2em"><img src="/bottle-logo.png" alt="Botle Logo" /></div>

Bottle is a fast and simple [WSGI][wsgi]-framework for the [Python Programming Language][py]. It
offers request dispatching with url parameter support ([routes](/page/docs#basic_routes)), [templates](/page/docs#templates), a build-in HTTP server and adapters for many third party
WSGI/HTTP-server and template engines. All in a single file and with no dependencies other than the Python standard library.

  [wsgi]: http://www.wsgi.org/wsgi/
  [py]: http://python.org/
  [bottle-dl]: http://github.com/defnull/bottle/raw/master/bottle.py

### Installation and Dependencies

You can install the latest stable release with `easy_install -U bottle` or just download the newest [bottle.py][bottle-dl] and place it in your project directory. There are no (hard) dependencies other than the Python standard library. Bottle runs with **Python 2.5+ and 3.x** (using 2to3)

<!--

## News

<ul id='newshere'><li><i>Loading...</i></li><li>&nbsp;</li><li>&nbsp;</li><li>&nbsp;</li><li>&nbsp;</li></ul>
<script type="text/javascript">
  $('#newshere').load('http://bottle.paws.de/news.html')
</script>

-->

## Features and Examples

### Small and Lightweight

No installation or configuration required. No dependencies other than 
the Python standard library. Just get a copy of bottle.py and start 
coding! A basic "Hello World" application in Bottle looks like this:

    #!Python
    from bottle import route, run
    
    @route('/')
    def index():
        return 'Hello World!'
    
    run(host='localhost', port=8080)

That's it. Start it up and go to <http://localhost:8080/>.

### Nice looking URLs

Extract data out of dynamic URLs with a simple route syntax.

    #!Python
    @route('/hello/:name')
    def hello(name):
        return 'Hello, %s' % name

Or use full featured regular expressions to do so.

    #!Python
    @route('/friends/(?<name>(Alice|Bob))')
    def friends(name):
        return 'Hello, %s! Good to see you :)' % name

### Static Files, Redirects and HTTP Errors

Use these handy helpers for regular tasks.

    #!Python
    from bottle import send_file, redirect, abort
    
    @route('/static/:filename')
    def static_file(filename):
        send_file(filename, root='/path/to/static/files')

    @route('/wrong/url')
    def wrong():
        redirect("/right/url")

    @route('/restricted')
    def restricted():
        abort(401, "Sorry, access denied.")

### POST, GET, Header and Cookies

As easy as using a `dict()`

    #!Python
    from bottle import request, response
    
    @route('/hello/cookie')
    def cookie():
        name = request.COOKIES.get('name', 'Stranger')
        response.header['Content-Type'] = 'text/plain'
        return 'Hello, %s' % name

    @route('/hello/cookie', method='POST')
    def set_cookie():
        if 'name' in request.POST:
            name = request.POST['name']
            response.COOKIES['name'] = name
        return 'OK'

### Templates

Bottle includes a simple and lightning fast template engine

    #!Python
    @route('/hello/template/:names')
    def pretty_hello(names):
       names = names.split(',')
       return template('hello', title='Hello World', names=names)

And here is the template:

    #!html
    <html>
     <head>
      <title>{{title}}</title>
     </head>
     <body>
      %for name in names:
        <p>Hello, <strong>{{name}}</strong></p>
      %end
     </body>
    </html>

Use [mako][] it you need more features

    #!Python
    from bottle import mako_template as template

### HTTP Server

Bottle has a HTTP Server build in but also supports [cherrypy][], 
[flup][], [paste][] and [fapws3][] as alternatives.

    #!Python
    from bottle import PasteServer
    run(server=PasteServer)


### Non-Features and Known Bugs

Bottle does **not** include (yet):

  * Models and ORMs: Choose your own (SQLAlchemy, Elixir)
  * HTML-Helper, Session, Identification and Authentication: Do it yourself
  * Scaffolding: No, sorry

Some things don't work (yet):

  * Multipart File Uploads do not work with Python 3.x because the cgi.FileStorage is broken.
  
[mako]: http://www.makotemplates.org/
[cherrypy]: http://www.cherrypy.org/
[flup]: http://trac.saddi.com/flup
[paste]: http://pythonpaste.org/
[fapws3]: http://github.com/william-os4y/fapws3





## Voices

[Kaelin](http://bitbucket.org/kaelin), 2009-10-22, [PyPi Comment](http://pypi.python.org/pypi/bottle):

> Bottle rocks! The fastest path I've found between idea and implementation for simple Web applications.

[Seth](http://blog.curiasolutions.com/about/) in his [blog](http://blog.curiasolutions.com/2009/09/the-great-web-development-shootout/) [posts](http://blog.curiasolutions.com/2009/10/the-great-web-technology-shootout-round-3-better-faster-and-shinier/) about common web framework performance:

> As you can see, there was practically no difference in speed between Bottle and pure WSGI in a basic “hello world” test. Even with the addition of Mako and SQLAlchemy, Bottle performed significantly faster than a bare Pylons or Django setup. On a side note, adding a sample template using Bottle’s default templating package didn’t seem to change these numbers at all.

## Projects using Bottle

  * [flugzeit-rechner.de](http://www.flugzeit-rechner.de/) runs on Bottle and Jinja2.
  * [Cuttlefish](http://bitbucket.org/kaelin/cuttlefish/) is a browser-based search tool for quickly `grep`ing source code.
  * [Torque](http://github.com/jreid42/torque) is a multiuser collaborative interface for torrenting.
  * [Message in a Bottle](http://github.com/kennyshen/MIAB) - a simple community messaging app using Bottle and Cassandra.


## Thanks to

In chronological order of their last contribution (DESC).

  * [Damien Degois](http://github.com/babs) for his `If-Modified-Since` support in `send_file()` and his excellent bug reports
  * [Stefan Matthias Aust](http://github.com/sma) for his contribution to `SimpleTemplate` and `Jinja2Template`
  * [DauerBaustelle](http://github.com/dauerbaustelle) for his ideas
  * [smallfish](http://pynotes.appspot.com/) for his chinese translation of the bottle documentation
  * [Johannes Schönberger](http://www.python-forum.de/user-6026.html) for his auto reloading code
  * [clutchski](http://github.com/clutchski) for his `CGIAdapter` and CGI support
  * huanguan1978 for his windows `send_file()` bug report and patch
  * The [German Python Community](http://www.python-forum.de/topic-19451.html) for their support and motivation
  

## Licence (MIT)

   Copyright (c) 2009, Marcel Hellkamp.

   Permission is hereby granted, free of charge, to any person obtaining a copy
   of this software and associated documentation files (the "Software"), to deal
   in the Software without restriction, including without limitation the rights
   to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
   copies of the Software, and to permit persons to whom the Software is
   furnished to do so, subject to the following conditions:

   The above copyright notice and this permission notice shall be included in
   all copies or substantial portions of the Software.

   THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
   IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
   FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
   AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
   LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
   OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
   THE SOFTWARE.

