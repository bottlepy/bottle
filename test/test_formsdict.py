# -*- coding: utf-8 -*-
# '瓶' means "Bottle"

import unittest
from bottle import FormsDict, touni, tob

class TestFormsDict(unittest.TestCase):
    def test_attr_access(self):
        """ FomsDict.attribute returs string values as unicode. """
        d = FormsDict(py3='瓶')
        self.assertEqual('瓶', d.py3)
        self.assertEqual('瓶', d["py3"])

    def test_attr_missing(self):
        """ FomsDict.attribute returs u'' on missing keys. """
        d = FormsDict()
        self.assertEqual('', d.missing)

    def test_attr_dunder(self):
        """ FormsDict raises AttributeError on missing dunder attributes. """
        d = FormsDict()
        with self.assertRaises(AttributeError):
            _ = d.__nonexistent__
