from daeso.string.rouge import rouge_n, rouge_s, rouge_l, rouge_su
import unittest


class TestRougeN(unittest.TestCase):
    
    def setUp(self):
        self.s1 = tuple("police killed the gunman".split())
        self.s2 = tuple("police kill the gunman".split())
        self.s3 = tuple("the gunman kill police".split())
        self.s4 = tuple("the gunman police killed".split())
        self.s5 = tuple("gunman the killed police".split())
        self.references = [self.s2, self.s3, self.s4, self.s5]
        
    def test_rouge_n_identiy_1(self):
        for n in range(1, len(self.s1) + 1):
            self.assertEqual(rouge_n(self.s1, [self.s1], n), 
                             1.0)
            
    def test_rouge_n_identiy_2(self):
        # if n is so large that no ngram fits,
        # then ROUGE-N is zero.... ! 
        self.assertEqual(rouge_n(self.s1, [self.s1],
                                 len(self.s1) + 1), 
                                 0.0)
        
    def test_rouge_n1(self):
        self.assertAlmostEqual(rouge_n(self.s1, [self.s2], 1), 
                               0.75, 2)
        
    def test_rouge_n2(self):
        self.assertAlmostEqual(rouge_n(self.s1, [self.s2], 2), 
                               0.33, 2)
        
    def test_rouge_n3(self):
        self.assertEqual(rouge_n(self.s1, [self.s2], 3), 
                         0.0)
        
    def test_rouge_n1_all(self):
        self.assertAlmostEqual(rouge_n(self.s1, self.references, 1), 
                         0.25, 2)
        
    def test_rouge_n2_all(self):
        self.assertAlmostEqual(rouge_n(self.s1, self.references, 2), 
                               0.17, 2)
        

class TestRougeL(unittest.TestCase):
    
    def setUp(self):
        self.s1 = tuple("police killed the gunman".split())
        self.s2 = tuple("police kill the gunman".split())
        self.s3 = tuple("the gunman kill police".split())
        self.s4 = tuple("the gunman police killed".split())
        
    def test_rouge_l_1(self):
        self.assertEqual(rouge_l(self.s1, self.s2), 
                         0.75)
        
    def test_rouge_l_2(self):
        self.assertEqual(rouge_l(self.s1, self.s3), 
                         0.5)
        
    def test_rouge_l_3(self):
        self.assertEqual(rouge_l(self.s1, self.s4), 
                         0.5)
        
        
class TestRougeSU(unittest.TestCase):
    
    def setUp(self):
        self.s1 = tuple("police killed the gunman".split())
        self.s2 = tuple("police kill the gunman".split())
        self.s3 = tuple("the gunman kill police".split())
        self.s4 = tuple("the gunman police killed".split())
        self.s5 = tuple("gunman the killed police".split())
        
    def test_rouge_s_1(self):
        self.assertAlmostEqual(rouge_su(self.s1, self.s2), 
                               0.5999, 3)
        
    def test_rouge_s_2(self):
        self.assertAlmostEqual(rouge_su(self.s1, self.s3), 
                               0.400, 3)
        
    def test_rouge_s_3(self):
        self.assertAlmostEqual(rouge_su(self.s1, self.s4), 
                               0.5999, 3)
        

if __name__ == '__main__':
    unittest.main()