from daeso.string.waterman_eggert import waterman_eggert, print_all_scores_and_alignments
import unittest


class TestWatermanEggertExample(unittest.TestCase):
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
        
    def test_waterman_eggert_example(self):
        seq1 = "CCAATCTACTACTGCTTGCAGTAC"
        seq2 = "AGTCCGAGGGCTACTCTACTGAAC"
        all_scores, all_alignments = waterman_eggert(seq1, seq2, self.sim_score, self.gap_cost,
                                                     limit=3)
        print_all_scores_and_alignments(seq1, seq2, all_scores, all_alignments)
        result = [[(0, 10), (1, 11), (2, 12), (3, 13), (4, 14), (5, 15), (6, 16), (7, 17), 
                   (8, 18), (9, 19)], 
                   [(5, 10), (6, 11), (7, 12), (8, 13), (9, 14), (11, 15), (12, 16), 
                    (13, 17), (14, 18), (15, 19)], 
                   [(8, 15), (9, 16), (10, 17), (11, 18), (12, 19), (13, 20)] ]
        self.assertEqual(all_alignments, result)
        
        
class TestWatermanEggert2(unittest.TestCase):
    
    def sim_score(self, e1, e2):
        if e1 == e2:
            return 5
        else:
            return 0
            
    def gap_cost(self, e):
        # uniform gaps cost
        return -5
        
    def test_waterman_eggert_1(self):
        seq1 = "ABCCBA"
        seq2 = "CBAABC"
        all_scores, all_alignments = waterman_eggert(seq1, seq2, self.sim_score, self.gap_cost)
        print_all_scores_and_alignments(seq1, seq2, all_scores, all_alignments)
        result = [[(0, 3), (1, 4), (2, 5)], 
                  [(3, 0), (4, 1), (5, 2)], 
                  [(0, 2), (1, 3), (2, 4), (3, 5)], 
                  [(0, 3), (1, 4), (2, 5)], 
                  [(1, 1), (2, 2), (3, 3), (4, 4)], 
                  [(2, 0), (3, 1), (4, 2), (5, 3)], 
                  [(3, 0), (4, 1), (5, 2)], 
                  [(3, 5)], [(5, 3)] ]
        self.assertEqual(all_alignments, result)
        
    def test_waterman_eggert_2(self):
        seq1 = "a nice and short sentence to start with".split()
        seq2 = "let's start with a really nice sentence".split()
        all_scores, all_alignments = waterman_eggert(seq1, seq2, self.sim_score, self.gap_cost)
        print_all_scores_and_alignments(seq1, seq2, all_scores, all_alignments)
        result = [[(6, 1), (7, 2)], 
                  [(0, 3)], 
                  [(1, 4)], 
                  [(1, 5)], 
                  [(2, 6)], 
                  [(4, 6)]]
        self.assertEqual(all_alignments, result)
        
        
    
    
if __name__ == '__main__':
    unittest.main()