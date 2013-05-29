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
calculate statistics for graph bank
"""

__authors__ = "Erwin Marsi <e.marsi@gmail.com>"

# TODO
# - token threshold

import os
import string

from daeso.gb.graphbank import GraphBank
from daeso.stats.table import StatsTable, percent



class GbStatsTable(StatsTable):
    
    columns_def = """
    BANK    string    graph bank file    
    
    CG      count     count of graphs    
    
    CGA     count     count of aligned graphs    
    CGU     count     count of unaligned graphs    
    CGSA    count     count of single aligned graphs    
    CGMA    count     count of multiple aligned graphs    
    CGUR    count     count of graphs with unaligned roots    
    CGFP    count     count of graphs with failed parses    
    
    PGA     percent   percentage of aligned graphs    
    PGSA    percent   percentage of single aligned graphs    
    PGMA    percent   percentage of multiple aligned graphs    
    PGUR    percent   percentage of graphs with unaligned roots    
    PGFP    percent   percentage of graphs with failed parses    
    
    CT      count     count of tokens    
    ATG     average   average number of tokens per graph    
    
    CN      count     count of nodes    
    ANG     average   average number of nodes per graph    
    
    CNA     count     count of aligned nodes    
    CNU     count     count of unaligned nodes    
    
    PNA     percent   percentage of aligned nodes    
    """

    def calc_percent_overalls(self):
        if self["CG"].overall:
            self["PGA"].overall = percent( self["CGA"].overall,
                                           self["CG"].overall)
            self["PGFP"].overall = percent( self["CGFP"].overall,
                                            self["CG"].overall)
            self["PGUR"].overall = percent( self["CGUR"].overall,
                                            self["CG"].overall)
        
        if self["CGA"].overall:
            self["PGSA"].overall = percent( self["CGSA"].overall,
                                            self["CGA"].overall)
            self["PGMA"].overall = percent( self["CGMA"].overall,
                                            self["CGA"].overall)
        
        if self["CN"].overall:
            self["PNA"].overall = percent( self["CNA"].overall,
                                           self["CN"].overall)
            
            
    def calc_average_overalls(self):
        if self["CG"].overall:
            self["ATG"].overall = self["CT"].overall / float(self["CG"].overall)
            self["ANG"].overall = self["CN"].overall / float(self["CG"].overall)

            


def gb_stats(files,
             format,
             with_empty_nodes=False,
             with_failed_parses=False,
             with_punc=False,
             threshold=0):
    
    gb_table = GbStatsTable(size=len(files))
    gb_row = 0
    
    for i, fn in enumerate(files):
        bank = GraphBank(file_path=fn, format=format)
        bank.load()
        graph_stats(bank,
                    gb_table, 
                    i,
                    with_empty_nodes,
                    with_failed_parses,
                    with_punc,
                    with_unaligned_roots=True,
                    threshold=threshold,
                    with_unaligned_graphs=True)
        
    gb_table.summarize()
    return gb_table


def graph_stats(gb,
                gb_table, 
                i,
                with_empty_nodes=False,
                with_failed_parses=False,
                with_punc=False,
                with_unaligned_roots=False,
                threshold=0,
                with_unaligned_graphs=False):
    name = os.path.basename(gb.get_file_path())
    gb_table["BANK"][i] = name

    for graph in gb:                                   
        if graph.is_failed_parse():
            if with_failed_parses:
                gb_table["CGFP"][i] += 1
            else:
                continue
        
        if not root_aligned(graph):
            if with_unaligned_roots:
                gb_table["CGUR"][i] +=1
            else:
                continue
            
        if threshold:
            # FIXME
            raise UserWarning("threshold not implemented!")
            
        if not graph_is_aligned(graph):
            if with_unaligned_graphs:
                gb_table["CGU"][i] += 1
            else:
                continue
        else:
            gb_table["CGA"][i] += 1
            
            if graph_is_single_aligned(graph):
                gb_table["CGSA"][i] +=1
            else:
                gb_table["CGMA"][i] += 1
        
        gb_table["CG"][i] += 1
        gb_table["CT"][i] += count_tokens(graph, with_punc)
        
        node_stats(gb_table, i, graph, with_empty_nodes, with_punc)
        
    calc_percentages(gb_table, i)
        
    return gb_table


def count_tokens(graph, with_punc):
    if with_punc:
        tokens = graph.tokens
    else:
        tokens = [ t for t in graph.tokens
                   if t not in string.punctuation ]
        
    return len(tokens)


def node_stats(gb_table, i, graph, with_empty_nodes, with_punc):
    for node in graph:
        if not with_punc and graph.node_is_punct(node):
            continue
        
        if not with_empty_nodes and graph.node_is_empty(node):
            continue
        
        gb_table["CN"][i] += 1
        
        if node_is_aligned(graph, node):
            gb_table["CNA"][i] += 1
        else:
            gb_table["CNU"][i] += 1

            
def calc_percentages(gb_table, i):
    if gb_table["CG"][i]:
        gb_table["PGA"][i] = percent( gb_table["CGA"][i],
                                      gb_table["CG"][i])
        gb_table["PGFP"][i] = percent(gb_table["CGFP"][i],
                                      gb_table["CG"][i])
        gb_table["PGUR"][i] = percent( gb_table["CGUR"][i],
                                       gb_table["CG"][i])
        gb_table["ATG"][i] = gb_table["CT"][i] / float(gb_table["CG"][i])
        gb_table["ANG"][i] = gb_table["CN"][i] / float(gb_table["CG"][i])
    
    if gb_table["CGA"][i]:
        gb_table["PGSA"][i] = percent( gb_table["CGSA"][i],
                                       gb_table["CGA"][i])
        gb_table["PGMA"][i] = percent( gb_table["CGMA"][i],
                                       gb_table["CGA"][i])
    
    if gb_table["CN"][i]:
        gb_table["PNA"][i] = percent( gb_table["CNA"][i],
                                      gb_table["CN"][i])
    
        
def is_below_threshold(from_tokens, to_tokens, with_punc):
    raise NotImplementedError("threshold not implemented!")
        

        
# The following three functions are intended for use with daeso.pgc.pgcstats        

def node_is_aligned(graph, node):
    # This function can be called after daeso.pgc.pgcstats.graph_pair_stats
    # has added the "from_align" and "to_align" attributes to graphs and nodes.
    return ( graph.node[node].get("from_align") or 
             graph.node[node].get("to_align") )


def graph_is_aligned(graph):
    # This function can be called after daeso.pgc.pgcstats.graph_pair_stats
    # has added the "from_align" and "to_align" attributes to graphs and nodes.
    return ( graph.graph.get("from_align") or
             graph.graph.get("to_align") )
    
    
def graph_is_single_aligned(graph):
    # This function can be called after daeso.pgc.pgcstats.graph_pair_stats
    # has added the "from_align" and "to_align" attributes to graphs and nodes.
    return ( graph.graph.get("from_align") == 1 or
             graph.graph.get("to_align") == 1 )
    

def root_aligned(graph):
    # This function can be called after daeso.pgc.pgcstats.graph_pair_stats
    # has added the "root_aligned" attribute to unaligned graphs

    # if attribute is lacking, assume it is aligned
    return graph.graph.get("root_aligned", True)
    


            
            