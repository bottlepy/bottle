import unittest
from bottle import ConfigDict

class TestConfigDict(unittest.TestCase):
    def test_isadict(self):
        """ ConfigDict should behaves like a normal dict. """
        # It is a dict-subclass, so this kind of pointless, but it doen't hurt.
        d, m = dict(a=5), ConfigDict(a=5)
        d['key'], m['key'] = 'value', 'value'
        d['k2'], m['k2'] = 'v1', 'v1'
        d['k2'], m['k2'] = 'v2', 'v2'
        self.assertEqual(d.keys(), m.keys())
        self.assertEqual(d.values(), m.values())
        self.assertEqual(list(d.iterkeys()), list(m.iterkeys()))
        self.assertEqual(list(d.itervalues()), list(m.itervalues()))
        self.assertEqual(d.get('key'), m.get('key'))
        self.assertEqual(d.get('cay'), m.get('cay'))
        self.assertEqual(list(iter(d)), list(iter(m)))
        self.assertEqual([k for k in d], [k for k in m])
        self.assertEqual(len(d), len(m))
        self.assertEqual('key' in d, 'key' in m)
        self.assertEqual('cay' in d, 'cay' in m)
        self.assertRaises(KeyError, lambda: m['cay'])
       
    def test_attr_access(self):
        """ ConfigDict allow attribute access to keys. """
        c = ConfigDict()
        c.test = 5
        self.assertEqual(5, c.test)
        self.assertEqual(5, c['test'])
        c['test'] = 6
        self.assertEqual(6, c.test)
        self.assertEqual(6, c['test'])
        del c.test
        self.assertTrue('test' not in c)

    def test_namespaces(self):
        """ Access to a non-existent attribute creates a new namespace. """
        c = ConfigDict()
        self.assertEqual(c.__class__, c.d.e.__class__)
        c.d.e.f = 5
        self.assertEqual(5, c.d.e.f)
        self.assertTrue('f' in c.d.e)
        self.assertTrue('e' in c.d)
        self.assertTrue('d' in c)
        self.assertTrue('f' not in c)
        # Overwriting namespaces is not allowed.
        self.assertRaises(AttributeError, lambda: setattr(c, 'd', 5))
        # Overwriting methods defined on dict is not allowed.
        self.assertRaises(AttributeError, lambda: setattr(c, 'keys', 5))
        # but not with the dict API:
        c['d'] = 5
        self.assertEquals(5, c.d)


   
if __name__ == '__main__': #pragma: no cover
    unittest.main()

