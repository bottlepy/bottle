import unittest
from bottle import MultiDict, HeaderDict

class TestMultiDict(unittest.TestCase):
    def test_isadict(self):
        """ MultiDict should behaves like a normal dict """
        d, m = dict(a=5), MultiDict(a=5)
        d['key'], m['key'] = 'value', 'value'
        d['k2'], m['k2'] = 'v1', 'v1'
        d['k2'], m['k2'] = 'v2', 'v2'
        self.assertEqual(list(d.keys()), list(m.keys()))
        self.assertEqual(list(d.values()), list(m.values()))
        self.assertEqual(list(d.keys()), list(m.iterkeys()))
        self.assertEqual(list(d.values()), list(m.itervalues()))
        self.assertEqual(d.get('key'), m.get('key'))
        self.assertEqual(d.get('cay'), m.get('cay'))
        self.assertEqual(list(iter(d)), list(iter(m)))
        self.assertEqual([k for k in d], [k for k in m])
        self.assertEqual(len(d), len(m))
        self.assertEqual('key' in d, 'key' in m)
        self.assertEqual('cay' in d, 'cay' in m)
        self.assertRaises(KeyError, lambda: m['cay'])
       
    def test_views_are_reiterable_and_sized(self):
        """ keys(), values() and items() should return dict-like views that
            support len() and can be iterated more than once (see issue #1113). """
        m = MultiDict(a=1, b=2, c=3)

        for name, view in (('keys', m.keys()),
                           ('values', m.values()),
                           ('items', m.items())):
            # Views must support len(), just like real dict views do.
            self.assertEqual(len(view), 3, "len() failed for %s()" % name)
            # Views must be re-iterable (generators are exhausted after one pass).
            first = list(view)
            second = list(view)
            self.assertEqual(first, second,
                             "%s() view is not re-iterable" % name)
            self.assertEqual(len(first), 3)

        # Views must reflect the newest value for each key, like dict access.
        m['a'] = 10
        self.assertEqual(sorted(m.values()), [2, 3, 10])
        self.assertEqual(dict(m.items()), {'a': 10, 'b': 2, 'c': 3})

    def test_ismulti(self):
        """ MultiDict has some special features """
        m = MultiDict(a=5)
        m['a'] = 6
        self.assertEqual([5, 6], m.getall('a'))
        self.assertEqual([], m.getall('b'))
        self.assertEqual([('a', 5), ('a', 6)], list(m.iterallitems()))
   
    def test_isheader(self):
        """ HeaderDict replaces by default and title()s its keys """
        m = HeaderDict(abc_def=5)
        m['abc_def'] = 6
        self.assertEqual(['6'], m.getall('abc_def'))
        m.append('abc_def', 7)
        self.assertEqual(['6', '7'], m.getall('abc_def'))
        self.assertEqual([('Abc-Def', '6'), ('Abc-Def', '7')], list(m.iterallitems()))
    
    def test_headergetbug(self):
        ''' Assure HeaderDict.get() to be case insensitive '''
        d = HeaderDict()
        d['UPPER'] = 'UPPER'
        d['lower'] = 'lower'
        self.assertEqual(d.get('upper'), 'UPPER')
        self.assertEqual(d.get('LOWER'), 'lower')
