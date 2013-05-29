"""
test pgc (parallel graph corpus) command line scripts
"""

# assumes that all executables are in PATH

import glob
import os
import subprocess
import tempfile
import unittest
import zipfile



class Test_pgc_extract(unittest.TestCase):

    def setUp(self):
        self.pgc_fn = os.path.join(os.getcwd(), "..", "data", "news",
                                   "news-2006-11-aligned-part-00.pgc")
    
    def test_1_pgc_extract_phrases_help(self):
        print 
        subprocess.check_call(("pgc_extract_phrases.py", "-h"))
        
    def test_2_pgc_extract_phrases_default(self):
        print 
        subprocess.check_call(("pgc_extract_phrases.py", self.pgc_fn))
        
    def test_3_pgc_extract_phrases_options(self):
        # test with defaults
        print 
        subprocess.check_call(("pgc_extract_phrases.py", 
                               "--delimiter",
                               '#',
                               "--verbose",
                               self.pgc_fn))
        
        

class Test_pgc_join(unittest.TestCase):

    def setUp(self):
        pgc_dir = os.path.join(os.getcwd(), "..", "data", "news")
        # create pattern -- no need to quote because subprocess.check_call is
        # invoked without a shell, so no expansion takes place
        self.pattern = os.path.join(pgc_dir, "*.pgc") 
    
    def test_1_pgc_join_help(self):
        print 
        subprocess.check_call(("pgc_join.py", "-h"))
        
    def test_2_pgc_join_default(self):
        print 
        subprocess.check_call(("pgc_join.py", 
                               self.pattern))
        
    def test_3_pgc_join_options(self):
        # test with defaults
        print 
        subprocess.check_call(("pgc_join.py", 
                               "--format",
                               "--verbose",
                               self.pattern))
 
        
        
class Test_pgc_split(unittest.TestCase):

    def setUp(self):
        self.pgc_dir = os.path.join(os.getcwd(), "..", "data", "news")
        self.pgc_fn = os.path.join( self.pgc_dir,
                                    "news-2006-11-aligned-part-00.pgc")
    
    def test_1_pgc_split_help(self):
        print 
        subprocess.check_call(("pgc_split.py", "-h"))
        
    def test_2_pgc_split_default(self):
        print 
        subprocess.check_call(("pgc_split.py", 
                               self.pgc_fn))
        result = glob.glob(
            os.path.join(self.pgc_dir,
                         "news-2006-11-aligned-part-00_*-*.pgc"))
        self.assertEqual(len(result), 2)
        
    def test_3_pgc_split_options(self):
        print 
        subprocess.check_call(("pgc_split.py", 
                               "--size",
                               "10",
                               self.pgc_fn))
        result = glob.glob(
            os.path.join(self.pgc_dir,
                         "news-2006-11-aligned-part-00_*-*.pgc"))
        self.assertEqual(len(result), 8)
        
    def tearDown(self):
        # clean up parts
        # FIXME output should go to temp dir
        for fn in  glob.glob(
            os.path.join(self.pgc_dir,
                         "news-2006-11-aligned-part-00_*-*.pgc")):
            os.remove(fn)
            
        
        

class Test_pgc_zip(unittest.TestCase):

    def setUp(self):
        self.pgc_fn = os.path.join(os.getcwd(), "..", "data", "news",
                                   "news-2006-11-aligned-part-00.pgc")
    
    def test_1_pgc_zip_help(self):
        print 
        subprocess.check_call(("pgc_zip.py", "-h"))
        
    def test_2_pgc_zip_default(self):
        print 
        zip_file = os.path.join(tempfile.gettempdir(),
                                "news.zip")
        subprocess.check_call(("pgc_zip.py", 
                               zip_file,
                               self.pgc_fn))
        arch = zipfile.ZipFile(zip_file)
        arch.printdir()
        
            
            
        
if __name__ == '__main__':
    import sys
    sys.argv.append("-v")
    unittest.main()