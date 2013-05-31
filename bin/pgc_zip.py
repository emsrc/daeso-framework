#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2007-2013 by Erwin Marsi and TST-Centrale
#
# This file is part of the DAESO Framework.
#
# The DAESO Framework is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# The DAESO Framework is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
Create a zip archive containing one or more parallel graph corpora
together with the required graphbanks.
"""

epilog = """ 
The prime use case is packing corpus and graphbank files for annotation at
another site without changing the original graphbank file paths. In the
archived directory, copies of corpus files and their corresponding graphbank
files are stored together. However, the orginal file paths to the graphbanks
as recorded in the corpus files will not be changed. The corpus file should
therefore be read with the 'relax_gb_paths' option, which allows graphbank
files to be read from the same direcory as the corpus file instead of the
location specified in the <file> XML element. Algraeph also reads corpora
under this the relaxed interpretation.
"""

__authors__ = 'Erwin Marsi <e.marsi@gmail.com>'


import os
import zipfile


from daeso.utils.cli import DaesoArgParser
from daeso.utils.opsys import multiglob
from daeso.pgc.corpus import ParallelGraphCorpus, LOAD_NONE


def pgc_zip(zip_filename, pgc_filenames):
    zip_arch = zipfile.ZipFile(zip_filename, "w")
    arch_dir = os.path.splitext( os.path.basename(zip_filename))[0]
    
    for corpus_filename in multiglob(pgc_filenames):
        # add corpus to archive
        arch_filename = os.path.join( arch_dir,
                                      os.path.basename(corpus_filename) )
        zip_arch.write(corpus_filename, arch_filename)
        
        corpus = ParallelGraphCorpus(inf=corpus_filename,
                                     graph_loading=LOAD_NONE)

        for gb in corpus._graphbanks():
            gb_filename = gb.get_file_path()
            # add graphbank files to archive
            arch_filename = os.path.join( arch_dir,
                                          os.path.basename(gb_filename) )
            zip_arch.write(gb_filename, arch_filename)
            
    zip_arch.close()
    

parser = DaesoArgParser(description=__doc__,
                        epilog=epilog)

parser.add_argument(
    "zip_file", 
    metavar="ZIP_FILE",
    help="filename of zip archive")

parser.add_argument(
    "pgc_files", 
    nargs="+", 
    metavar="CORPUS_FILE",
    help="parallel graph corpus filename, "
    "or quoted file name pattern for parallel graph corpora")

args = parser.parse_args()

pgc_zip(args.zip_file, args.pgc_files)




