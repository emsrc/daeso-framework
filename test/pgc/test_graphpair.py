import unittest
import copy
import xml.etree.cElementTree as et

from daeso.pair import Pair
from daeso.pgc.graphpair import GraphPairBase, GraphMapping, GraphMatching
from daeso.gb.graphbank import GraphBank
from daeso.graph.daesograph import DaesoGraph


class Test_GraphPairBase(unittest.TestCase):
    
    def setUp(self):
        self.banks = Pair(GraphBank("/path1", "alpino"), 
                          GraphBank("/path2", "alpino"))
        self.graphs = Pair(DaesoGraph(id="g1"), 
                           DaesoGraph(id="g2"))
    
    def test_init_1(self):
        GraphPairBase(self.banks, self.graphs)
        
    def test_shallow_copy(self):
        gp1 = GraphPairBase(self.banks, self.graphs, meta_data=[])
        gp2 = copy.copy(gp1)
        
        self.assertTrue(isinstance(gp2, GraphPairBase))
        self.assertTrue(gp1._banks is gp2._banks)
        self.assertTrue(gp1._graphs is gp2._graphs)
        self.assertTrue(gp1._meta_data is gp2._meta_data)
  
        
    def test_deep_copy(self):
        gp1 = GraphPairBase(self.banks, self.graphs, meta_data=[])
        gp2 = copy.deepcopy(gp1)
        
        self.assertTrue(isinstance(gp2, GraphPairBase))
        self.assertTrue(gp1._banks is gp2._banks)
        self.assertTrue(gp1._graphs is gp2._graphs)
        # for this to work, meta_data must not be string, int, etc.
        self.assertFalse(gp1._meta_data is gp2._meta_data)
        
        
    def test__eq__(self):
        gp1 = GraphPairBase(self.banks, self.graphs)
        gp2 = GraphPairBase(self.banks, self.graphs)
        
        self.assertTrue(gp1 == gp2)
        
        # although the graph objects are different, they have the same id,
        # so they count as equal
        equal_graphs = Pair(DaesoGraph(id="g1"), 
                            DaesoGraph(id="g2"))
        gp4 = GraphPairBase(self.banks, equal_graphs)
        
        self.assertTrue(gp1 == gp4)
        
        
    def test_meta_data(self):
        gp = GraphPairBase(self.banks, self.graphs)
        md_elem = gp.get_meta_data()
        et.SubElement(md_elem, "comment")
        
        
        
        
        

