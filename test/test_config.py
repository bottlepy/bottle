import unittest
from bottle import ConfigDict

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
        # unicode keys (see issue #720)
        try:
            key = unichr(12354)
        except NameError:
            key = chr(12354)
        c = ConfigDict()
        c.load_dict({key: 'value'})
        self.assertEqual('value', c[key])
        c = ConfigDict()
        c.load_dict({key: {'subkey': 'value'}})
        self.assertEqual('value', c[key + '.subkey'])

    @classmethod
    def setUpClass(self):
        # create config file
        from configparser import ConfigParser
        config = ConfigParser()
        # two special section
        config['DEFAULT'] = {'interval': '45'}
        config['bottle'] = {'port': '8080'}
        # ordinary section
        config['compression'] = {'status': 'single'}
        with open('example.ini', 'w') as config_file:
            config.write(config_file)

    @classmethod
    def tearDownClass(self):
        # remove config file
        import os
        os.remove('example.ini')

    def test_load_config(self):
        """`DEFAULT` section should refer to the root namespace."""
        c = ConfigDict()
        c.load_config('example.ini')
        self.assertEqual('45', c['interval'])
        self.assertEqual('8080', c['port'])
        self.assertTrue('compression.interval' not in c)

if __name__ == '__main__': #pragma: no cover
    unittest.main()

