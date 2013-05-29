from daeso.string.tf_idf import tf_idf, idf
from math import log
import unittest


class TestTfIdf(unittest.TestCase):
    
    def test_tf_idf_1(self):
        dtc = [ ["a"] ]
        w = tf_idf(dtc)
        self.assertEqual(w, (["a"], 
                             [[1/1.0 * log(1/1.0)]]))
        
    def test_tf_idf_2(self):
        dtc = [ ["a", "b"] ]
        w = tf_idf(dtc)
        self.assertEqual(w, (["a", "b"],
                             [[1/2.0 * log(1/1.0), 
                              1/2.0 * log(1/1.0)]]))
        
    def test_tf_idf_3(self):
        dtc = [ ["a"], ["a"] ]
        w = tf_idf(dtc)
        self.assertEqual(w, (["a"], 
                             [[1/1.0 * log(2/2.0)], 
                              [1/1.0 * log(2/2.0)]]))
        
    def test_tf_idf_4(self):
        dtc = [ ["a"], ["b"] ]
        w = tf_idf(dtc)
        self.assertEqual(w, (["a", "b"],
                             [[1/1 * log(2/1.0), 0.0], 
                              [0.0, 1/1 * log(2/1.0)]]))
        
    def test_tf_idf_5(self):
        dtc = [ ["a", "b", "a", "c"], 
                ["b", "d"] ]
        w = tf_idf(dtc)
        self.assertEqual(w, (["a", "b", "c", "d"],
                             [[2/4.0 * log(2/1.0), # a
                               1/4.0 * log(2/2.0), # b 
                               1/4.0 * log(2/1.0), # c
                               0/4.0 * log(2/1.0)  # d
                               ], 
                               [0/2.0 * log(2/1.0), # a
                                1/2.0 * log(2/2.0), # b 
                                0/2.0 * log(2/1.0), # c
                                1/2.0 * log(2/1.0)  # d
                            ] 
                          ]))
        
    def test_tf_idf_empty_1(self):
        dtc = []
        self.assertEqual(tf_idf(dtc), ([], []))
        
    def test_tf_idf_empty_2(self):
        dtc = [[]]
        self.assertEqual(tf_idf(dtc), ([], [[]]))
        
    def test_tf_idf_empty_3(self):
        dtc = [["a"], []]
        self.assertEqual(tf_idf(dtc), (["a"], [[1/1 * log(2/1)], [0.0]]))

        
class TestIdf(unittest.TestCase):
    
    def test_idf_1(self):
        dtc = [ ["a"] ]
        w = idf(dtc)
        self.assertEqual(w, (["a"], 
                             [[log(1/1.0)]]))
        
    def test_idf_2(self):
        dtc = [ ["a", "b"] ]
        w = idf(dtc)
        self.assertEqual(w, (["a", "b"],
                             [[log(1/1.0), 
                               log(1/1.0)]]))
        
    def test_idf_3(self):
        dtc = [ ["a"], ["a"] ]
        w = idf(dtc)
        self.assertEqual(w, (["a"], 
                             [[log(2/2.0)], 
                              [log(2/2.0)]]))
        
    def test_idf_4(self):
        dtc = [ ["a"], ["b"] ]
        w = idf(dtc)
        self.assertEqual(w, (["a", "b"],
                             [[log(2/1.0), log(2/1.0)], 
                              [log(2/1.0), log(2/1.0)]]))
        
    def test_idf_5(self):
        dtc = [ ["a", "b", "a", "c"], 
                ["b", "d"] ]
        w = idf(dtc)
        self.assertEqual(w, (["a", "b", "c", "d"],
                             [[log(2/1.0), # a
                               log(2/2.0), # b 
                               log(2/1.0), # c
                               log(2/1.0)  # d
                               ], 
                               [log(2/1.0), # a
                                log(2/2.0), # b 
                                log(2/1.0), # c
                                log(2/1.0)  # d
                            ] 
                          ]))
        
    def test_idf_empty_1(self):
        dtc = []
        self.assertEqual(idf(dtc), ([], []))
        
    def test_idf_empty_2(self):
        dtc = [[]]
        self.assertEqual(idf(dtc), ([], [[]]))
        
    def test_idf_empty_3(self):
        dtc = [["a"], []]
        self.assertEqual(idf(dtc), (["a"], [[log(2/1)], [log(2/1.0)]]))
                
    def test_idf_normalized(self):
        dtc = [ ["a", "b", "a", "c"], 
                ["b", "d"] ]
        w = idf(dtc, normalized=True)
        self.assertEqual(w, (["a", "b", "c", "d"],
                             [[log(2/1.0) / log(2), # a
                               log(2/2.0) / log(2), # b 
                               log(2/1.0) / log(2), # c
                               log(2/1.0) / log(2)  # d
                               ], 
                               [log(2/1.0) / log(2), # a
                                log(2/2.0) / log(2), # b 
                                log(2/1.0) / log(2), # c
                                log(2/1.0) / log(2)  # d
                            ] 
                          ]))    

if __name__ == '__main__':
    unittest.main()