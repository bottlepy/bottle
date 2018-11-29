# -*- coding: utf-8 -*-
# '瓶' means "Bottle"

import unittest
from bottle import UnicodeFormsDict, FormsDict, touni, tob

class TestUnicodeFormsDict(unittest.TestCase):
    def test_attr_access(self):
        """ UnicodeFormsDict.attribute returns string values as unicode. """
        d = UnicodeFormsDict(py2=tob('瓶'), py3=tob('瓶').decode('latin1'))
        self.assertEqual(touni('瓶'), d.py2)
        self.assertEqual(touni('瓶'), d.py3)

    def test_attr_missing(self):
        """ UnicodeFormsDict.attribute returns u'' on missing keys. """
        d = UnicodeFormsDict()
        self.assertEqual(touni(''), d.missing)

    def test_attr_unicode_error(self):
        """ UnicodeFormsDict.attribute returns u'' on UnicodeError. """
        d = UnicodeFormsDict(latin=touni('öäüß').encode('latin1'))
        self.assertEqual(touni(''), d.latin)
        d.input_encoding = 'latin1'
        self.assertEqual(touni('öäüß'), d.latin)

    def test_dict_access(self):
        """ UnicodeFormsDict[direct_access] returns string values as unicode. """
        d = UnicodeFormsDict(py2=tob('瓶'), py3=tob('瓶').decode('latin1'))
        self.assertEqual(touni('瓶'), d['py2'])
        self.assertEqual(touni('瓶'), d['py3'])
    
    def test_get_access(self):
        """ UnicodeFormsDict returns value strings as unicode in all relevent methods. """
        d = UnicodeFormsDict(py2=tob('瓶'), py3=tob('瓶').decode('latin1'))
        self.assertTrue(hasattr(d.get('py2'), 'encode'))
        self.assertTrue(hasattr(d.getunicode('py2'), 'encode'))
        self.assertTrue(hasattr(list(d.values())[0], 'encode'))
        self.assertTrue(hasattr(list(d.items())[0][1], 'encode'))
        self.assertTrue(hasattr(list(d.allitems())[0][1], 'encode'))
    
    def test_raw_access(self):
        """ UnicodeFormsDict returns raw strings in relevent methods with proper kwargs. """
        d = UnicodeFormsDict(py2=tob('瓶'), py3=tob('瓶').decode('latin1'))
        self.assertEqual(d.get('py2', raw=True), tob('瓶'))
        self.assertEqual(d.get('py3', raw=True), tob('瓶').decode('latin1'))
        self.assertEqual(d.get('py2'), touni('瓶'))
        self.assertEqual(d.get('py3'), touni('瓶'))
        self.assertEqual(d.getall('py2', raw=True), [tob('瓶')])
        self.assertEqual(d.getall('py3', raw=True), [tob('瓶').decode('latin1')])
        self.assertEqual(d.getall('py2'), [touni('瓶')])
        self.assertEqual(d.getall('py3'), [touni('瓶')])

    def test_decode_method(self):
        d = UnicodeFormsDict(py2=tob('瓶'), py3=tob('瓶').decode('latin1'))
        d = d.decode()
        self.assertTrue(isinstance(d, FormsDict))
        self.assertFalse(d.recode_unicode)
        self.assertTrue(hasattr(list(d.keys())[0], 'encode'))
        self.assertTrue(hasattr(list(d.values())[0], 'encode'))
