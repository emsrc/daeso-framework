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
report statistics over (part of) the files from a corpus (segment)
"""

# TODO:
# - not tested on windows
# - design flaw: it's funny that we have to write the tables, 
#   then parse them  and add them to another table, while we have
#   both tables in memory


__authors__ = "Erwin Marsi <e.marsi@gmail.com>"

from sys import stderr
from glob import glob
from os import getcwd, chdir, path

from daeso.pgc.pgcstats import pgc_stats, PgcStatsTable 
from daeso.gb.gbstats import GbStatsTable



def corpus_seg_stats(targets,
                     seg_dir, 
                     annot_dirs=("ma", "aa", "na"),
                     subseg_dirs=None,
                     pgc_files_pattern="*.pgc",
                     verbose=True):
    """
    report statistics over (part of) the files from a corpus (segment)
    """
    assert subseg_dirs
    
    targets = dict.fromkeys(targets or ["all"])
    
    seg_dir = seg_dir.rstrip(path.sep)
    # assume final dir of seg_dir path represents 
    seg = seg_dir.split(path.sep)[-1]
    
    pgc_tables = dict(all=PgcStatsTable())
    gb_tables = dict(all=GbStatsTable())
    
    for annot in annot_dirs:
        pgc_tables[annot] = PgcStatsTable()
        gb_tables[annot] = GbStatsTable()
        
        # **** HACK *** !
        if annot == "na":
            # We typically want to know how many potential tokens an unanotated
            # file contains, that is, the CT columns in the graph bank stats.
            # However, the token t will be zero because by default graphs with
            # unaligned roots are discounted. hence we need to set the
            # with_unaligned_roots option.
            # This also means that the token count over both ma/aa and na is
            # a overestimation, because some aligned graph pairs may be wrong.
            with_unaligned_roots = True
        else:
            with_unaligned_roots = False
        
        for subseg in subseg_dirs:
            # ****** HACK *****
            # Replacing "/" by "." is a quick hack to facilitate deepr subdirs
            # Should be fixed in a proper manner!
            gb_tab_fn = ".".join(("stats", seg, annot, subseg, "gb")).replace("/",".")
            pgc_tab_fn = ".".join(("stats", seg, annot, subseg, "pgc")).replace("/",".")  
            
            if ( "all" in targets or
                 annot in targets or
                 subseg in targets or 
                 (annot + "." +  subseg) in targets ):
                
                pgc_dir = path.join(seg_dir, "pgc", annot, subseg)
                
                print "Processing corpora files in ", pgc_dir
                
                # this assumes there are no duplicates of part/whole pgc files in
                # this directory
                pgc_tab, gb_tab = stats(pgc_dir,
                                        pgc_files_pattern,
                                        with_unaligned_roots)
                
                write_table(pgc_tab, pgc_tab_fn, verbose=verbose)
                write_table(gb_tab, gb_tab_fn, verbose=verbose)
            
            read_subtable(pgc_tables[annot], pgc_tab_fn)
            read_subtable(gb_tables[annot], gb_tab_fn)
            
        pgc_tables[annot].summarize()
        pgc_tab_fn = ".".join(("stats", seg, annot, "pgc")) 
        write_table(pgc_tables[annot], pgc_tab_fn, verbose=verbose)
        read_subtable(pgc_tables["all"], pgc_tab_fn, verbose=verbose)
        
        gb_tables[annot].summarize()
        gb_tab_fn = ".".join(("stats", seg, annot, "gb"))
        write_table(gb_tables[annot], gb_tab_fn, verbose=verbose)
        read_subtable(gb_tables["all"], gb_tab_fn, verbose=verbose)
        
    pgc_tab_fn = "stats.%s.pgc" % seg
    pgc_tables["all"].summarize()
    write_table(pgc_tables["all"], pgc_tab_fn, verbose=verbose)

    gb_tab_fn = "stats.%s.gb" % seg
    gb_tables["all"].summarize()
    write_table(gb_tables["all"], gb_tab_fn, verbose=verbose)
    


def stats(pgc_dir, pgc_files_pattern, with_unaligned_roots=False):
    """
    return statistics tables for all matching parallel graph corpora and 
    associated graph banks
    """
    cwd = getcwd()
    
    # must change to dir of pgc files,
    # because paths to gb files are interpreted relative to location of pgc file 
    try:
        chdir(pgc_dir)
    except OSError:
        # dir does not exist
        # assume there are no files, which results in a empty table
        pgc_files = []
    else:
        pgc_files = glob(pgc_files_pattern)
        
    pgc_table, gb_table = pgc_stats(pgc_files, 
                                    with_unaligned_roots=with_unaligned_roots)

    chdir(cwd)
    
    return  pgc_table, gb_table
    

    
def read_subtable(table, fn, verbose=True):
    """
    try to read a stats table for parallel graph corpora or graph banks
    """
    try:
        if verbose: print "Reading table", fn
        table.read(fn)
    except IOError:
        print >>stderr, "Warning: no file", fn

        
        
def write_table(table, fn, verbose=True):
    """
    write a stats table for parallel graph corpora or graph banks
    unless it is empty
    """
    if not table.is_empty():
        if verbose: print "Writing table", fn
        table.write(out=file(fn, "w"))