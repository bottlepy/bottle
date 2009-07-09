from bottle import route, run, request, response, send_file, abort, validate, template, db

# Lets start with "Hello World!"
# Point your Browser to 'http://localhost:8080/' and greet the world :D
@route('/')
def hello_world():
    return 'Hello World!'

# Receiving GET parameter (/hello?name=Tim) is as easy as using a dict.
@route('/hello')
def hello_get():
    name = request.GET['name']
    return 'Hello %s!' % name

# This example handles POST requests to '/hello_post'
@route('/hello_post', method='POST')
def hello_post():
    name = request.POST['name']
    return 'Hello %s!' % name

# Cookies :D
@route('/counter')
def counter():
    old = request.COOKIES.get('counter',0)
    new = int(old) + 1
    response.COOKIES['counter'] = new
    return "You viewed this page %d times!" % new

# URL-parameter are a useful tool and generate nice looking URLs
# This handles requests such as '/hello/Tim' or '/hello/Jane'
@route('/hello/:name')
def hello_url(name):
    return 'Hello %s!' % name

# By default, an URL parameter matches everything up to the next slash.
# You can change that behaviour by adding a regular expression between two '#'
# in this example, :num will only match one or more digits.
# Requests to '/number/Tim' won't work (and result in a 404)
@route('/number/:num#[0-9]+#')
def hello_number(num):
    return "Your number is %d" % int(num)

# How to send a static file to the Browser? Just name it.
# Bottle does the content-type guessing and save path checking for you.
@route('/static/:filename#.*#')
def static_file(filename):
    send_file(filename, root='/path/to/static/files/')

# You can manually add header and set the content-type of the response.
@route('/json')
def json():
    response.header['Cache-Control'] = 'no-cache, must-revalidate'
    response.content_type = 'application/json'
    return "{counter:%d}" % int(request.COOKIES.get('counter',0))

# Throwing an error using abort()
@route('/private')
def private():
    if request.GET.get('password','') != 'secret':
        abort(401, 'Go away!')
    return "Welcome!"

# Validating URL Parameter
@route('/validate/:i/:f/:csv')
@validate(i=int, f=float, csv=lambda x: map(int, x.strip().split(',')))
def validate_test(i, f, csv):
    return "Int: %d, Float:%f, List:%s" % (i, f, repr(csv))

# Templates
@route('/template/test')
def template_test():
    return template('example', title='Template Test', items=[1,2,3,'fly'])
        
# Database
@route('/db/counter')
def template_test():
    if 'hits' not in db.counter:
        db.counter.hits = 0
        print 'fresh', db.counter.keys()
    db['counter']['hits'] +=  1
    return "Total hits in this page: %d!" % db.counter.hits

import bottle
bottle.DEBUG = True
run(server=bottle.PasteServer, host='localhost', port=8080) 
