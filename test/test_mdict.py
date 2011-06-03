import unittest
from bottle import MultiDict, HeaderDict

class TestMultiDict(unittest.TestCase):
    def test_isadict(self):
        """ MultiDict should behaves like a normal dict """
        d, m = dict(a=5), MultiDict(a=5)
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


   
if __name__ == '__main__': #pragma: no cover
    unittest.main()

