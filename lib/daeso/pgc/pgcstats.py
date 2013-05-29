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
calculate statistics for parallel graph corpus
"""

__authors__ = "Erwin Marsi <e.marsi@gmail.com>"



# TODO
# - token threshold

import os

from daeso.pgc.corpus import ParallelGraphCorpus, LOAD_ALL
from daeso.stats.table import (
    StatsTable,
    percent)
from daeso.gb.gbstats import (
    GbStatsTable,
    graph_stats, 
    is_below_threshold)
from daeso.pair import Pair



class PgcStatsTable(StatsTable):
    
    columns_def = """
    
    CORPUS  string    parallel graph corpus file

    CGP     count     count of graph pairs
    CGPFU   count     count of graph pairs with full alignment 
    CGPFP   count     count of graph pairs with failed parse(s)
    CGPUR   count     count of graph pairs with unaligned roots
    PGPFU   percent   percentage of graph pairs with full alignment
    PGPFP   percent   percentage of aligned graph pairs with failed parse(s)
    PGPUR   percent   percentage of aligned graph pairs with unaligned roots

    CNP     count     count of aliged node pairs
    CEQ     count     count of equals relations
    CRE     count     count of restates relations
    CGEN    count     count of generalizes relations
    CSPEC   count     count of specifies relations
    CINT    count     count of intersects relations

    PEQ     percent   percentage of equals relations
    PRE     percent   percentage of restates relations
    PGEN    percent   percentage of generalizes relations
    PSPEC   percent   percentage of specifies relations
    PINT    percent   percentage of intersect relations
    
    """
        
    def calc_percent_overalls(self):
        #  graph percentages
        if self["CGP"].overall:
            self["PGPFP"].overall = percent( self["CGPFP"].overall,
                                             self["CGP"].overall)
            self["PGPUR"].overall = percent( self["CGPUR"].overall,
                                             self["CGP"].overall)
            self["PGPFU"].overall = percent( self["CGPFU"].overall,
                                             self["CGP"].overall)

        # relations percentages
        cnp = float(self["CNP"].overall)
    
        if cnp:
            for relation in "EQ RE SPEC GEN INT".split():
                self["P" + relation].overall = percent(self["C" +
                                                            relation].overall, cnp)
        
    
            
    
def pgc_stats(files, 
              with_empty_nodes=False,
              with_failed_parses=False,
              with_punc=False,
              with_unaligned_roots=False,
              threshold=0,
              with_unaligned_graphs=False):
    
    pgc_table = PgcStatsTable(size=len(files))
    gb_table = GbStatsTable()
    pgc_row = gb_row = 0
    
    for fn in files:
        pgc = ParallelGraphCorpus()
        pgc.read(inf=fn, graph_loading=LOAD_ALL)
        graph_pair_stats(os.path.basename(fn),
                         pgc,
                         pgc_table, 
                         pgc_row,
                         with_empty_nodes,
                         with_failed_parses,
                         with_punc,
                         with_unaligned_roots,
                         threshold)
        
        graphbanks = pgc._graphbanks()
        gb_table.grow(len(graphbanks))
    
        # somewhat messy to process pgc and gb files intertwined, 
        # but otherwise all graphbanks must be kept in memory
        for gb in graphbanks:
            graph_stats(gb,
                        gb_table, 
                        gb_row,
                        with_empty_nodes,
                        with_failed_parses,
                        with_punc,
                        with_unaligned_roots,
                        threshold,
                        with_unaligned_graphs)
            gb_row += 1
            
        pgc_row += 1

    pgc_table.summarize()
    gb_table.summarize()
    
    return pgc_table, gb_table


def graph_pair_stats(filename,
                     pgc,
                     pgc_table,
                     i,
                     with_empty_nodes=False,
                     with_failed_parses=False,
                     with_punc=False,
                     with_unaligned_roots=False,
                     threshold=0): 
    
    pgc_table["CORPUS"][i] = filename
    
    for graph_pair in pgc:
        found_failed_parses = found_unaligned_roots = False
        graphs = graph_pair.get_graphs()
        
        if ( graphs.source.is_failed_parse() or
             graphs.target.is_failed_parse() ):
            if with_failed_parses:
                # found a pair with failed parse(s),
                # but postpone counting because the pair might be discarded
                # for other reasons  (e.g. unaligned roots or threshold) 
                found_failed_parses = True
            else:
                continue            
            
        if not roots_are_aligned(graph_pair, graphs):
            if with_unaligned_roots:
                # found a pair with unaligned roots,
                # but postpone counting because the pair might be discarded
                # for other reasons (e.g. threshold) 
                found_unaligned_roots = True
            else:
                continue
            
        if threshold:
            if is_below_threshold(graphs.source.tokens, graphs.target.tokens,
                                  with_punc):
                continue
            
        pgc_table["CGP"][i] += 1
        
        if found_failed_parses:
            pgc_table["CGPFP"][i] += 1
            
        if found_unaligned_roots:
            pgc_table["CGPUR"][i] +=1
            # prepare for counting unaligned graphs per graphbank later on
            graphs.source.graph["root_aligned"] = False
            graphs.target.graph["root_aligned"] = False
            
        if not found_failed_parses and not found_unaligned_roots:
            pgc_table["CGPFU"][i] += 1
        
        node_pair_stats(graph_pair,
                        graphs,
                        pgc_table, 
                        i, 
                        with_empty_nodes, 
                        with_punc)
        
        # prepare for counting graph alignments per graphbank later on
        attr = graphs.source.graph
        attr["from_align"] = attr.get("from_align", 0) + 1
        
        attr = graphs.target.graph
        attr["to_align"] = attr.get("to_align", 0) + 1
        
    calc_percentages(pgc_table, i)


def node_pair_stats(graph_pair, 
                    graphs,
                    pgc_table,
                    i,
                    with_empty_nodes=False,
                    with_punc=False):
    for nodes, relation in graph_pair.alignments_iter():
        if not with_empty_nodes:
            if ( graphs.source.node_is_empty(nodes.source) or
                 graphs.target.node_is_empty(nodes.target)):
                continue
            
        if not with_punc:
            if ( graphs.source.node_is_punct(nodes.source) or
                 graphs.target.node_is_punct(nodes.target)):
                continue
            
        pgc_table["CNP"][i] += 1
        
        # TODO: this is DAESO specific, but should be generic
        if relation == "equals":
            pgc_table["CEQ"][i]  += 1
        elif relation == "restates":
            pgc_table["CRE"][i]  += 1
        elif relation == "specifies":
            pgc_table["CSPEC"][i]  += 1
        elif relation == "generalizes":
            pgc_table["CGEN"][i]  += 1
        elif relation == "intersects":
            pgc_table["CINT"][i]  += 1
        else:
            raise AssertionError("Unknown relation: " + relation)
        
        # prepare for counting node alignments per graph bank later on
        attr = graphs.source.node[nodes.source]
        attr["from_align"] = attr.get("from_align", 0) + 1
        
        attr = graphs.target.node[nodes.target]
        attr["to_align"] = attr.get("to_align", 0) + 1
        

        
def calc_percentages(pgc_table, i):
        #  graph percentages
        if pgc_table["CGP"][i]:
            pgc_table["PGPFP"][i] = percent(pgc_table["CGPFP"][i],
                                            pgc_table["CGP"][i])
            pgc_table["PGPUR"][i] = percent(pgc_table["CGPUR"][i],
                                            pgc_table["CGP"][i])
            pgc_table["PGPFU"][i] = percent(pgc_table["CGPFU"][i],
                                            pgc_table["CGP"][i])

        # relations percentages
        cnp = float(pgc_table["CNP"][i])
    
        if cnp:
            for relation in "EQ RE SPEC GEN INT".split():
                pgc_table["P" + relation][i] = percent(pgc_table["C" +
                                                                 relation][i], cnp)
        
    
    
def roots_are_aligned(graph_pair, graphs):
    return graph_pair.has_edge(graphs.source.root, graphs.target.root)

