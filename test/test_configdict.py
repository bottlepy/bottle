import unittest
from bottle import ConfigDict

def setitem(d, key, value):
    d[key] = value

class TestConfigDict(unittest.TestCase):

    def test_isadict(self):
        """ ConfigDict should behaves like a normal dict. """
        # It is a dict-subclass, so this kind of pointless, but it doen't hurt.
        d, m = dict(a=5), ConfigDict(a=5)
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
        self.assertEqual(None, c.test)

    def test_namespaces(self):
        """ Access to a non-existent uppercase attribute creates a new namespace. """
        c = ConfigDict()
        self.assertEqual(ConfigDict.Namespace, c.Name.Space.__class__)
        c.Name.Space.value = 5
        self.assertEqual(5, c.Name.Space.value)
        self.assertTrue('value' in c.Name.Space)
        self.assertTrue('Space' in c.Name)
        self.assertTrue('Name' in c)
        self.assertTrue('value' not in c)
        # Overwriting namespaces is not allowed.
        self.assertRaises(AttributeError, lambda: setattr(c, 'Name', 5))
        # Overwriting methods defined on dict is not allowed.
        self.assertRaises(AttributeError, lambda: setattr(c, 'keys', 5))
        # but not with the dict API:
        c['Name'] = 5
        self.assertEqual(5, c.Name)

    def test_call(self):
        """ Calling updates and returns the dict. """
        c = ConfigDict()
        self.assertEqual(c, c(a=1))
        self.assertTrue('a' in c)
        self.assertEqual(1, c.a)

    def test_issue588(self):
        """`ConfigDict` namespaces break route options"""
        c = ConfigDict()
        c.load_dict({'a': {'b': 'c'}}, make_namespaces=True)
        self.assertEqual('c', c['a.b'])
        self.assertEqual('c', c['a']['b'])
        self.assertEqual({'b': 'c'}, c['a'])

    def test_string_key_only(self):
        c = ConfigDict()
        self.assertRaises(TypeError, lambda: setitem(c, 5, 6))
        self.assertRaises(TypeError, lambda: c.load_dict({5:6}))


if __name__ == '__main__': #pragma: no cover
    unittest.main()

