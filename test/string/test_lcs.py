from daeso.string.lcs import longest_common_subsequence, normalized_lcs
import unittest


class TestLCS(unittest.TestCase):
    
    def setUp(self):
        self.s1 = "abcdefghi"
        self.s2 = "xxaxbcxxdefxgxhix"
    
    def test_lcs_string(self):
        lcs = longest_common_subsequence(self.s1, self.s2)
        self.assertEqual(lcs, self.s1)
    
    def test_lcs_tuple(self):
        lcs = longest_common_subsequence(tuple(self.s1), 
                                         tuple(self.s2))
        self.assertEqual(lcs, tuple(self.s1))
    
    def test_lcs_list(self):
        lcs = longest_common_subsequence(list(self.s1), 
                                         list(self.s2))
        self.assertEqual(lcs, list(self.s1))
    
    def test_lcs_identity(self):
        lcs = longest_common_subsequence(self.s1, self.s1)
        self.assertEqual(lcs, self.s1)
    
    def test_lcs_none(self):
        lcs = longest_common_subsequence(self.s1, "")
        self.assertEqual(lcs, "")
    
    def test_lcs_none2(self):
        lcs = longest_common_subsequence("", "")
        self.assertEqual(lcs, "")   
        
    def test_normalized_lcs(self):
        nlcs = normalized_lcs(self.s1, self.s2)
        self.assertAlmostEqual(nlcs, 0.728, 3)

    def test_normalized_lcs_identity(self):
        nlcs = normalized_lcs(self.s1, self.s1)
        self.assertEqual(nlcs, 1.0)
    
    def test_normalized_lcs_none(self):
        nlcs = normalized_lcs(self.s1, "")
        self.assertEqual(nlcs, 0.0)

        
        

if __name__ == '__main__':
    unittest.main()