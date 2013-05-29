from daeso.string.sgram import skip_bigram_slices, padded_skip_bigram_slices
import unittest


class TestSgramSlices(unittest.TestCase):
    
    def test_s_gram_slices(self):
        self.tokens = tuple("a nice sentence".split())
        sb = skip_bigram_slices(self.tokens)
        self.assertEqual(sb, [ ("a", "nice"), 
                               ("a", "sentence"), 
                               ("nice", "sentence") ])
    
    def test_s_gram_slices_limit(self):
        self.tokens = tuple("a really nice sentence".split())
        sb = skip_bigram_slices(self.tokens, 1)
        self.assertEqual(sb, [ ("a", "really"), 
                               ("a", "nice"),
                               # skips ("a", "sentence"),
                               ("really", "nice"),
                               ("really", "sentence"),
                               ("nice", "sentence") ])
    
    def test_s_gram_slices_empty(self):
        sb = skip_bigram_slices([])
        self.assertEqual(sb, [])  
    
    def test_padded_s_gram_slices(self):
        self.tokens = tuple("a nice sentence".split())
        sb = padded_skip_bigram_slices(self.tokens)
        self.assertEqual(sb, [ ("_", "a"),
                               ("_", "nice"),
                               ("_", "sentence"),
                               ("_", "_"), # !!!
                               ("a", "nice"), 
                               ("a", "sentence"),
                               ("a", "_"),
                               ("nice", "sentence"),
                               ("nice", "_"),
                               ("sentence", "_") ] )  


if __name__ == '__main__':
    unittest.main()