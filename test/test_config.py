import unittest
from bottle import ConfDict

class TestConfDict(unittest.TestCase):
    def test_write(self):
        c = ConfDict()
        c['key'] = 'value'
        self.assertEqual(c['key'], 'value')
        self.assertTrue('key' in c)
        c['key'] = 'value2'
        self.assertEqual(c['key'], 'value2')

    def test_update(self):
        c = ConfDict()
        c['key'] = 'value'
        c.update(key='value2', key2='value3')
        self.assertEqual(c['key'], 'value2')
        self.assertEqual(c['key2'], 'value3')

    def test_namespaces(self):
        c = ConfDict()
        c.update('a.b', key='value')
        self.assertEqual(c['a.b.key'], 'value')
        self.assertEqual(c['a.b.key'], 'value')

    def test_meta(self):
        c = ConfDict()
        c.meta_set('bool', 'filter', bool)
        c.meta_set('int', 'filter', int)
        c['bool'] = 'I am so true!'
        c['int']  = '6'
        self.assertTrue(c['bool'] is True)
        self.assertEquals(c['int'], 6)        
        self.assertRaises(ValueError, lambda: c.update(int='not an int'))
   
if __name__ == '__main__': #pragma: no cover
    unittest.main()

