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
parallel graph corpus diff and analysis
"""

__authors__ = "Erwin Marsi <e.marsi@gmail.com>"


# TODO 
# - a number of things here might be Alpino specific

from sys import stdout

from daeso.pgc.corpus import ParallelGraphCorpus
from daeso.utils.report import header


def pgc_diff(corpus1, corpus2, 
             corpus_name1="Corpus1", corpus_name2="Corpus2", 
             annot1="Annot1", annot2="Annot2", 
             words_only=False,
             show_comments=False,
             show_ident=False,
             relations=None,
             out=stdout):
    """
    reports the differences (and optionally the similarities) between 
    the labeled alignments from two parallel graph corpora
    """
    assert len(corpus1) == len(corpus2)
    
    if not relations:
        relations = corpus1.get_relations()
    
    # counter for numbering the alignments when printing;
    # may be less than the actual number of alignments when identical alignments
    # are not printed (cf. show_ident option)
    align_count = 0
    
    # counter for numbering the graph pairs when printing
    pair_count = 0
    
    header("%s corpus: %s\n%s corpus: %s" % (annot1, corpus_name1, annot2,
                                             corpus_name2), width=120, char="#")
    
    for graph_pair1, graph_pair2 in zip(corpus1, corpus2):
        # assume that the corpora have the same graph pairs in the same order,
        # so the only difference is in the aligned nodes
        assert graph_pair1._banks == graph_pair2._banks
        assert graph_pair1._graphs_equal(graph_pair2)
        
        pair_count += 1
        ident = []
        rel_diff = [] 
        uniq1 = []
        uniq2 = []
        # recall that graphs are identical
        graphs = graph_pair1.get_graphs()
        
        for nodes, rel1 in graph_pair1.alignments_iter(relations=relations):
            if ( words_only and
                 graphs.source.node_node_is_non_terminal(nodes.source) and
                 graphs.target.node_is_non_terminal(nodes.target) ):
                continue
            
            rel2 = graph_pair2.get_align(nodes)
                        
            if not rel2:
                uniq1.append(nodes)
            elif rel1 == rel2:
                ident.append(nodes)
            else:                        
                rel_diff.append(nodes)
            
        for nodes, rel2 in graph_pair2.alignments_iter(relations=relations):
            if ( words_only and
                 ( graphs.source.node_is_terminal(nodes.source) or
                   graphs.target.node_is_terminal(nodes.target) )):
                continue
            
            if not graph_pair1.get_align(nodes):
                uniq2.append(nodes)
                    
        
        #if not ( ident and rel_diff and uniq1 and uniq2 and show_comments ):
        #    continue
            
        header("Graph pair %d" % pair_count, width=120, char="=")
        
        print >>out, graphs.source.get_graph_token_string().encode("utf-8"), "\n"
        print >>out, graphs.target.get_graph_token_string().encode("utf-8"), "\n"
        
        if show_comments:
            print_comments(graph_pair1, annot1, out)
            print_comments(graph_pair2, annot2, out)
            
        if show_ident:
            ident.sort(cmp=cmp_nodes)
            align_count = print_alignments(align_count, "Identical",
                                           graph_pair1, graph_pair2, graphs, ident, out)
        
        rel_diff.sort(cmp=cmp_nodes)
        align_count = print_alignments(align_count, "Relation different",
                                       graph_pair1, graph_pair2, graphs, rel_diff, out)
        
        uniq1.sort(cmp=cmp_nodes)
        align_count = print_alignments(align_count, annot1 + " only",
                                       graph_pair1, graph_pair2, graphs, uniq1, out)
        
        uniq2.sort(cmp=cmp_nodes)
        align_count = print_alignments(align_count, annot2 + " only",
                                       graph_pair1, graph_pair2, graphs, uniq2, out)
        
        
def cmp_nodes(nodes1, nodes2):
    return cmp(int(nodes1.source), int(nodes2.source))


def print_alignments(align_count, title, graph_pair1, graph_pair2, graphs,
                     nodes_list, out=stdout):
    if nodes_list:
        header(title, out, char="-")
        
        for nodes in nodes_list:        
            align_count += 1
            rel1 = str(graph_pair1.get_align(nodes))
            rel2 = str(graph_pair2.get_align(nodes))
            
            # tricky because of implicit coercions, 
            # see "Formatting Markers" http://www.python.org/dev/peps/pep-0100/
            print >>out, "#%d:" % align_count 
            s = '(%s) %s [%s:%s]: "%s"' % (                
                nodes.source,
                graphs.source.node[nodes.source]["label"].encode("utf-8"),
                graphs.source.node[nodes.source]["begin"],
                graphs.source.node[nodes.source]["end"],
                graphs.source.get_node_token_string(nodes.source))
            print >>out, s.encode("utf-8")
            print >>out, "<<<", rel1.upper(), "/", rel2.upper(), ">>>"
            s = '(%s) %s [%s:%s]: "%s"\n' % (
                nodes.target,
                graphs.target.node[nodes.target]["label"],
                graphs.target.node[nodes.target]["begin"],
                graphs.target.node[nodes.target]["end"],
                graphs.target.get_node_token_string(nodes.target))
            print >>out, s.encode("utf-8")
            
    return align_count
        


def print_comments(graph_pair, annot, out, encoding="utf-8"):
    try:
        comment = graph_pair.get_meta_data().find("comment").text
    except AttributeError:
        return
    
    if comment.strip():
        header("Comments by " + annot, out, char="-")
        print >>out, comment.encode(encoding), "\n"
