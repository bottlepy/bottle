Bottle Web Framework
====================

Bottle is a fast and simple mirco-framework for small web-applications. It
offers request dispatching with url parameter support, templates, a buildin HTTP
server and adapters for many third party WSGI/HTTP-server and template engines.
All in a single file and with no dependencies other than the Python Standard
Library.

You can install bottle with `easy_install bottle` or just download bottle.py
and place it in your project directory. There are no (hard) dependencies other
than the Python Standard Library. For news, bugs and new releases
visit my [GitHub repository][www] or the [bottle.py wiki][wiki].

  [www]: http://github.com/defnull/bottle
  [wiki]: http://wiki.github.com/defnull/bottle

Features
--------

  * Request dispatching: Map requests to handler-callables using URL-routes
    * URL parameters: Use regular expressions `/object/(?P<id>[0-9]+)` or simplified syntax `/object/:id` to extract data out of URLs
  * WSGI abstraction: Don't worry about cgi and wsgi internals
    * Input: `request.GET['parameter']` or `request.POST['form-field']`
    * HTTP header: `response.header['Content-Type'] = 'text/html'`
    * Cookie Management: `response.COOKIES['session'] = 'new_key'`
    * Static files: `send_file('movie.flv', '/downloads/')` with automatic mime-type guessing
    * Errors: Throw HTTP errors using `abort(404, 'Not here')` or subclass `HTTPError` and use custom error handlers
  * Templates: Integrated template language
    * Plain simple: Execute python code with `%...` or use the inline syntax `{{...}}` for one-line expressions
    * No IndentationErrors: Blocks are closed by `%end`. Indentation is optional.
    * Extremely fast: Parses and renders templates 5 to 10 times faster than [mako][]
    * Support for [Mako-Templates][mako] (requires [mako][])
  * HTTP Server: Build in WSGI/HTTP Gateway server (for development and production mode)
    * Currently supports wsgiref.simple_server (default), [cherrypy][], [flup][], [paste][] and [fapws3][]
  * Speed optimisations:
    * Sendfile: Support for platform-specific high-performance file-transmission facilities, such as the Unix sendfile()
      * Depends on `wsgi.file_wrapper` provided by your WSGI-Server implementation.
    * Self optimising routes: Frequently used routes are tested first (optional)
    * Fast static routes (single dict lookup)
  
Bottle does **not** include:

  * Models and ORMs: Choose your own (SQLAlchemy, Elixr)
  * HTML-Helper, Session, Identification and Authentication: Do it yourself
  * Scaffolding: No, sorry
  
  [mako]: http://www.makotemplates.org/
  [cherrypy]: http://www.cherrypy.org/
  [flup]: http://trac.saddi.com/flup
  [paste]: http://pythonpaste.org/
  [fapws3]: http://github.com/william-os4y/fapws3

Example
-------

    from bottle import route, run, request, response, send_file, abort, template

    @route('/')
    def hello_world():
        return 'Hello World!'

    @route('/hello/:name')
    def hello_name(name):
        return 'Hello %s!' % name

    @route('/hello', method='POST')
    def hello_post():
        name = request.POST['name']
        return 'Hello %s!' % name

    @route('/static/:filename#.*#')
    def static_file(filename):
        send_file(filename, root='/path/to/static/files/')

    @route('/template/test')
    def template_test():
        return template('template_name', title='Template Test', items=[1,2,3,'fly'])
        
    run(host='localhost', port=8080)

Template example:

    %message = 'Hello world!'
    <html>
      <head>
        <title>{{title.title()}}</title>
      </head>
      <body>
        <h1>{{title.title()}}</h1>
        <p>{{message}}</p>
        <p>Items in list: {{len(items)}}</p>
        <ul>
        %for item in items:
          <li>
          %if isinstance(item, int):
            Zahl: {{item}}
          %else:
            %try:
              Other type: ({{type(item).__name__}}) {{repr(item)}}
            %except:
              Error: Item has no string representation.
            %end try-block (yes, you may add comments here)
          %end
          </li>
        %end
        </ul>
      </body>
    </html>


Benchmark
---------

Using ApacheBench on my AMD 2800+ (2GB) on `/template/test` (`Bottle 0.4.2` and `run(server=PasteServer)`

    marc@nava:/work/bottle$ ab -c10 -n1000 http://localhost:8080/template/test
    This is ApacheBench, Version 2.3 <$Revision: 655654 $>
    ...
    Server Software:        PasteWSGIServer/0.5
    ...
    Concurrency Level:      10
    Time taken for tests:   2.238 seconds
    Complete requests:      1000
    ...
    Requests per second:    446.83 [#/sec] (mean)
    Time per request:       22.380 [ms] (mean)
    Time per request:       2.238 [ms] (mean, across all concurrent requests)


Licence (MIT)
-------------

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

