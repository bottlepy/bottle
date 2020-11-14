# -*- coding: utf-8 -*-
# '瓶' means "Bottle"

import unittest
from bottle import FormsDict, touni, tob

class TestFormsDict(unittest.TestCase):
    def test_attr_access(self):
        """ FomsDict.attribute returs string values as unicode. """
        d = FormsDict(py3=tob('瓶').decode('latin1'))
        self.assertEqual('瓶', d.py3)

    def test_attr_missing(self):
        """ FomsDict.attribute returs u'' on missing keys. """
        d = FormsDict()
        self.assertEqual('', d.missing)

    def test_attr_unicode_error(self):
        """ FomsDict.attribute returs u'' on UnicodeError. """
        d = FormsDict(latin='öäüß'.encode('latin1'))
        self.assertEqual('', d.latin)
        d.input_encoding = 'latin1'
        self.assertEqual('öäüß', d.latin)

    def test_decode_method(self):
        d = FormsDict(py3=tob('瓶').decode('latin1'))
        d = d.decode()
        self.assertFalse(d.recode_unicode)
        self.assertTrue(hasattr(list(d.keys())[0], 'encode'))
        self.assertTrue(hasattr(list(d.values())[0], 'encode'))
