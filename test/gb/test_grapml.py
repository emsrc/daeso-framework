"""
test GraphmlParser class
"""

import sys
import unittest

from daeso.gb.graphml import GraphmlParser


class Test_GraphmlParser(unittest.TestCase):

    def setUp(self):
        pass
        
    def test_parser(self):
        parser = GraphmlParser()
        id2graph = {}
        parser.parse_file("data/gml-graphbank-sample.xml", id2graph)
        
        print
        for id, graph in id2graph.items():
            print id + ":", graph.get_graph_token_string().encode("utf-8")
        
        
        
if __name__ == '__main__':
    import sys
    sys.argv.append("-v")
    unittest.main()