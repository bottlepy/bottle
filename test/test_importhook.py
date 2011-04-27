# -*- coding: utf-8 -*-
import unittest
import sys
import imp

class TestImportHooks(unittest.TestCase):
    server = 'wsgiref'

    def make_module(self, name, **args):
        mod = sys.modules.setdefault(name, imp.new_module(name))
        mod.__file__ = '<virtual %s>' % name
        mod.__dict__.update(**args)
        return mod

    def test_direkt_import(self):
        mod = self.make_module('bottle_test')
        import bottle.ext.test
        self.assertEqual(bottle.ext.test, mod)

    def test_from_import(self):
        mod = self.make_module('bottle_test')
        from bottle.ext import test
        self.assertEqual(test, mod)

    def test_data_import(self):
        mod = self.make_module('bottle_test', item='value')
        from bottle.ext.test import item
        self.assertEqual(item, 'value')

    def test_import_fail(self):
        ''' Test a simple static page with this server adapter. '''
        def test():
            import bottle.ext.doesnotexist
        self.assertRaises(ImportError, test)

if __name__ == '__main__': #pragma: no cover
    unittest.main()
