from daeso.string.similar import cosine, generalized_cosine
from daeso.string.similar import dice, generalized_dice
from daeso.string.similar import jaccard, generalized_jaccard
from daeso.string.similar import overlap, overlap_max
import unittest


class TestCosine(unittest.TestCase):
    
    def test_cosine_empty_1(self):
        self.assertEqual(cosine("",""), 0.0)
        
    def test_cosine_empty_2(self):
        self.assertEqual(cosine("a",""), 0.0)
    
    def test_cosine_empty_3(self):
        self.assertEqual(cosine("","a"), 0.0)
        
    def test_cosine_identity(self):
        self.assertEqual(cosine("a","a"), 1.0)
        
    def test_cosine_symmetry(self):
        self.assertEqual(cosine("ab","bc"), cosine("bc","ab"))
        
    def test_cosine_1(self):
        self.assertAlmostEqual(cosine("levenshtein","leuwenhstijn"), 0.609, 3)
    

class TestGeneralizedCosine(unittest.TestCase):
    
    def test_generalized_cosine_empty_1(self):
        self.assertEqual(generalized_cosine(["","","",""]), 0.0)
        
    def test_generalized_cosine_empty_2(self):
        self.assertEqual(generalized_cosine(["a","","",""]), 0.0)
    
    def test_generalized_cosine_empty_3(self):
        self.assertEqual(generalized_cosine(["","","","a"]), 0.0)
        
    def test_generalized_cosine_identity(self):
        self.assertEqual(generalized_cosine(["a","a","a","a"]), 1.0)
        
    def test_generalized_cosine_symmetry(self):
        self.assertEqual(generalized_cosine(["ab","bc","bd"]), generalized_cosine(["bd", "bc","ab"]))
        
    def test_generalized_cosine_1(self):
        self.assertAlmostEqual(generalized_cosine(["levenshtein","leuwenhstijn","leuvenstein"]), 0.157, 3)
        
        

class TestDice(unittest.TestCase):
    
    def test_dice_empty_1(self):
        self.assertEqual(dice("",""), 0.0)
        
    def test_dice_empty_2(self):
        self.assertEqual(dice("a",""), 0.0)
    
    def test_dice_empty_3(self):
        self.assertEqual(dice("","a"), 0.0)
        
    def test_dice_identity(self):
        self.assertEqual(dice("a","a"), 1.0)
        
    def test_dice_symmetry(self):
        self.assertEqual(dice("ab","bc"), dice("bc","ab"))
        
    def test_dice_1(self):
        self.assertAlmostEqual(dice("levenshtein","leuwenhstijn"), 0.609, 3)
    

class TestGeneralizedDice(unittest.TestCase):
    
    def test_generalized_dice_empty_1(self):
        self.assertEqual(generalized_dice(["","","",""]), 0.0)
        
    def test_generalized_dice_empty_2(self):
        self.assertEqual(generalized_dice(["a","","",""]), 0.0)
    
    def test_generalized_dice_empty_3(self):
        self.assertEqual(generalized_dice(["","","","a"]), 0.0)
        
    def test_generalized_dice_identity(self):
        self.assertEqual(generalized_dice(["a","a","a","a"]), 1.0)
        
    def test_generalized_dice_symmetry(self):
        self.assertEqual(generalized_dice(["ab","bc","bd"]), generalized_dice(["bd", "bc","ab"]))
        
    def test_generalized_dice_1(self):
        self.assertAlmostEqual(generalized_dice(["levenshtein","leuwenhstijn","leuvenstein"]), 0.529, 3)
        

class TestJaccard(unittest.TestCase):
    
    def test_jaccard_empty_1(self):
        self.assertEqual(jaccard("",""), 0.0)
        
    def test_jaccard_empty_2(self):
        self.assertEqual(jaccard("a",""), 0.0)
    
    def test_jaccard_empty_3(self):
        self.assertEqual(jaccard("","a"), 0.0)
        
    def test_jaccard_identity(self):
        self.assertEqual(jaccard("a","a"), 1.0)
        
    def test_jaccard_symmetry(self):
        self.assertEqual(jaccard("ab","bc"), jaccard("bc","ab"))
        
    def test_jaccard_1(self):
        self.assertAlmostEqual(jaccard("levenshtein","leuwenhstijn"), 0.636, 3)
    

class TestGeneralizedJaccard(unittest.TestCase):
    
    def test_generalized_jaccard_empty_1(self):
        self.assertEqual(generalized_jaccard(["","","",""]), 0.0)
        
    def test_generalized_jaccard_empty_2(self):
        self.assertEqual(generalized_jaccard(["a","","",""]), 0.0)
    
    def test_generalized_jaccard_empty_3(self):
        self.assertEqual(generalized_jaccard(["","","","a"]), 0.0)
        
    def test_generalized_jaccard_identity(self):
        self.assertEqual(generalized_jaccard(["a","a","a","a"]), 1.0)
        
    def test_generalized_jaccard_symmetry(self):
        self.assertEqual(generalized_jaccard(["ab","bc","bd"]), generalized_jaccard(["bd", "bc","ab"]))
        
    def test_generalized_jaccard_1(self):
        self.assertAlmostEqual(generalized_jaccard(["levenshtein","leuwenhstijn","leuvenstein"]), 0.545, 3)
        


class TestOverlap(unittest.TestCase):
    
    def test_overlap_empty_1(self):
        self.assertEqual(overlap("",""), 0.0)
        
    def test_overlap_empty_2(self):
        self.assertEqual(overlap("a",""), 0.0)
    
    def test_overlap_empty_3(self):
        self.assertEqual(overlap("","a"), 0.0)
        
    def test_overlap_identity(self):
        self.assertEqual(overlap("a","a"), 1.0)
        
    def test_overlap_symmetry(self):
        self.assertEqual(overlap("ab","bc"), overlap("bc","ab"))
        
    def test_overlap_1(self):
        self.assertAlmostEqual(overlap("levenshtein","leuwenhstijn"), 0.636, 3)
            


class TestOverlapMax(unittest.TestCase):
    
    def test_overlap_max_empty_1(self):
        self.assertEqual(overlap_max("",""), 0.0)
        
    def test_overlap_max_empty_2(self):
        self.assertEqual(overlap_max("a",""), 0.0)
    
    def test_overlap_max_empty_3(self):
        self.assertEqual(overlap_max("","a"), 0.0)
        
    def test_overlap_max_identity(self):
        self.assertEqual(overlap_max("a","a"), 1.0)
        
    def test_overlap_max_symmetry(self):
        self.assertEqual(overlap_max("ab","bc"), overlap_max("bc","ab"))
        
    def test_overlap_max_1(self):
        self.assertAlmostEqual(overlap_max("levenshtein","leuwenhstijn"), 0.583, 3)
            
        
if __name__ == '__main__':
    unittest.main()    