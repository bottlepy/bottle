Bottle Web Framework
====================

<div style="float: right; padding: 0px 0px 2em 2em"><img src="http://bottle.paws.de/bottle-logo.png" alt="Bottle Logo" /></div>

Bottle is a fast and simple [WSGI][wsgi]-framework for the
[Python Programming Language][py]. It offers request dispatching with url
parameter support (routes), templates, a built-in HTTP server and adapters for
many third party WSGI/HTTP-server and template engines - all in a single file
and with no dependencies other than the Python Standard Library.

For news, bugs and documentation visit the [bottle.py homepage][home].

  [wsgi]: http://www.wsgi.org/wsgi/
  [home]: http://bottle.paws.de/
  [py]: http://python.org/
  [www]: http://github.com/defnull/bottle
  [bottle-dl]: http://pypi.python.org/pypi/bottle

Installation and Dependencies
-----------------------------

You can install bottle with `pip install bottle` or just [download][bottle-dl] bottle.py and place it in your project directory. There are no (hard) dependencies other than the Python Standard Library.

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

