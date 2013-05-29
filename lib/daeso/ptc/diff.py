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
differences in text alignment between parallel text corpora
"""

__authors__ = "Erwin Marsi <e.marsi@gmail.com>"


from daeso.ptc.document import HitaextDoc


# TODO:
# - unittests
# - code is not very efficient, but who cares?


def print_diff(true_corpus, pred_corpus, tag, encoding="utf-8"):
    """
    print differences in text alignment w.r.t. tag between two parallel text
    corpora
    
    @param true_corpus: parallel text corpus containing true alignments
    
    @param pred_corpus: parallel text corpus containing predicted alignments
    
    @param tag: only alignments involving this tag are considered
    
    @keyword encoding: character encoding of printed output
    """
    true_corpus, true_from_tree, true_to_tree = read_corpus(true_corpus)
    pred_corpus, pred_from_tree, pred_to_tree = read_corpus(pred_corpus)
    count = 0
    
    for true_from_elem, pred_from_elem in zip(
        true_from_tree.tagCountTable[tag],
        pred_from_tree.tagCountTable[tag]):
        
        for true_to_elem in true_from_elem.get("_alignments"):

            for pred_to_elem in pred_from_elem.get("_alignments"):
                if true_to_elem.get("id") == pred_to_elem.get("id"):
                    # same alignment
                    break
            else:
                count += 1
                print "#%d true only (%s, %s):" % (
                    count,
                    true_from_elem.get("id"),
                    true_to_elem.get("id"))
                print true_from_tree.get_elem_text(true_from_elem).encode(encoding)
                print true_to_tree.get_elem_text(true_to_elem).encode(encoding)
                print
                
        for pred_to_elem in pred_from_elem.get("_alignments"):

            for true_to_elem in true_from_elem.get("_alignments"):
                if true_to_elem.get("id") == pred_to_elem.get("id"):
                    # same alignment
                    break
            else:
                count += 1
                print "#%d predicted only (%s, %s)" % (
                    count,
                    pred_from_elem.get("id"),
                    pred_to_elem.get("id"))
                print pred_from_tree.get_elem_text(pred_from_elem).encode(encoding)
                print pred_to_tree.get_elem_text(pred_to_elem).encode(encoding)
                print
                
    
    
def read_corpus(corpus): 
    if not isinstance(corpus, HitaextDoc):
        corpus = HitaextDoc(file=corpus)
        
    from_tree = corpus.get_doc_tree("from")
    from_tree.update()
    to_tree = corpus.get_doc_tree("to")
    to_tree.update()
    corpus.inject_alignments(from_tree, to_tree)  
    
    return corpus, from_tree, to_tree
        
          
    
        
    
    