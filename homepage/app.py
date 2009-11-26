#!/usr/bin/env python2.6
# -*- coding: utf-8 -*-
from bottle import route, abort, view, response
import bottle
import markdown
import os.path
import sys
import re
import codecs
import glob
import datetime
import cgi

class Page(object):
    pagedir  = '../docs'
    cachedir = './cache'

    def __init__(self, name):
        self.name = name
        self.title = name.replace('_',' ').title()
        self._text = ''
        self._html = ''
        self.filename  = os.path.join(self.pagedir,  self.name+'.md')
        self.cachename = os.path.join(self.cachedir, self.name+'.html')

    @property
    def rawfile(self):
        return codecs.open(self.filename, encoding='utf8')

    @property
    def raw(self):
        return self.rawfile.read()

    @property
    def cachefile(self):
        if not os.path.exists(self.cachename) \
        or os.path.getmtime(self.filename) > os.path.getmtime(self.cachename):
           with self.rawfile as f:
               html = markdown.markdown(f.read(), ['codehilite(force_linenos=True)','wikilink(base_url=/page/)','toc'])
           with open(self.cachename, 'w') as f:
               f.write(html.encode('utf-8'))
        return codecs.open(self.cachename, encoding='utf8')

    @property
    def html(self):
        return self.cachefile.read()

    @property
    def mtime(self):
        return datetime.datetime.utcfromtimestamp(os.path.getmtime(self.filename))

    @property
    def ctime(self):
        return datetime.datetime.utcfromtimestamp(os.path.getctime(self.filename))

    @property
    def preview(self):
        buffer = []
        for line in self.raw.splitlines():
             if len(line) > 32 and not line.startswith('#') \
             and not line.startswith(' '):
                 buffer.append(line.strip())
             elif buffer:
                 break
        return ' '.join(buffer)

    def exists(self):
        return os.path.exists(self.filename)



# Static files

@route('/:filename#.+\.(css|js|ico|png|txt|html)#')
def static(filename):
    bottle.send_file(filename, root='./static/')

# Bottle Pages

@route('/')
@route('/page/:name#[a-zA-Z0-9_]{3,128}#')
@view('pagemask')
def page(name='start'):
    p = Page(name)
    if p.exists():
        return dict(page=p)
    else:
        abort(404, 'Page not found')


@route('/rss.xml')
@view('rss')
def blogrss():
    response.content_type = 'xml/rss'
    posts = []
    for post in glob.glob(os.path.join(Page.pagedir, 'blog_*.md')):
        name = os.path.basename(post).split('.',1)[0]
        posts.append(Page(name))
    posts.sort(key=lambda x: x.mtime, reverse=True)
    return dict(posts=posts, escape=cgi.escape)


@route('/blog')
@view('blogposts')
def bloglist():
    posts = []
    for post in glob.glob(os.path.join(Page.pagedir, 'blog_*.md')):
        name = os.path.basename(post).split('.',1)[0]
        posts.append(Page(name))
    posts.sort(key=lambda x: x.mtime, reverse=True)
    return dict(posts=posts, escape=cgi.escape)


# Start server
#bottle.debug(True)
bottle.run(host='0.0.0.0', reloader=False, port=int(sys.argv[1]), server=bottle.PasteServer)
