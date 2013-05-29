"""
test Pair class
"""

import unittest

from daeso.pair import Pair


class Test_(unittest.TestCase):

    def setUp(self):
        self.p = Pair("x", "y")
        
    def test__repr__(self):
        print repr(self.p)
        
    def test__iter__(self):
        self.assertTrue(list(iter(self.p)))
        
    def test__eq__(self):
        p2 = Pair("x", "y")
        self.assertEqual(self.p, p2)
        
    def test_set(self):
        self.p.set(3, 4)
        self.assertEqual(self.p.source, 3)
        
    
        
        
        
        
        
if __name__ == '__main__':
    import sys
    sys.argv.append("-v")
    unittest.main()