import unittest
import gc

from daeso.pair import Pair
from daeso.gb.graphbank import GraphBank, SparseGraphBank
from daeso.gb.graphstub import GraphStub
from daeso.pgc.graphpair import GraphPair
from daeso_nl.graph.alpinograph import AlpinoGraph


class TestGraphBank(unittest.TestCase):
    
    def setUp(self):
        pass
        
    
    def test_init_1(self):
        gb = GraphBank("data/source-gb-1.xml", "alpino")
        gb.load()
        self.assertEqual(len(gb), 3)
        
        
    def test_equal(self):
        gb1 = GraphBank("data/source-gb-1.xml", "alpino")
        gb1.load()
        
        gb2 = GraphBank("data/source-gb-1.xml", "alpino")
        gb2.load()
        self.assertTrue(gb1 == gb2)
        
        gb2 = GraphBank("../../test/gb/data/source-gb-1.xml", "alpino")
        gb2.load()
        self.assertTrue(gb1 == gb2)
        
        gb2 = GraphBank("data/target-gb-1.xml", "alpino")
        gb2.load()
        self.assertFalse(gb1 == gb2)
        
        
    def test__iter__(self):
        gb = GraphBank("data/source-gb-1.xml", "alpino")
        gb.load()
        graphs = [graph for graph in gb]
        self.assertEqual(len(graphs), 3)
        
        
        
class TestSparseGraphBank(unittest.TestCase):
    
    def test_1(self):
        gb = SparseGraphBank("data/source-gb-1.xml", "alpino")

        # create a strong reference to the graph stub object,
        # otherwise it will vanish immediately :-)
        graph_stub1 = gb.get_graph_stub("s100")
        graph_stub2 = gb.get_graph_stub("s200")
        
        graph_pair = GraphPair(Pair(gb, gb), 
                               Pair(graph_stub1, graph_stub2))
        # add a backlink to graph_pair
        graph_stub1.add_client(graph_pair)
        graph_stub2.add_client(graph_pair)
        
        self.assertTrue(isinstance(gb.get_graph("s100"), GraphStub))
        self.assertTrue(isinstance(gb.get_graph("s200"), GraphStub))
        
        gb.load()
        
        self.assertEqual(len(gb), 2)
        self.assertTrue(isinstance(graph_pair._graphs.source, AlpinoGraph))
        self.assertTrue(isinstance(graph_pair._graphs.target, AlpinoGraph))
        self.assertTrue(isinstance(gb.get_graph("s100"), AlpinoGraph))
        self.assertTrue(isinstance(gb.get_graph("s200"), AlpinoGraph))
        
        del graph_pair
        # force garbage collection
        gc.collect()
        
        # make sure the graphs are gone now that the referring graph pair is
        # no longer alive
        self.assertEqual(len(gb), 0)
        self.assertRaises(KeyError,  gb.get_graph, "s100")
        self.assertRaises(KeyError,  gb.get_graph, "s200")
        


graphbank_suite = unittest.TestSuite(
    [ unittest.TestLoader().loadTestsFromTestCase(test_case)
      for test_case in (TestGraphBank, TestSparseGraphBank) ])


if __name__ == '__main__':
    import sys
    sys.argv.append("-v")
    unittest.main()        
