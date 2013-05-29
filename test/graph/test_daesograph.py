"""
test DaesoGraph and DaesoNode classes
"""

import unittest

from daeso.graph.daesograph import DaesoGraph


class Test_DaesoGraph(unittest.TestCase):

    def setUp(self):
        self.dg = DaesoGraph()
        
    def test_init(self):
        DaesoGraph()
        
    def test_graph_token_string(self):
        s = self.dg.get_graph_token_string()
        self.assertEqual(s, None)
        
        self.dg.set_graph_token_string("w1 w2 w3 ")
        s = self.dg.get_graph_token_string()
        self.assertEqual(s, "w1 w2 w3")
        
        self.assertRaises(TypeError,
                          self.dg.get_graph_token_string,
                          1)
        
    def test_add_node(self):
        self.dg.add_node("1", "noun")
        self.assertEqual(self.dg.node["1"]["label"], "noun")
        
        self.dg.add_node("1", "noun", ("tree",))
        self.assertEqual(self.dg.node["1"]["tokens"], ("tree",))
        
        self.dg.add_node("1", "noun", ("tree",), extra=True)
        self.assertEqual(self.dg.node["1"]["extra"], True)
        
    def test_node_token_string(self):
        s = "a nice tree"
        self.dg.add_node("1", "noun", s.split())
        self.assertEqual(self.dg.get_node_token_string("1"), s)
        
    def test_add_edge(self):
        self.assertRaises(ValueError,
                          self.dg.add_edge,
                          "1", 
                          "2")
        
        self.dg.add_node("1", "NP")
        self.dg.add_node("2", "noun")
        self.dg.add_edge("1", "2", "head", extra=True)
        
        self.assertEqual(self.dg["1"]["2"]["label"], "head")
        self.assertEqual(self.dg["1"]["2"]["extra"], True)
        
        
    def test_add_edges_from(self):
        self.assertRaises(ValueError,
                          self.dg.add_edges_from,
                          [("1", "2")])
        
        self.dg.add_node("1", "S")
        self.dg.add_node("2", "NP")
        self.dg.add_node("3", "noun")
        
        ebunch = [("1", "2"), ("2", "3", dict(label="l2"))]
        
        self.dg.add_edges_from(ebunch, label="l1", extra=True)
        
        self.assertEqual(self.dg["1"]["2"]["label"], "l1")
        self.assertEqual(self.dg["1"]["2"]["extra"], True)
        self.assertEqual(self.dg["2"]["3"]["label"], "l2")
        
        
    def test_node_is_empty(self):
        self.dg.add_node("1", "noun")
        self.assertTrue(self.dg.node_is_empty("1"))
        self.dg.add_node("1", "noun", ["noun"])
        self.assertFalse(self.dg.node_is_empty("1"))
        
        
    def test_node_is_punct(self):
        self.dg.add_node("1", "noun", [","])
        self.assertTrue(self.dg.node_is_punct("1"))
        self.dg.add_node("1", "noun", ["noun"])
        self.assertFalse(self.dg.node_is_punct("1"))
        
        
    def test_terminal_yield(self):
        self.dg.root = "1"
        self.dg.add_node("1", "NP")
        self.dg.add_node("2", "det")
        self.dg.add_node("3", "noun")
        self.dg.add_edge("1", "2", "det")
        self.dg.add_edge("1", "3", "head")
        
        terminals = self.dg.terminal_yield()
        self.assertEqual(terminals, ['2', '3'])
    
        
        
if __name__ == '__main__':
    import sys
    sys.argv.append("-v")
    unittest.main()