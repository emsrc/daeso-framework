"""
test ParallelGraphCorpus class
"""

import copy
import pprint
import unittest

from daeso.pgc.corpus import ParallelGraphCorpus
from daeso.pgc.graphpair import GraphPair
from daeso.gb.graphbank import GraphBank
from daeso.exception import DaesoWarning


class Test_ParallelGraphCorpus(unittest.TestCase):
    
    def setUp(self):
        self.pgc1 = ParallelGraphCorpus(inf="data/corpus-1.pgc")
    
        
    def test__init(self):
        """
        init from another corpus
        """
        ParallelGraphCorpus(self.pgc1, self.pgc1.get_relations())
        
    
    def test__add__(self):
        """
        corpus + other
        """
        pgc2 = ParallelGraphCorpus(inf="data/corpus-2.pgc")
        pgc3 = self.pgc1 + pgc2

        self.assertEqual(len(pgc3), len(self.pgc1) + len(pgc2))
        
        
    def test__deepcopy__(self):
        """
        copy.deepcopy(corpus)
        """
        pgc2 = copy.deepcopy(self.pgc1)
        
        self.assertTrue(isinstance(pgc2, ParallelGraphCorpus))
        self.assertFalse(self.pgc1._relations is pgc2._relations)
        self.assertFalse(self.pgc1._meta_data is pgc2._meta_data)
        
        for gp1, gp2 in zip(self.pgc1, pgc2):
            self.assertFalse(gp1 is gp2)
            # however, graphbanks and graphs are still shared
            self.assertTrue(gp1._banks is gp2._banks)
            self.assertTrue(gp1._graphs is gp2._graphs)
            
            
    def test__delitem__(self):
        """
        del corpus[1]
        """
        pg = self.pgc1[0]
        del self.pgc1[0]
        self.assertFalse(pg in self.pgc1)
        
        
    def test__delslice__(self):
        """
        del [:1]
        """
        pg = self.pgc1[0]
        del self.pgc1[:1]
        self.assertFalse(pg in self.pgc1)
        
        del self.pgc1[:]
        self.assertEqual(len(self.pgc1), 0)
        
        
    def test__eq__(self):
        self.assertEqual(self.pgc1, self.pgc1)
        
        pgc2 = self.pgc1[:]
        self.assertEqual(self.pgc1, pgc2)
        
        pgc2 = copy.deepcopy(self.pgc1)
        self.assertEqual(self.pgc1, pgc2)
        
        
    def test__getitem__(self):
        self.assertTrue(isinstance(self.pgc1[0], GraphPair))
        
    
    def test__getslice__(self):
        # or shallow copy
        pgc2 = self.pgc1[1:1:1]
        
        self.assertTrue(isinstance(pgc2, ParallelGraphCorpus))
        self.assertTrue(self.pgc1._relations is pgc2._relations)
        self.assertTrue(self.pgc1._meta_data is pgc2._meta_data)
        
        for gp1, gp2 in zip(self.pgc1, pgc2):
            self.assertTrue(gp1 is gp2)
            
            
    def test__iadd__(self):
        self.pgc1 += self.pgc1
        self.assertEquals(len(self.pgc1), 6)
        
        pgc2 = ParallelGraphCorpus(inf="data/corpus-2.pgc")
        pgc2 += self.pgc1
        self.assertEquals(len(pgc2), 9)
        
        
    def test__repr__(self):
        self.assertTrue(repr(self.pgc1))
        
        
    def test__str__(self):
        self.assertTrue(str(self.pgc1))
        
        
    def test__setitem__(self):
        self.pgc1[0] = self.pgc1[-1]
        self.assertEqual(self.pgc1[0], self.pgc1[-1])
        
        self.assertRaises(TypeError, 
                          ParallelGraphCorpus.__setitem__,
                          self.pgc1,
                          1)
        
        
    def test__setslice__(self):
        pgc2 = ParallelGraphCorpus(inf="data/corpus-2.pgc")
        self.pgc1[-1:] = pgc2[:2]
        self.assertEqual(len(self.pgc1), 4)
        
        self.assertRaises(TypeError,
                          ParallelGraphCorpus.__setslice__,
                          self.pgc1,
                          1,
                          1,
                          ["x"])
        
        
    def test_append(self):
        pgc2 = ParallelGraphCorpus(inf="data/corpus-2.pgc")
        self.pgc1.append(pgc2[2])
        self.assertEqual(len(self.pgc1), 4)
        
        self.assertRaises(TypeError,
                          ParallelGraphCorpus.__setslice__,
                          self.pgc1,
                          1,
                          1,
                          ["x"])
        
        
    def test_clear(self):
        self.pgc1.clear()
        self.assertFalse(self.pgc1)
        self.assertTrue(isinstance(self.pgc1, ParallelGraphCorpus))
        
        
    def test_extend(self):
        pgc2 = ParallelGraphCorpus(inf="data/corpus-2.pgc")
        self.pgc1.extend(iter(pgc2))
        self.assertEqual(len(self.pgc1), 6)
        
        
    def test_purge(self):
        # adding graph pairs with identical graphbanks
        pgc1 = ParallelGraphCorpus(inf="data/corpus-1.pgc")
        pgc1 += pgc1
        graphbanks_before = pgc1._graphbanks()
        self.assertEqual(len(graphbanks_before), 2)
        pgc1.purge()
        graphbanks_after = pgc1._graphbanks()        
        self.assertEqual(graphbanks_before, graphbanks_after)
        
        # adding graph pairs with equal graphbanks
        pgc1 = ParallelGraphCorpus(inf="data/corpus-1.pgc")
        pgc2 = ParallelGraphCorpus(inf="data/corpus-1.pgc")
        pgc1 += pgc2
        graphbanks_before = pgc1._graphbanks()
        self.assertEqual(len(graphbanks_before), 4)
        pgc1.purge()
        graphbanks_after = pgc1._graphbanks()        
        self.assertEqual(len(graphbanks_after), 2)
        
        # adding graph pairs with different graphbanks
        pgc1 = ParallelGraphCorpus(inf="data/corpus-1.pgc")
        pgc2 = ParallelGraphCorpus(inf="data/corpus-2.pgc")
        pgc1 += pgc2
        graphbanks_before = pgc1._graphbanks()
        self.assertEqual(len(graphbanks_before), 4)
        pgc1.purge()
        graphbanks_after = pgc1._graphbanks()        
        self.assertEqual(graphbanks_before, graphbanks_after)
        
        # removing graphpairs and thus dependencies on graphbanks
        del pgc1[:]
        graphbanks = pgc1._graphbanks()
        self.assertEqual(len(graphbanks), 0)
            
        
    def test__graph_banks(self):
        graphbanks = self.pgc1._graphbanks()
        self.assertEqual(len(graphbanks), 2)
        
        for gb in graphbanks:
            self.assertTrue(isinstance(gb, GraphBank)) 
            
            
    def test_annotator(self):
        self.assertFalse(self.pgc1.get_annotator())
        self.pgc1.set_annotator("AA")
        self.assertEqual(self.pgc1.get_annotator(), "AA")
        self.pgc1.set_annotator("BB")
        self.assertEqual(self.pgc1.get_annotator(), "AA + BB")
        self.pgc1.set_annotator("CC", append=False)
        self.assertEqual(self.pgc1.get_annotator(), "CC")
        
        
        


if __name__ == '__main__':
    import sys
    import warnings
    from daeso.exception import DaesoWarning
        
    warnings.simplefilter("ignore",  DaesoWarning)  
    sys.argv.append("-v")
    #Test_ParallelGraphCorpus("test__eq__").run()
    unittest.main()
        