"""
test ODiGraph class
"""

import unittest

from daeso.graph.ograph import ODiGraph


class Test_(unittest.TestCase):
        
    def test_order(self):
        """
        test if edges are indeed returned in insertion order
        """
        g = ODiGraph()
        
        daughters = range(10)

        for d in daughters:
            g.add_edge("mother", d)
            
        self.assertEqual(g.successors("mother"),
                         daughters)
        
        
        
        
if __name__ == '__main__':
    import sys
    sys.argv.append("-v")
    unittest.main()