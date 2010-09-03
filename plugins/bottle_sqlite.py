# -*- coding: utf-8 -*-
"""
This plugin passes a sqlite3 database handle to callbacks that expect a
`db` parameter. If the callback does not define that parameter, no
connection is made.

Example::

    import bottle

    bottle.install('sqlite', dbfile='/tmp/test.db')

    @bottle.route('/show/:id')
    def show(db, id):
        id = int(id)
        c = db.execute('SELECT content FROM objects WHERE id = ?', (id,))
        row = c.fetchone()
        return bottle.template('show', content=row['content'])

"""

__autor__ = "Marcel Hellkamp"
__version__ = '0.1'
__licence__ = 'MIT'

import sqlite3
import inspect
import bottle

def accepts_keyword(func, name):
    ''' Return True if it is save to pass a named keyword argument to
        func. This works only on decorated functions if they were wrapped by
        bottle.
    '''
    while func:
        args, varargs, varkw, defaults = inspect.getargspec(func)
        if name not in args and not varkw:
            return False
        func = getattr(func, '_bottle_wrapped', None)
    return True


class SQLitePlugin(bottle.BasePlugin):
    plugin_name = 'sqlite'

    def setup(self, app, dbfile=':memory:', keyword='db',
                         commit=True, dictrows=True):
        self.dbfile = app.config.get('plugin.sqlite.dbfile', dbfile)
        self.keyword = app.config.get('plugin.sqlite.keyword', keyword)
        self.commit = app.config.get('plugin.sqlite.commit', commit)
        self.dictrows = app.config.get('plugin.sqlite.dictrows', dictrows)

    def wrap(self, callback):
        # Do not wrap callbacks that do not expect a 'db' keyword argument
        if not accepts_keyword(callback, self.keyword):
            return callback
        def wrapper(*args, **kwargs):
            # Connect to the database
            db = self.get_connection()
            # Add the connection handle to the dict of keyword arguments.
            kwargs[self.keyword] = db
            try:
                rv = callback(*args, **kwargs)
                if self.commit: db.commit() # Auto-commit
            finally:
                # Be sure to close the connection.
                db.close()
            return rv
        return wrapper

    def get_connection(self):
        con = sqlite3.connect(self.dbfile)
        # This allows column access by name: row['column_name']
        if self.dictrows: con.row_factory = sqlite3.Row
        return con

