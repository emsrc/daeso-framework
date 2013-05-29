"""
test PGCParser and PGCGenerator classes from daeso.pgc.corpus
"""

import os
import shutil
import tempfile
import unittest
import xml.etree.cElementTree as et

from daeso.pgc.corpus import ( ParallelGraphCorpus, PGCParser, PGCGenerator,
                                LOAD_ALL, LOAD_NONE, LOAD_SPARSE )
from daeso.gb.graphstub import GraphStub
from daeso.gb.graphbank import GraphBank, SparseGraphBank
from daeso.exception import DaesoError
from daeso.pair import Pair



        
class Test_PGCParser(unittest.TestCase):
    
    def test_parser_load_all(self):
        parser = PGCParser()
        pg_corpus = parser.parse("data/corpus-2.pgc",
                                 graph_loading=LOAD_ALL)
    
        for graph_pair in pg_corpus:
            for graph in graph_pair._graphs:
                self.assertFalse(isinstance(graph, GraphStub))
                
            for bank in graph_pair._banks:
                self.assertEqual(bank.__class__, GraphBank)
                self.assertEqual(len(bank), 5)
                
                
    def test_parser_load_sparse(self):
        parser = PGCParser()
        pg_corpus = parser.parse("data/corpus-2.pgc",
                                 graph_loading=LOAD_SPARSE)

        for graph_pair in pg_corpus:
            for graph in graph_pair._graphs:
                self.assertFalse(isinstance(graph, GraphStub))
                
            for bank in graph_pair._banks:
                self.assertEqual(bank.__class__, SparseGraphBank)
                self.assertEqual(len(bank), 3)
        
        
    def test_parser_load_none(self):
        parser = PGCParser()
        pg_corpus = parser.parse("data/corpus-2.pgc",
                                 graph_loading=LOAD_NONE)
        
        for graph_pair in pg_corpus:
            for graph in graph_pair._graphs:
                self.assertTrue(isinstance(graph, GraphStub))
                
            for bank in graph_pair._banks:
                self.assertEqual(bank.__class__, SparseGraphBank)
                self.assertEqual(len(bank), 3)
                
                
    def test_parser_load_relaxed(self):
        tmp_dir = tempfile.gettempdir()
        shutil.copy("data/corpus-2.pgc",
                    tmp_dir + "/corpus-2.pgc")
        shutil.copy("../gb/data/source-gb-2.xml", 
                    tmp_dir + "/source-gb-2.xml")
        shutil.copy("../gb/data/target-gb-2.xml", 
                    tmp_dir + "/target-gb-2.xml")
        
        pg_corpus = ParallelGraphCorpus()
        pg_corpus.read(tmp_dir + "/corpus-2.pgc",
                       relax_gb_paths=True)
    
        for graph_pair in pg_corpus:
            for graph in graph_pair._graphs:
                self.assertFalse(isinstance(graph, GraphStub))
                
            for bank in graph_pair._banks:
                self.assertEqual(bank.__class__, SparseGraphBank)
                self.assertEqual(len(bank), 3)
                
        os.remove(tmp_dir + "/corpus-2.pgc")
        os.remove(tmp_dir + "/source-gb-2.xml")
        os.remove(tmp_dir + "/target-gb-2.xml")

                
    def test_parser_node_pairs(self):
        """
        check if all node_pair are correctly read
        """
        parser = PGCParser()
        pg_corpus = parser.parse("data/corpus-2.pgc")
        
        true_align = [ (Pair("4","4"), "equals"),
                       (Pair("8","11"), "equals"),
                       (Pair("5","5"), "equals"),
                       (Pair("11","10"), "intersects"),
                       (Pair("19","8"), "intersects"),
                       (Pair("1","1"), "restates"),
                       (Pair("0","0"), "restates") ]
        
        read_align = pg_corpus[1].alignments()
        
        self.assertEqual(len(read_align), len(true_align))

        for e in read_align:
            true_align.remove(e)
            
        self.assertFalse(true_align)


