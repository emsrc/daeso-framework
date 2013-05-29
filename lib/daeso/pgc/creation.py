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
creating a parallel graph corpus from a parallel text corpus and graphbanks
"""

__authors__ = "Erwin Marsi <e.marsi@gmail.com>"

import sys

from daeso.ptc.document import HitaextDoc
from daeso.pgc.corpus import ParallelGraphCorpus
from daeso.pgc.graphpair import GraphPair
from daeso.gb.graphbank import GraphBank
from daeso.pair import Pair
from daeso.relations import RELATIONS

# TODO:
# - unittest


def pgc_from_ptc(text_corpus_file,
                 source_graphbank_file, 
                 target_graphbank_file,
                 focus_tags=Pair("s", "s"),
                 graph_formats=Pair("alpino", "alpino"),
                 relations=RELATIONS,
                 min_token_diff=0,
                 max_token_len=99999):
    """
    Create a new parallel graph corpus from a parallel text corpus and a pair of
    graphbanks
    
    @PARAM text_corpus_file: parallel text corpus filename
    @PARAM source_bank: source graphank filename
    @PARAM target_bank: target graphbank filname
        
    @KEYWORD focus_tags: pair of focus tags
    @KEYWORD graph_format: pair of graphbank formats
    @KEYWORD relations: list of alignment relations
    @keyword min_token_diff: minimum number of different tokens
    @keyword max_token_len: maximum number of tokens per focus element 
    
    @RETURN: ParallelGraphCorpus object
    """
    # read parallel text corpus
    text_corpus = HitaextDoc(file=text_corpus_file)    
    doc_trees = text_corpus.get_doc_trees(search=True)
    
    # read graph banks
    source_bank = GraphBank(source_graphbank_file,
                            graph_formats.source)
    source_bank.load()
    target_bank = GraphBank(target_graphbank_file,
                            graph_formats.target)
    target_bank.load()
    graph_banks = Pair(source_bank, target_bank)
    
    # create an empty parallel graph corpus
    graph_corpus = ParallelGraphCorpus(relations=relations)
    
    for alignment in text_corpus.alignment:
        if ( alignment.get("from_tag") != focus_tags.source or 
             alignment.get("to_tag") != focus_tags.target ):
            continue
        
        source_tokens = _get_elem_tokens(doc_trees.source,
                                         focus_tags.source,
                                         alignment.get("from_id"))
        target_tokens = _get_elem_tokens(doc_trees.target,
                                         focus_tags.target,
                                         alignment.get("to_id"))
        
        if len(source_tokens) > max_token_len or len(target_tokens) > max_token_len:
            continue
        
        if ( min_token_diff and
             _token_diff(source_tokens, target_tokens)  < min_token_diff ):
            continue
        
        # the crucial assumption is that id's of the aligned focus
        # elements in the marked-up text have corresponding graphs with
        # the same id in the graph banks
        source_graph_id = alignment.get("from_id")
        target_graph_id = alignment.get("to_id")
        graphs = Pair(
            source_bank.get_graph(source_graph_id),
            target_bank.get_graph(target_graph_id))
        
        graph_pair = GraphPair(graph_banks, graphs)
        graph_corpus.append(graph_pair)
            
    return graph_corpus


def _get_elem_tokens(doc_tree, tag, id):
    el = doc_tree.tagIdTable[tag][id]
    text = doc_tree.get_elem_text(el)
    return text.lower().split()


def _token_diff(source_tokens, target_tokens):
    # FXME: find faster solution
    fd = dict.fromkeys(source_tokens)
    td = dict.fromkeys(target_tokens)
    
    return ( len([ t for t in source_tokens if t not in td]) +
             len([t for t in target_tokens if t not in fd]))
