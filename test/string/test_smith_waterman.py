from daeso.string.smith_waterman import smith_waterman
from daeso.string.needleman_wunsch import print_scores, print_alignment
import unittest


class TestSmithWatermanExample(unittest.TestCase):
    """
    reproduces the example in Figure1 from the Waterman & Eggert paper
    """
    
    def sim_score(self, e1, e2):
        if e1 == e2:
            return 10
        else:
            return -9
            
    def gap_cost(self, e):
        # uniform gaps cost
        return -20
        
    def test_smith_waterman_example(self):
        seq1 = "CCAATCTACTACTGCTTGCAGTAC"
        seq2 = "AGTCCGAGGGCTACTCTACTGAAC"
        scores, alignment = smith_waterman(seq1, seq2, self.sim_score, self.gap_cost)
        print_scores(seq1, seq2, scores)
        print_alignment(seq1, seq2, alignment)
        self.assertEqual(alignment, [(0, 10), (1, 11), (2, 12), (3, 13), (4,14), 
                                     (5, 15), (6, 16), (7, 17), (8, 18), (9, 19)])
        
        
class TestSmithWaterman2(unittest.TestCase):
    
    def sim_score(self, e1, e2):
        if e1 == e2:
            return 5
        else:
            return 0
            
    def gap_cost(self, e):
        # uniform gaps cost
        return -5
        
    def test_smith_waterman_1(self):
        seq1 = "ABCCBA"
        seq2 = "CBAABC"
        scores, alignment = smith_waterman(seq1, seq2, self.sim_score, self.gap_cost)
        print_scores(seq1, seq2, scores)
        print_alignment(seq1, seq2, alignment)
        self.assertEqual(alignment, [(3, 0), (4, 1), (5, 2)])
        
    def test_smith_waterman_2(self):
        seq1 = "a nice and short sentence to start with".split()
        seq2 = "let's start with a really nice sentence".split()
        scores, alignment = smith_waterman(seq1, seq2, self.sim_score, self.gap_cost)
        print_scores(seq1, seq2, scores)
        print_alignment(seq1, seq2, alignment)
        self.assertEqual(alignment, [(6,1),(7,2)])
        
        
    
    
if __name__ == '__main__':
    unittest.main()