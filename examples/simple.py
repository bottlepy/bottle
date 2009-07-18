#!/usr/bin/env python
from bottle import route, run, request, response, send_file, abort, validate, template, db
import bottle
bottle.DEBUG=True

@route('/')
def index():
    return template('index')

run(host='localhost', port=8080)
