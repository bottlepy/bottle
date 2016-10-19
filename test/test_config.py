import os
import sys
import tempfile
import unittest

import functools

import itertools

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
        self.assertEquals(d.setdefault('key', "Val2"), m.setdefault('key', "Val2"))
        self.assertEquals(d.setdefault('key', "Val3"), m.setdefault('key', "Val3"))
        self.assertEqual(d.get('key'), m.get('key'))
        with self.assertRaises(KeyError):
            del m['No key']

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

    def test_string_save_keys(self):
        c = ConfigDict()
        with self.assertRaises(TypeError):
            c[5] = 'value'
        with self.assertRaises(TypeError):
            c.load_dict({5: 'value'})

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

    def test_overlay(self):
        source = ConfigDict()
        source['key'] = 'source'
        intermediate = source._make_overlay()
        overlay = intermediate._make_overlay()

        # Overlay contains values from source
        self.assertEqual(overlay['key'], 'source')
        self.assertEqual(overlay.get('key'), 'source')
        self.assertTrue('key' in overlay)

        # Overlay is updated with source
        source['key'] = 'source2'
        self.assertEqual(source['key'], 'source2')
        self.assertEqual(overlay['key'], 'source2')

        # Overlay 'overlays' source (hence the name)
        overlay['key'] = 'overlay'
        self.assertEqual(source['key'], 'source2')
        self.assertEqual(intermediate['key'], 'source2')
        self.assertEqual(overlay['key'], 'overlay')

        # Deleting an overlayed key restores the value from source
        del overlay['key']
        self.assertEqual(source['key'], 'source2')
        self.assertEqual(overlay['key'], 'source2')

        # Deleting a virtual key is actually not possible.
        with self.assertRaises(KeyError):
            del overlay['key']

        # Deleting a key in the source also removes it from overlays.
        del source['key']
        self.assertTrue('key' not in overlay)
        self.assertTrue('key' not in intermediate)
        self.assertTrue('key' not in source)

        # New keys in source are copied to overlay
        source['key2'] = 'source'
        self.assertEqual(source['key2'], 'source')
        self.assertEqual(intermediate['key2'], 'source')
        self.assertEqual(overlay['key2'], 'source')

        # New keys in overlay do not change the source
        overlay['key3'] = 'overlay'
        self.assertEqual(overlay['key3'], 'overlay')
        self.assertTrue('key3' not in intermediate)
        self.assertTrue('key3' not in source)

        # Setting the same key in the source does not affect the overlay
        # because it already has this key.
        source['key3'] = 'source'
        self.assertEqual(source['key3'], 'source')
        self.assertEqual(intermediate['key3'], 'source')
        self.assertEqual(overlay['key3'], 'overlay')

        # But as soon as the overlayed key is deleted, it gets the
        # copy from the source
        del overlay['key3']
        self.assertEqual(source['key3'], 'source')
        self.assertEqual(overlay['key3'], 'source')

    def test_gc_overlays(self):
        root = ConfigDict()
        overlay = root._make_overlay()
        del overlay
        import gc; gc.collect()
        root._make_overlay()  # This triggers the weakref-collect
        self.assertEqual(len(root._overlays), 1)


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
