# -*- coding: utf-8 -*-

import unittest
from bottle import FormsDict, touni, tob

class TestFormsDict(unittest.TestCase):
    def test_attr_access(self):
        """ FomsDict.attribute returs string values as unicode. """
        data = tob('äöü')
        d = FormsDict(py2=data, py3=data.decode('latin1'))
        self.assertEqual(touni('äöü'), d.py2)
        self.assertEqual(touni('äöü'), d.py3)

    def test_attr_missing(self):
        """ FomsDict.attribute returs u'' on missing keys. """
        d = FormsDict()
        self.assertEqual(touni(''), d.missing)

    def test_attr_unicode_error(self):
        """ FomsDict.attribute returs u'' on UnicodeError. """
        d = FormsDict(latin=touni('äöü').encode('latin1'))
        self.assertEqual(touni(''), d.latin)
        d.input_encoding = 'latin1'
        self.assertEqual(touni('äöü'), d.latin)

    def test_decode_method(self):
        """ FomsDict.attribute returs u'' on UnicodeError. """
        data = tob('äöü')
        d = FormsDict(py2=data, py3=data.decode('latin1'))
        d = d.decode()
        self.assertFalse(d.recode_unicode)
        self.assertEqual(unicode, type(list(d.keys())[0]))
        self.assertEqual(unicode, type(list(d.values())[0]))

if __name__ == '__main__': #pragma: no cover
    unittest.main()

