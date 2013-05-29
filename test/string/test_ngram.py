from daeso.string.ngram import n_gram_slices, n_gram_strings, n_gram_slices_range
import unittest


class TestNgramSlices(unittest.TestCase):
    
    def setUp(self):
        self.tokens = tuple("a nice sentence".split())
    
    def test_n_gram_slices_unigram(self):
        ng = n_gram_slices(self.tokens, 1)
        self.assertEqual(ng, [ ("a",), ("nice",), ("sentence",) ])
    
    def test_n_gram_slices_bigram(self):
        ng = n_gram_slices(self.tokens, 2)
        self.assertEqual(ng, [ ("a", "nice"), ("nice", "sentence") ])
    
    def test_n_gram_slices_trigram(self):
        ng = n_gram_slices(self.tokens, 3)
        self.assertEqual(ng, [ ("a", "nice", "sentence") ])
    
    def test_n_gram_slices_empty(self):
        ng = n_gram_slices((), 2)
        self.assertEqual(ng, [])    



class TestNgramSlicesPadded(unittest.TestCase):
    
    def setUp(self):
        self.tokens = tuple("a nice sentence".split())
    
    def test_n_gram_slices_unigram_padded(self):
        ng = n_gram_slices(self.tokens, 1, pad_size=0)
        self.assertEqual(ng, [ ("a",), ("nice",), ("sentence",) ])
    
    def test_n_gram_slices_bigram_padded(self):
        ng = n_gram_slices(self.tokens, 2, pad_size=1)
        self.assertEqual(ng, [ ("_", "a"), 
                               ("a", "nice"), 
                               ("nice", "sentence"), 
                               ("sentence", "_") ])
    
    def test_n_gram_slices_padded_empty(self):
        # this is probably not what you want,
        # but in a sense it is correct
        ng = n_gram_slices((), 2, pad_size=1)
        self.assertEqual(ng, [ ("_", "_") ])    

        

class TestNgramStrings(unittest.TestCase):
    
    def setUp(self):
        self.tokens = tuple("a nice sentence".split())
    
    def test_n_gram_strings_bigram(self):
        ng = n_gram_strings(self.tokens, 2)
        self.assertEqual(ng, [ "a nice", 
                               "nice sentence" ])
    
    def test_n_gram_strings_bigram_padded(self):
        ng = n_gram_strings(self.tokens, 2, pad_size=1)
        self.assertEqual(ng, [ "_ a",
                               "a nice", 
                               "nice sentence",
                               "sentence _"] )
    
    def test_n_gram_strings_empty(self):
        ng = n_gram_slices(tuple(), 2)
        self.assertEqual(ng, [])    



class TestNgramSlicesRange(unittest.TestCase):
    
    def setUp(self):
        self.tokens = tuple("a nice sentence".split())
        
    def test_n_gram_slices_range(self):
        ng = n_gram_slices_range(self.tokens, range(1,4))
        self.assertEqual(ng, { 1: [ ("a",), 
                                    ("nice",), 
                                    ("sentence",) ],
                                    2: [ ("a", "nice"), 
                                         ("nice", "sentence") ],
                                    3: [ ("a", "nice", "sentence") ]
                                } )
    
    def test_n_gram_slices_range_padded(self):
        ng = n_gram_slices_range(self.tokens, range(1, 4), pad=True)
        self.assertEqual(ng, { 1: [ ("a",), 
                                    ("nice",), 
                                    ("sentence",) ],
                                    2: [ ("_", "a"), 
                                         ("a", "nice"), 
                                         ("nice", "sentence"), 
                                         ("sentence", "_") ],
                                    3: [ ("_", "_", "a"), 
                                         ("_", "a", "nice"), 
                                         ("a", "nice", "sentence"),
                                         ("nice", "sentence", "_"),
                                         ("sentence", "_", "_" ) ]
                                } )
        

if __name__ == '__main__':
    unittest.main()