class Test_GraphMapping(unittest.TestCase):
    
    def setUp(self):
        self.banks = Pair(GraphBank("/path1", "alpino"), 
                          GraphBank("/path2", "alpino"))
        self.graphs = Pair(DaesoGraph(id="g1"), 
                           DaesoGraph(id="g2"))
        
    
    def test_init_1(self):
        GraphMapping(self.banks, self.graphs)
        
        
    def test_align_2(self):
        gp = GraphMapping(self.banks, self.graphs)
        
        nodes1 = Pair("1", "1")
        nodes2 = Pair("1", "2")
        rel = "equals"
        
        gp.add_align(nodes1, rel)
        gp.add_align(nodes2, rel)
        
        rel2 = gp.get_align(nodes1)
        self.assertEqual(rel2, rel)
        
        gp.del_align(nodes1)
        self.assertFalse(gp.get_align(nodes1))
        self.assertTrue(gp.get_align(nodes2))
        self.assertTrue(gp.has_node("1"))
        self.assertTrue(gp.has_node("2"))
        
        gp.del_align(nodes2)
        self.assertFalse(gp.get_align(nodes2))
        self.assertFalse(gp.has_node("1"))
        self.assertFalse(gp.has_node("2"))
        
        
    def test_shallow_copy(self):
        gp1 = GraphMapping(self.banks, self.graphs, meta_data=[])
        nodes = Pair("n1", "n2")
        gp1.add_align(nodes, "equals")
        
        gp2 = copy.copy(gp1)
        
        self.assertTrue(isinstance(gp2, GraphMapping))
        self.assertTrue(gp1._banks is gp2._banks)
        self.assertTrue(gp1._graphs is gp2._graphs)
        self.assertTrue(gp1._meta_data is gp2._meta_data)
        # also test attibs inherited from DiGraph
        self.assertTrue(gp1.graph is gp2.graph)
        self.assertTrue(gp1.node is gp2.node)
        self.assertTrue(gp1.adj is gp2.adj)
        self.assertTrue(gp1.pred is gp2.pred)
        
        gp2.add_align(nodes, "restates")
        self.assertEqual(gp1.get_align(nodes),
                         gp2.get_align(nodes))
  
        
    def test_deep_copy(self):
        gp1 = GraphMapping(self.banks, self.graphs, meta_data=[])
        nodes = Pair("n1", "n2")
        gp1.add_align(nodes, "equals")        
        
        gp2 = copy.deepcopy(gp1)
        
        self.assertTrue(isinstance(gp2, GraphMapping))
        self.assertTrue(gp1._banks is gp2._banks)
        self.assertTrue(gp1._graphs is gp2._graphs)
        # for this to work, meta_data must not be string, int, etc.
        self.assertFalse(gp1._meta_data is gp2._meta_data)
        # also test attibs inherited from DiGraph
        self.assertFalse(gp1.graph is gp2.graph)
        self.assertFalse(gp1.node is gp2.node)
        self.assertFalse(gp1.adj is gp2.adj)
        self.assertFalse(gp1.pred is gp2.pred)
        
        gp2.add_align(nodes, "restates")
        self.assertNotEqual(gp1.get_align(nodes),
                            gp2.get_align(nodes))
        
        
    def test__eq__(self):
        # TODO: reorganize in 4 different tests
        alignments = [("n1", "n1", dict(relation="r1"))]
        gp1 = GraphMapping(self.banks, self.graphs, 
                           data=alignments)
        gp2 = GraphMapping(self.banks, self.graphs, 
                           data=alignments)
        
        self.assertTrue(gp1 == gp2)
        
        gp3 = GraphMapping(self.banks, self.graphs)
        
        self.assertFalse(gp1 == gp3)
        
        # although the graph objects are different, they have the same id,
        # so they count as equal
        equal_graphs = Pair(DaesoGraph(id="g1"), 
                            DaesoGraph(id="g2"))
        gp4 = GraphMapping(self.banks, equal_graphs,
                           data=alignments)
        
        self.assertTrue(gp1 == gp4)
                

        
class Test_GraphMatching(unittest.TestCase):
    
    def setUp(self):
        self.banks = Pair(GraphBank("/path1", "alpino"), 
                          GraphBank("/path2", "alpino"))
        self.graphs = Pair(DaesoGraph(id="g1"), 
                           DaesoGraph(id="g2"))
        
        
    def test_align(self):
        gp = GraphMatching(self.banks, self.graphs)
        
        nodes1 = Pair("1", "2")
        nodes2 = Pair("2", "3")
        nodes3 = Pair("1", "4")
        rel = "equals"
        
        gp.add_align(nodes1, rel)
        self.assertTrue(gp.get_align(nodes1))
        
        gp.add_align(nodes2, rel)
        self.assertTrue(gp.get_align(nodes1))
        self.assertTrue(gp.get_align(nodes2))
        
        gp.add_align(nodes3, rel)
        self.assertFalse(gp.get_align(nodes1))
        self.assertTrue(gp.get_align(nodes2))
        self.assertTrue(gp.get_align(nodes3))

        gp.del_align(nodes2)
        self.assertFalse(gp.get_align(nodes2))        
        self.assertFalse(gp.has_node("2"))
        self.assertFalse(gp.has_node("3"))
        
        gp.del_align(nodes3)
        self.assertFalse(gp.nodes())
        
        
    def test_align(self):
        # test for previous bug which caused unintended deletion of
        # source/target nodes with the same name
        gp = GraphMatching(self.banks, self.graphs)
        
        nodes1 = Pair("1", "2")
        nodes2 = Pair("2", "1")
        rel = "equals"
        
        gp.add_align(nodes1, rel)
        gp.add_align(nodes2, rel)
        gp.del_align(nodes1)
        self.assertTrue(gp.get_align(nodes2))
        
        
        
if __name__ == '__main__':
    import sys
    sys.argv.append("-v")
    unittest.main()        
        