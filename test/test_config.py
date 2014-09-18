import unittest
from bottle import ConfigDict, tob, touni

class TestConfDict(unittest.TestCase):
    
    def test_isadict(self):
        """ ConfigDict should behaves like a normal dict. """
        # It is a dict-subclass, so this kind of pointless, but it doen't hurt.
        d, m = dict(), ConfigDict()
        d['key'], m['key'] = 'value', 'value'
        d['k2'], m['k2'] = 'v1', 'v1'
        d['k2'], m['k2'] = 'v2', 'v2'
        self.assertEqual(d.keys(), m.keys())
        self.assertEqual(list(d.values()), list(m.values()))
        self.assertEqual(d.get('key'), m.get('key'))
        self.assertEqual(d.get('cay'), m.get('cay'))
        self.assertEqual(list(iter(d)), list(iter(m)))
        self.assertEqual([k for k in d], [k for k in m])
        self.assertEqual(len(d), len(m))
        self.assertEqual('key' in d, 'key' in m)
        self.assertEqual('cay' in d, 'cay' in m)
        self.assertRaises(KeyError, lambda: m['cay'])

    def test_write(self):
        c = ConfigDict()
        c['key'] = 'value'
        self.assertEqual(c['key'], 'value')
        self.assertTrue('key' in c)
        c['key'] = 'value2'
        self.assertEqual(c['key'], 'value2')

    def test_save_types(self):
        """ Types that are considered save (immutable) are stored as is
            (but may still be copied). """
        c = ConfigDict()
        for value in (True, False,
                      1, -1024, 0.5,
                      tob('abc'), touni('abc'),
                      (1,2,3), frozenset([3,4,5]),
                      (1,2,3,(4,5),'6', frozenset([3,(4,5),6]))):
            c['key'] = value
            self.assertEquals(c['key'], value)

    def test_immutable_values(self):
        """ Config values must be immutable. For some types (list, set) we do this
            automagically, even for nested structures. For others, we don't. """
        c = ConfigDict()
        c['key'] = [1,2,set([3,4]),5, '6']
        self.assertEquals(c['key'], (1,2,frozenset([3,4]),5, '6'))
        self.assertRaises(TypeError, c.__setitem__, 'key', dict())
        self.assertRaises(TypeError, c.__setitem__, 'key', ['a', {}])
        self.assertRaises(TypeError, c.__setitem__, 'key', ('a', {}))

    def test_update(self):
        c = ConfigDict()
        c['key'] = 'value'
        c.update(key='value2', key2='value3')
        self.assertEqual(c['key'], 'value2')
        self.assertEqual(c['key2'], 'value3')

    def test_namespaces(self):
        c = ConfigDict()
        c.update('a.b', key='value')
        self.assertEqual(c['a.b.key'], 'value')

    def test_meta(self):
        c = ConfigDict()
        c.meta_set('bool', 'filter', bool)
        c.meta_set('int', 'filter', int)
        c['bool'] = 'I am so true!'
        c['int']  = '6'
        self.assertTrue(c['bool'] is True)
        self.assertEqual(c['int'], 6)
        self.assertRaises(ValueError, lambda: c.update(int='not an int'))

    def test_load_dict(self):
        c = ConfigDict()
        d = dict(a=dict(b=dict(foo=5, bar=6), baz=7))
        c.load_dict(d)
        self.assertEqual(c['a.b.foo'], 5)
        self.assertEqual(c['a.b.bar'], 6)
        self.assertEqual(c['a.baz'], 7)
   
if __name__ == '__main__': #pragma: no cover
    unittest.main()

