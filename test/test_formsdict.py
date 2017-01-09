# -*- coding: utf-8 -*-
# '瓶' means "Bottle"

import unittest
from bottle import FormsDict, touni, tob

class TestFormsDict(unittest.TestCase):
    def test_attr_access(self):
        """ FomsDict.attribute returs string values as unicode. """
        d = FormsDict(py2=tob('瓶'), py3=tob('瓶').decode('latin1'))
        self.assertEqual(touni('瓶'), d.py2)
        self.assertEqual(touni('瓶'), d.py3)

    def test_attr_missing(self):
        """ FomsDict.attribute returs u'' on missing keys. """
        d = FormsDict()
        self.assertEqual(touni(''), d.missing)

    def test_attr_unicode_error(self):
        """ FomsDict.attribute returs u'' on UnicodeError. """
        d = FormsDict(latin=touni('öäüß').encode('latin1'))
        self.assertEqual(touni(''), d.latin)
        d.input_encoding = 'latin1'
        self.assertEqual(touni('öäüß'), d.latin)

    def test_decode_method(self):
        d = FormsDict(py2=tob('瓶'), py3=tob('瓶').decode('latin1'))
        d = d.decode()
        self.assertFalse(d.recode_unicode)
        self.assertTrue(hasattr(list(d.keys())[0], 'encode'))
        self.assertTrue(hasattr(list(d.values())[0], 'encode'))
