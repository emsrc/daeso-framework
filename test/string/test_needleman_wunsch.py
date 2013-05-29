from daeso.string.needleman_wunsch import needleman_wunsch, print_scores, print_alignment
import unittest





class TestNeedlemanWunsch(unittest.TestCase):
    
    def sim_score(self, e1, e2):
        if e1 == "S":
            if e2 == "A":
                return 1
            elif e2 == "N":
                return 1
            elif e2 == "D":
                return 0
        elif e1 == "E":
            if e2 == "A":
                return -1
            elif e2 == "N":
                return 0
            elif e2 == "D":
                return 2
        elif e1 == "N":
            if e2 == "A":
                return -2
            elif e2 == "N":
                return 6
            elif e2 == "D":
                return 1
        elif e1 == "D":
            if e2 == "A":
                return -2
            elif e2 == "N":
                return 1
            elif e2 == "D":
                return 6
    
    def gap_cost(self, e):
        # uniform gaps cost
        return -10

    def test_needleman_wunsch_1(self):
        seq1 = "SEND"
        seq2 = "AND"
        scores, alignment = needleman_wunsch(seq1, seq2, self.sim_score, self.gap_cost)
        print_scores(seq1, seq2, scores)
        print_alignment(seq1, seq2, alignment)
        self.assertEqual(alignment, [(0,0), (2,1), (3,2)])
        #self.assertEqual(alignment, [(0,0), (1, None), (2,1), (3,2)])

    def test_needleman_wunsch_2(self):
        seq1 = "SEND"
        seq2 = "N"
        scores, alignment = needleman_wunsch(seq1, seq2, self.sim_score, self.gap_cost)
        print_scores(seq1, seq2, scores)
        print_alignment(seq1, seq2, alignment)
        self.assertEqual(alignment, [(2,0)])
        #self.assertEqual(alignment, [(0,None), (1, None), (2,0), (3,None)])
        
    
if __name__ == '__main__':
    unittest.main()