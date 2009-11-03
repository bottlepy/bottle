#!/usr/bin/env python2.6
# -*- coding: utf-8 -*-
from bottle import route, abort, view
import bottle
import markdown
import os.path
import sys
import re
import codecs

# Static files

@route('/:filename#.+\.(css|js|ico|png|txt|html)#')
def static(filename):
    bottle.send_file(filename, root='./static/')

# Bottle Pages

pagedir = './pages'
cachedir   = './cache'

@route('/')
@route('/page/:name#[a-zA-Z0-9_]{3,65}#')
@view('pagemask')
def page(name='start'):
    orig = os.path.join(pagedir, name+'.md')
    cache = os.path.join(cachedir, name+'.html')
    if not os.path.exists(orig):
        abort(404, 'Page %s not found.' % name)
    if not os.path.exists(cache) \
    or os.path.getmtime(orig) > os.path.getmtime(cache):
        with codecs.open(orig, encoding='utf8') as f:
           html = markdown.markdown(f.read(), ['codehilite(force_linenos=True)','wikilink(base_url=/page/)','toc'])
        with open(cache, 'w') as f:
           f.write(html.encode('utf-8'))
    with open(cache) as f:
        return dict(content=f.read(), pagename=name.title())

# Start server
#bottle.debug(True)
bottle.run(host='0.0.0.0', reloader=True, port=int(sys.argv[1]), server=bottle.PasteServer)
