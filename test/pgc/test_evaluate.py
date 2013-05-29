"""
test pgc evaluate
"""

import pickle
import tempfile
import unittest

from daeso.pgc.corpus import ParallelGraphCorpus
from daeso.pgc.evaluate import AlignEval


class TestEvalAlign(unittest.TestCase):

    def setUp(self):
        pass
    
    def test_pickle(self):
        true_corpus = pred_corpus = ParallelGraphCorpus(inf="data/corpus-1.pgc")
        align_eval = AlignEval()
        align_eval.add(true_corpus, pred_corpus, "corpus-1")
        align_eval.run_eval()

        pickle_file = tempfile.TemporaryFile()
        pickle.dump(align_eval, pickle_file, 2)
        pickle_file.seek(0)
        align_eval_2 = pickle.load(pickle_file)
        align_eval_2.write()

        
        
if __name__ == '__main__':
    import sys
    sys.argv.append("-v")
    unittest.main()