import unittest
from ns001 import reference,verify

class TestReferenceAndVerifier(unittest.TestCase):
    def test_valid(self):
        for kind in ('couette','poiseuille'):
            v=[reference(kind,i/20) for i in range(21)]
            self.assertTrue(verify(kind,v)['accepted'],kind)
    def test_faults(self):
        for kind in ('couette','poiseuille'):
            v=[reference(kind,i/20) for i in range(21)]
            for bad in ([-x for x in v], [x+0.1 for x in v], [x+(0.05 if i==10 else 0) for i,x in enumerate(v)]):
                self.assertFalse(verify(kind,bad)['accepted'])
    def test_invalid(self):
        v=[reference('couette',i/20) for i in range(21)]
        v[8]=float('nan')
        self.assertFalse(verify('couette',v)['accepted'])
        with self.assertRaises(ValueError): reference('poiseuille',0.5,mu=0)
if __name__=='__main__':unittest.main()
