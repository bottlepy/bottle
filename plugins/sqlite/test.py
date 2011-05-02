import unittest
import os
import bottle
from bottle.ext import sqlite
import sqlite3

class SQLiteTest(unittest.TestCase):
    def setUp(self):
        self.app = bottle.Bottle(catchall=False)

    def test_with_keyword(self):
        self.plugin = self.app.install(sqlite.Plugin())

        @self.app.get('/')
        def test(db):
            self.assertEqual(type(db), type(sqlite3.connect(':memory:')))
        self.app({'PATH_INFO':'/', 'REQUEST_METHOD':'GET'}, lambda x, y: None)

    def test_without_keyword(self):
        self.plugin = self.app.install(sqlite.Plugin())

        @self.app.get('/')
        def test():
            pass
        self.app({'PATH_INFO':'/', 'REQUEST_METHOD':'GET'}, lambda x, y: None)

        @self.app.get('/2')
        def test(**kw):
            self.assertFalse('db' in kw)
        self.app({'PATH_INFO':'/2', 'REQUEST_METHOD':'GET'}, lambda x, y: None)
        
if __name__ == '__main__':
    unittest.main()
