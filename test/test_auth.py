# -*- coding: utf-8 -*-
import unittest
import bottle
from tools import ServerTestBase

class TestBasicAuth(ServerTestBase):

    def test__header(self):
        @bottle.route('/')
        @bottle.auth_basic(lambda x, y: False)
        def test(): return {}
        self.assertStatus(401)
        self.assertHeader('Www-Authenticate', 'Basic realm="private"')
