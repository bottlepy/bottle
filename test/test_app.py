# -*- coding: utf-8 -*-
""" Tests for the functionality of the application object.

    TODO: Move other tests here.
""" 

import unittest
from bottle import Bottle

class TestApplicationObject(unittest.TestCase):
    
    def test_setattr(self):
        """ Attributed can be assigned, but only once. """
        app = Bottle()
        app.test = 5
        self.assertEquals(5, app.test)
        self.assertRaises(AttributeError, setattr, app, 'test', 6) 
        del app.test
        app.test = 6
        self.assertEquals(6, app.test)
