# -*- coding: utf-8 -*-
''' Tests for the maxage decorator. '''

import unittest
import bottle
from tools import ServerTestBase


class TestMaxAge(ServerTestBase):
    def testCacheable(self):
        # Register a route
        self.app.get('/static')(self.app.maxage(60)(lambda: "foo"))
        result = self.urlopen("/static")
        self.assertEquals(result["header"]["Cache-Control"],
                          "public, max-age=60")
        self.assertEquals(result["header"]["Pragma"], "public")

        self.app.get('/dynamic')(self.app.maxage(0)(lambda: "foo"))
        result = self.urlopen("/dynamic")
        self.assertEquals(result["header"]["Cache-Control"],
                          "no-cache, must-revalidate, max-age=0")
        self.assertEquals(result["header"]["Pragma"],
                          "no-cache, must-revalidate")


if __name__ == '__main__': #pragma: no cover
    unittest.main()