class Test_PGCParser_Errors(unittest.TestCase):
    """
    Test robustness against common cases semantically invalid xml
    (but not for invalid xml due or extra/missing elements/attributes).
    """
    
    def setUp(self):
        # create an element tree which we can mutilate and save
        pg_corpus = ParallelGraphCorpus(inf="data/corpus-1.pgc")
        self.tmpfn = tempfile.NamedTemporaryFile().name
        generator = PGCGenerator()  
        self.tree = generator.generate(pg_corpus, outf=self.tmpfn)
        
    
    def test_unresolved_graphs(self):
        graph_pair_elem = self.tree.find("//graph_pair")
        graph_pair_elem.set("from_graph_id", "XXX")
        self.tree.write(self.tmpfn)
        
        # will pas unnoticed with LOAD_NONE
        for graph_loading in (LOAD_ALL, LOAD_SPARSE):
            parser = PGCParser()
            self.assertRaises(DaesoError,
                              parser.parse,
                              self.tmpfn, 
                              graph_loading=graph_loading)  
            
            
    def test_unresolved_graphbanks(self):
        graph_pair_elem = self.tree.find("//graph_pair")
        graph_pair_elem.set("from_bank_id", "XXX")
        self.tree.write(self.tmpfn)
                        
        for graph_loading in (LOAD_ALL, LOAD_SPARSE, LOAD_NONE):
            parser = PGCParser()
            ##parser.parse(self.tmpfn, graph_loading=graph_loading)
            self.assertRaises(DaesoError,
                              parser.parse,
                              self.tmpfn, 
                              graph_loading=graph_loading)
            
        
    def test_missing_graphbank(self):
        file_elem = self.tree.find("//file")
        file_elem.text = "XXX"
        self.tree.write(self.tmpfn)

        parser = PGCParser()
        self.assertRaises(DaesoError,
                          parser.parse,
                          self.tmpfn) 

        


    
    
class Test_PGCGenerator(unittest.TestCase):
    
    def setUp(self):
        parser = PGCParser()
        self.pg_corpus = parser.parse("data/corpus-1.pgc")
        self.generator = PGCGenerator()        
        self.tmpfn = tempfile.NamedTemporaryFile().name
        
        
    def _can_be_parsed(self, corpus_filename):
        parser = PGCParser()
        corpus = parser.parse(corpus_filename)
        return len(corpus)
        
        
    def test_rel_path(self):
        """
        test if relative graphbank file paths are correct after saving the
        corpus in a different directory
        """
        tree = self.generator.generate(self.pg_corpus, outf=self.tmpfn,
                                       pprint=True)
        out_dir = os.path.dirname(self.tmpfn)
        
        for file_elem in tree.findall("//file"):
            rel_path = file_elem.text
            self.assertFalse(os.path.isabs(rel_path))
            
            abs_path = os.path.join(out_dir, rel_path)
            self.assertTrue(os.path.exists(abs_path))
        
        self.assertTrue(self._can_be_parsed(self.tmpfn))

            
    def test_abs_path(self):
        """
        test if absolute graphbank file paths are correct after saving the
        corpus in a different directory
        """
        tree = self.generator.generate(self.pg_corpus, outf=self.tmpfn,
                                       pprint=True, abs_path=True)
        
        for file_elem in tree.findall("//file"):
            gb_path = file_elem.text
            self.assertTrue(os.path.isabs(gb_path))
            self.assertTrue(os.path.exists(gb_path))
            
        self.assertTrue(self._can_be_parsed(self.tmpfn))
        
        
    def test_merge_1(self):
        """
        merging a corpus with copy of itself should not change the number of
        graphbanks
        """
        parser = PGCParser()
        pg_corpus2 = parser.parse("data/corpus-1.pgc")
        self.pg_corpus.extend(pg_corpus2)
        
        self.assertEqual(len(self.pg_corpus),
                         2*len(pg_corpus2))
        
        tree = self.generator.generate(self.pg_corpus, outf=self.tmpfn,
                                       pprint=True, abs_path=True)
        
        gb_elem = tree.find("//graphbanks")
        
        self.assertEqual(len(gb_elem), 2)
            
        self.assertTrue(self._can_be_parsed(self.tmpfn))
        

    def test_merge_2(self):
        """
        merging a corpus with another corpus should change the number of
        graphbanks
        """
        parser = PGCParser()
        pg_corpus2 = parser.parse("data/corpus-2.pgc")
        self.pg_corpus.extend(pg_corpus2)
        
        self.assertEqual(len(self.pg_corpus), 6)
        
        tree = self.generator.generate(self.pg_corpus, outf=self.tmpfn,
                                       pprint=True, abs_path=True)
        
        gb_elem = tree.find("//graphbanks")
        
        self.assertEqual(len(gb_elem), 4)
            
        self.assertTrue(self._can_be_parsed(self.tmpfn))        
        
        
        
        

if __name__ == '__main__':
    import sys
    import warnings
    from daeso.exception import DaesoWarning
        
    warnings.simplefilter("ignore",  DaesoWarning)  
    sys.argv.append("-v")
    #Test_PGCParser_Errors("test_unresolved_graphbanks").run()
    unittest.main()
            