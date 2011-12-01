# -*- coding: utf-8 -*-

import unittest
from bottle import FormsDict, touni, tob

class TestFormsDict(unittest.TestCase):
    def test_attr_access(self):
        """ FomsDict.attribute returs string values as unicode. """
        data = 'äöü'.encode('utf8')
        d = FormsDict(py2=data, py3=data.decode('latin1'))
        self.assertEqual('äöü', d.py2)
        self.assertEqual('äöü', d.py3)

    def test_attr_missing(self):
        """ FomsDict.attribute returs u'' on missing keys. """
        d = FormsDict()
        self.assertEqual('', d.missing)

    def test_attr_unicode_error(self):
        """ FomsDict.attribute returs u'' on UnicodeError. """
        d = FormsDict(latin='äöü'.encode('latin1'))
        self.assertEqual('', d.latin)
        d.input_encoding = 'latin1'
        self.assertEqual('äöü', d.latin)



   
if __name__ == '__main__': #pragma: no cover
    unittest.main()

