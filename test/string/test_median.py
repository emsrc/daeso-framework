from daeso.string.median import set_median_string
from daeso.string.levenshtein import levenshtein
import unittest


class TestMedian(unittest.TestCase):
    
    def test_set_median_string_1(self):
        s = set_median_string(['SpSm', 'mpamm', 'Spam', 'Spa', 'Sua', 'hSam'],
                              levenshtein)
        self.assertEqual(s, "Spam")
        
    def test_set_median_string_2(self):
        strings = ['ehee', 'cceaes', 'chees', 'chreesc', 'chees', 'cheesee',
                   'cseese', 'chetese']
        s = set_median_string(strings, levenshtein)
        self.assertEqual(s, "chees")
        
    def test_set_median_string_with_sentences(self):
        s1 = "i am a nice sentence"
        s2 = "am i a new sentence"
        s3 = "a nice sentence i am indeed"
        
        sentences = [s1.split(), s2.split(), s3.split()]
        
        sm = set_median_string(sentences, levenshtein)
        self.assertEqual(" ".join(sm), s1)
        

if __name__ == '__main__':
    unittest.main()