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
        self._text = ''
        self._html = ''
        self.filename  = os.path.join(self.pagedir,  self.name+'.md')
        self.cachename = os.path.join(self.cachedir, self.name+'.html')

    @property
    def title(self):
        m = re.search(r'^#\s+(.+)$|^(.+)\n=+', self.raw, re.MULTILINE)
        if not m:
            return 'No Title'
        return filter(None, m.groups())[0].strip()

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
    def preview(self):
        out = []
        for line in self.raw.splitlines():
             if len(line) > 32 and not line.startswith('#') \
             and not line.startswith(' '):
                 out.append(line.strip())
             elif buffer:
                 break
        return ' '.join(out)

    def exists(self):
        return os.path.exists(self.filename)

    @classmethod
    def yield_blogposts(cls):
        for post in glob.glob(os.path.join(cls.pagedir, '*.md')):
            name = os.path.basename(post)[:-3]
            if re.match(r'20[0-9]{2}-[0-9]{2}-[0-9]{2}_', name):
                yield Page(name)

    @property
    def blogtime(self):
        try:
            date, name = self.name.split('_', 1)
            year, month, day = map(int, date.split('-'))
            return datetime.date(year, month, day)
        except ValueError:
            raise AttributeError("This page is not a blogpost")

    def has_blogtime(self):
        try:
            self.blogtime
            return True
        except AttributeError:
            return False

# Static files

@route('/:filename#.+\.(css|js|ico|png|txt|html)#')
def static(filename):
    bottle.send_file(filename, root='./static/')

# Bottle Pages

@route('/')
@route('/page/:name')
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
    posts = [post for post in Page.yield_blogposts()]
    posts.sort(key=lambda x: x.blogtime, reverse=True)
    return dict(posts=posts, escape=cgi.escape)


@route('/blog')
@view('blogposts')
def bloglist():
    posts = [post for post in Page.yield_blogposts()]
    posts.sort(key=lambda x: x.blogtime, reverse=True)
    return dict(posts=posts, escape=cgi.escape)


# Start server
#bottle.debug(True)
bottle.run(host='0.0.0.0', reloader=False, port=int(sys.argv[1]), server=bottle.PasteServer)
