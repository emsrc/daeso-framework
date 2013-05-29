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
pair of aligned source and target graphs
"""

__authors__ = "Erwin Marsi <e.marsi@gmail.com>"


# TODO:
# - check valid node id's hen creating alignments?

import copy
import xml.etree.cElementTree as et

from networkx import DiGraph, NetworkXError

from daeso.graph.daesograph import DaesoGraph
from daeso.gb.graphstub import GraphStub
from daeso.gb.graphbank import GraphBank
from daeso.pair import Pair
from daeso.utils.etree import equals



class GraphPairBase(object):
    """
    The GraphPairBase class represents a pair of source and target graphs obtained
    from a their respective source and target graphbanks.
    """
    
    # ------------------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------------------
    
    def __init__(self, banks, graphs, meta_data=None):
        """
        @param banks: a Pair of GraphBank instances

        @param graphs: a Pair of DaesoGraph or GraphStub instances

        @keyword meta_data: an ElementTree Element resulting from parsing
        <graph_meta_data> element
        """
        assert isinstance(banks.source, GraphBank)
        assert isinstance(banks.target, GraphBank)
        assert isinstance(graphs.source, DaesoGraph) or isinstance(graphs.source, GraphStub)
        assert isinstance(graphs.target, DaesoGraph) or isinstance(graphs.target, GraphStub)
        
        # Each GraphPairBase holds a reference to the GraphBanks containing the
        # source and target graphs of the pair. There are no other (strong)
        # references to GraphBank objects. Hence GraphBank objects are garbage
        # collected as soon as there are no GraphPairBase's referring to them.   
        self._banks = banks
        
        # Likewise, each GraphPairBase holds a reference to the source ad target
        # graphs. The graphbanks of type SparseGraphBank only hold weak
        # references to them. Therefore graphs are automatically destroyed if
        # they are no longer part of any graph pair.
        self._graphs = graphs
        self._meta_data = meta_data or et.Element("graph_meta_data")
        
        
    def __eq__(self, other):
        """
        self.__eq__(self, other) <==> self == other
        
        Test if two graphpairs are equal. This is true iff all of the
        following conditions are true:
        
        1. Their graphbanks are equal. This means that the *file paths* of
        self's and other's source (target) graphbank are equal (see
        GraphBank.__eq__ method).
        
        2. Their graphs are equal. This means the *id's* of self's and other's
        source (target) graph are the same. This is only valid under the
        assumption that both graphs are from the same graphbank and that each
        graph in a graphbank has a unique id.
        
        3. Their meta-data is equal. This means both are None or the Element
        objects are equal.
        """
        if isinstance(other, GraphPairBase):
            if self is other:
                return True
            else:
                return ( self._banks == other._banks and
                         self._graphs_equal(other) and
                         self._meta_data_equal(other) )
        
        
    def __deepcopy__(self, memo_dict):
        """
        Implements the copy protocol for copy.deepcopy(graph_pair), which only
        makes a deepcopy of the alignments (i.e. nodes and edges) and the
        meta_data, whereas the shallow copies are made of the graph banks and
        graphs.
        
        @return: new GraphPairBase object
        """
        return GraphPairBase(
            self._banks,
            self._graphs,
            meta_data = copy.deepcopy(self._meta_data, memo_dict))
    
    # Graphs
    
    def get_graphs(self):
        return self._graphs
    
    def get_source_graph(self):
        return self._graphs.source
    
    def get_target_graph(self):
        return self._graphs.target
    
    # Graphbanks
    
    def get_banks(self):
        return self._banks
    
    def get_source_bank(self):
        return self._banks.source
    
    def get_target_bank(self):
        return self._banks.target
        
    # Meta data    
    
    def set_meta_data(self, meta_data):
        assert meta_data.tag == "graph_meta_data"
        self._meta_data = meta_data
        
    def get_meta_data(self):
        return self._meta_data
    
    #-------------------------------------------------------------------------
    # Private methods 
    #-------------------------------------------------------------------------
        
    # Graphs
        
    def _graphs_equal(self, other):
        """
        test if self and other graphpair have the same source & target graphs
        
        Graphs are taken to be equal if they have the same id. This is only
        valid under the assumption that the two source (target) graphs come
        from the same source (target) graphbank, and that each graph in a
        graphbank has a unique id.
        """
        # and that is why there is no general DaesoGraph.__eq__ method,
        # because we cannot be sure that the graphs to be compared are from
        # the same graphbank...
        return ( (self._graphs.source.id == other._graphs.source.id) and
                 (self._graphs.target.id == other._graphs.target.id) )
        
    # Meta-data
    
    def _meta_data_equal(self, other):
        """
        test if self and other graphpair have the same meta-data (if any)
        """
        if self._meta_data is other._meta_data:
            # both None or same object 
            return True
        else: 
            return equals(self._meta_data, other._meta_data)
    

        
                
class GraphMapping(GraphPairBase, DiGraph):
    """
    The GraphMapping class represent a mapping between a pair of graphs where
    node alignment is unrestricted. That is, many-to-many node alignment is
    allowed; aka a bipartite graph in graph theory.
    """
    
    def __init__(self, banks, graphs, 
                 data=None, meta_data=None):
        """
        @param banks: a Pair of GraphBank instances

        @param graphs: a Pair of DaesoGraph or GraphStub instances
        
        @keyword data: an object to initialize the node alignment, e.g.
        another GraphPairBase instance or a list of edges

        @keyword meta_data: an ElementTree Element resulting from parsing
        <graph_meta_data> element
        """
        GraphPairBase.__init__(self, banks, graphs, meta_data)
        DiGraph.__init__(self, data=data)
        
   
    def __eq__(self, other):
        """
        self.__eq__(self, other) <==> self == other
        
        Test if two graphpairs are equal. This is true iff all of the
        following four conditions are true:
        
        1. Their graphbanks are equal. This means that the *file paths* of
        self's and other's source (target) graphbank are equal (see
        GraphBank.__eq__ method).
        
        2. Their graphs are equal. This means the *id's* of self's and other's
        source (target) graph are the same. This is only valid under the
        assumption that both graphs are from the same graphbank and that each
        graph in a graphbank has a unique id.
        
        3. Their alignments are equal, where every alignment is a triple of
        source node id, target node id and relation.
        
        4. Their meta-data is equal. This means both are None or the Element
        objects are equal.
        """
        if isinstance(other, self.__class__):
            if self is other:
                return True
            else:
                return ( GraphPairBase.__eq__(self, other) and 
                         self._alignments_equal(other) )
        
        
    def __deepcopy__(self, memo_dict):
        """
        Implements the copy protocol for copy.deepcopy(graph_pair), which only
        makes a deepcopy of the alignments (i.e. nodes and edges) and the
        meta_data, whereas the shallow copies are made of the graph banks and
        graphs.
        
        @return: new GraphPairBase instance
        """
        return self.__class__(
            self._banks,
            self._graphs,
            data=self,
            meta_data = copy.deepcopy(self._meta_data, memo_dict))
            
            
    def __len__(self):
        """
        Return number of alignments
        """
        return len(self.edges())
    
    
    def __str__(self):
        return "{0}(banks={1}, graphs={2}, data={3}, meta_data={4}))".format(
            self.__class__.__name__,
            self._banks,
            self._graphs,
            list.__str__(self),
            self._meta_data)

    
    def get_align(self, nodes):
        try:
            return self[nodes.source][nodes.target]["relation"]
        except KeyError:
            return None

        
    def add_align(self, nodes, relation):
        # non-existent nodes are automatically added
        self.add_edge(nodes.source, nodes.target, relation=relation)

        
    def del_align(self, nodes):
        self.remove_edge(nodes.source, nodes.target)
        # House keeping: if a node became unaligned, then remove it
        for n, degree in self.degree_iter(nodes):
            if degree == 0:
                try:
                    self.remove_node(n)  
                except NetworkXError:
                    # node already gone
                    pass
        # Note that even in the case of GraphMatching, we cannot automatically
        # delete the nodes, because soure and target nodes may have the same
        # name! 
                
        
    def alignments_iter(self, relations=None):
        if relations:
            return ( (Pair(source, target), data["relation"])
                     for source, target, data in self.edges_iter(data=True)
                     if data["relation"] in relations)
        else:
            return ( (Pair(source, target), data["relation"])
                     for source, target, data in self.edges_iter(data=True) )
        
        
    def alignments(self, relations=None):
        return list(self.alignments_iter(relations=relations))
    
    
    def roots_aligned(self):
        """
        test if root nodes (if defined) from source and target graphs are
        aligned
        """
        return self.has_edge(
            self._graphs.source.root ,
            self._graphs.source.root)
    
    
    def dump_alignments(self):
        for nodes, rel in self.alignments_iter():
            print '[{0}] {1!r} <=={2}==> [{3}] {4!r}\n'.format(
                nodes.source, 
                self._graphs.source.get_node_token_string(nodes.source),
                rel.upper(),
                nodes. target,
                self._graphs.target.get_node_token_string(nodes.target))
            
        print 40 * "-"
        
        
          
    
    def _alignments_equal(self, other):
        """
        test if self and other graphpair have the same alignments
        
        This means that every triple of source node id, target node id and
        relation in self must also occur in the other graphpair, and
        vice versa.
        """
        if len(self) == len(other):
            # note that the order of the edges may differ, hence no zip()
            for nodes, rel in self.alignments_iter():
                try:
                    if other[nodes.source][nodes.target]["relation"] != rel:
                        # other has different relation 
                        return None
                except KeyError:
                    # other lacks this edge
                    return
                
            return True
        


class GraphMatching(GraphMapping):
    """ 
    The GraphMatching class represents a matching between a pair of graphs
    where node alignment is a (partial) injective. That is, only one-to-one
    node alignments are allowed; aka a bipartite matching in graph theory.
    """
    
    def add_align(self, nodes, relation): 
        # free nodes of their alignments to any other nodes
        try:
            old_target = self.succ[nodes.source].iterkeys().next()
        except (KeyError, StopIteration):
            # source.node was unaligned
            pass
        else:
            if old_target != nodes.target:
                self.remove_edge(nodes.source, old_target)
                # remove old target node if it became unaligned
                if self.degree(old_target) == 0:
                    self.remove_node(old_target)
                
        try:
            old_source = self.pred[nodes.target].iterkeys().next()
        except (KeyError, StopIteration):
            # target.node was unaligned
            pass
        else:
            if old_source != nodes.source:
                self.remove_edge(old_source, nodes.target)
                # remove old source node if it became unaligned
                if self.degree(old_source) == 0:
                    self.remove_node(old_source)

        self.add_edge(nodes.source, nodes.target, relation=relation)
        
        
    def get_aligned_source_node(self, n):
        try:
            return self.predecessors_iter(n).next()  
        except (NetworkXError, StopIteration):
            pass
    
    
    def get_aligned_target_node(self, n):
        try:
            return self.successors_iter(n).next() 
        except (NetworkXError, StopIteration):
            pass
        
        
       
            
                

# support for GraphMapping in corpus, parser and generator classes is
# unfinished, so for the time being GraphPair is always GraphMatching

GraphPair = GraphMatching
    
    
    
    

    
                
                
        
        
        

    