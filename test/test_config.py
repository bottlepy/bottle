import os
import sys
import tempfile
import unittest

import functools

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
        c['int'] = '6'
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

    def test_load_module(self):
        c = ConfigDict()
        c.load_module('example_settings', True)
        self.assertEqual(c['A.B.C'], 3)

        c = ConfigDict()
        c.load_module('example_settings', False)
        self.assertEqual(c['A']['B']['C'], 3)

    def test_fallback(self):
        fallback = ConfigDict()
        fallback['key'] = 'fallback'
        primary = ConfigDict()
        primary._set_fallback(fallback)

        # Check copy of existing values from fallback to primary
        self.assertEqual(primary['key'], 'fallback')

        # Check value change in fallback
        fallback['key'] = 'fallback2'
        self.assertEqual(fallback['key'], 'fallback2')
        self.assertEqual(primary['key'], 'fallback2')

        # Check value change in primary
        primary['key'] = 'primary'
        self.assertEqual(fallback['key'], 'fallback2')
        self.assertEqual(primary['key'], 'primary')

        # Check delete of mirrored value in primary
        del primary['key']
        self.assertEqual(fallback['key'], 'fallback2')
        self.assertEqual(primary['key'], 'fallback2')

        # Check delete on mirrored key in fallback
        del fallback['key']
        self.assertTrue('key' not in primary)
        self.assertTrue('key' not in fallback)

        # Check new key in fallback
        fallback['key2'] = 'fallback'
        self.assertEqual(fallback['key2'], 'fallback')
        self.assertEqual(primary['key2'], 'fallback')

        # Check new key in primary
        primary['key3'] = 'primary'
        self.assertEqual(primary['key3'], 'primary')
        self.assertTrue('key3' not in fallback)

        # Check delete of primary-only key
        del primary['key3']
        self.assertTrue('key3' not in primary)
        self.assertTrue('key3' not in fallback)

        # Check delete of fallback value
        del fallback['key2']
        self.assertTrue('key2' not in primary)
        self.assertTrue('key2' not in fallback)


class TestINIConfigLoader(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.config_file = tempfile.NamedTemporaryFile(suffix='.example.ini',
                                                       delete=True)
        self.config_file.write(b'[DEFAULT]\n'
                               b'default: 45\n'
                               b'[bottle]\n'
                               b'port = 8080\n'
                               b'[ROOT]\n'
                               b'namespace.key = test\n'
                               b'[NameSpace.Section]\n'
                               b'sub.namespace.key = test2\n'
                               b'default = otherDefault\n'
                               b'[compression]\n'
                               b'status=single\n')
        self.config_file.flush()

    @classmethod
    def tearDownClass(self):
        self.config_file.close()

    def test_load_config(self):
        c = ConfigDict()
        c.load_config(self.config_file.name)
        self.assertDictEqual({
            'compression.default': '45',
            'compression.status': 'single',
            'default': '45',
            'namespace.key': 'test',
            'namespace.section.default': 'otherDefault',
            'namespace.section.sub.namespace.key': 'test2',
            'port': '8080'}, c)
