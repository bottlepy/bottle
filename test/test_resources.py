import bottle
from tools import ServerTestBase
from bottle import Bottle
import os.path

class TestAppMounting(ServerTestBase):
	def test_path_normalize(self):
		tests = ('/foo/bar/', '/foo/bar/baz', '/foo/baz/../bar/blub')
		for test in tests:
			app = bottle.Bottle(resources=test)
			self.assertEqual(app.resource_path, ['/foo/bar/'])

		for test in tests:
			app = bottle.Bottle()
			app.add_resource_path(test)
			self.assertEqual(app.resource_path, ['/foo/bar/'])

	def test_path_absolutize(self):
		tests = ('./foo/bar/', './foo/bar/baz', './foo/baz/../bar/blub')
		abspath = os.path.abspath('./foo/bar/') + os.sep
		for test in tests:
			app = bottle.Bottle(resources=test)
			self.assertEqual(app.resource_path, [abspath])

		for test in tests:
			app = bottle.Bottle()
			app.add_resource_path(test)
			self.assertEqual(app.resource_path, [abspath])

		for test in tests:
			app = bottle.Bottle()
			app.add_resource_path(test[2:])
			self.assertEqual(app.resource_path, [abspath])

	def test_path_unique(self):
		tests = ('/foo/bar/', '/foo/bar/baz', '/foo/baz/../bar/blub')
		app = bottle.Bottle(resources=tests)
		self.assertEqual(app.resource_path, ['/foo/bar/'])

	def test_root_path(self):
		tests = ('/foo/bar/', '/foo/bar/baz', '/foo/baz/../bar/blub')
		for test in tests:
			app = bottle.Bottle()
			app.add_resource_path('./baz/', test)
			self.assertEqual(app.resource_path, ['/foo/bar/baz/'])

		for test in tests:
			app = bottle.Bottle()
			app.add_resource_path('baz/', test)
			self.assertEqual(app.resource_path, ['/foo/bar/baz/'])

	def test_path_order(self):
		app = bottle.Bottle()
		app.add_resource_path('/middle/')
		app.add_resource_path('/first/', prepend=True)
		app.add_resource_path('/last/')
		self.assertEqual(app.resource_path, ['/first/', '/middle/', '/last/'])

	def test_find(self):
		app = bottle.Bottle()
		app.add_resource_path('/first/')
		app.add_resource_path(__file__)
		app.add_resource_path('/last/')
		self.assertEqual(None, app.find_resource('notexist.txt'))
		self.assertEqual(__file__,
					     app.find_resource(os.path.basename(__file__)))


if __name__ == '__main__': #pragma: no cover
	import unittest
    unittest.main()
