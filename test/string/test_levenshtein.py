from daeso.string.levenshtein import levenshtein, normalized_levenshtein
import unittest


class TestLevenshtein(unittest.TestCase):
    
    def test_levenshtein_no_overlap(self):
        d = levenshtein("abc", "def")
        self.assertEqual(d, 3)
    
    def test_levenshtein_some_overlap(self):
        d = levenshtein("abc", "dcb")
        self.assertEqual(d, 3)

    def test_levenshtein_identity(self):
        d = levenshtein("abc", "abc")
        self.assertEqual(d, 0)
        
    def test_levenshtein_on_words(self):
        d = levenshtein("i am a nice sentence".split(), 
                        "am i a new sentence".split())
        self.assertEqual(d, 3)
    
    def test_normalized_levenshtein_no_overlap(self):
        d = normalized_levenshtein("abc", "def")
        self.assertEqual(d, 1.0)
    
    def test_normalized_levenshtein_some_overlap(self):
        d = normalized_levenshtein("abc", "asbs")
        self.assertAlmostEqual(d, 0.5)

    def test_normalized_levenshtein_identity(self):
        d = normalized_levenshtein("abc", "abc")
        self.assertEqual(d, 0.0)
        
    def test_normalized_levenshtein_on_words(self):
        d = normalized_levenshtein("i am a nice sentence".split(), 
                                   "am i a new sentence".split())
        self.assertAlmostEqual(d, 0.59, 1)


if __name__ == '__main__':
    unittest.main()