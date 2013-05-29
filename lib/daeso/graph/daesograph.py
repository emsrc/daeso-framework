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
Definition of DaesoGraph class
"""

__authors__ = "Erwin Marsi <e.marsi@gmail.com>"


import string

from daeso.graph.ograph import ODiGraph

# TODO:
# * docstrings


class DaesoGraph(ODiGraph):
    
    def __init__(self, id=None, tokens=None, root=None):
        # blocked init by conversion from data for the time being
        ODiGraph.__init__(self)
        self.id = id
        self.tokens = tokens
        # root is an optional property fro rooted graphs
        self.root = root
        
        
    def get_graph_token_string(self):
        try:
            return " ".join(self.tokens)
        except TypeError:
            pass
    
    
    def set_graph_token_string(self, token_str):
        # strips whitespace
        self.tokens = token_str.split()
        
        
    def is_failed_parse(self):
        # not implemented yet except for alpino format
        return False

        
    #-------------------------------------------------------------------------
    # Node methods 
    #-------------------------------------------------------------------------
        
    def add_node(self, n, label, tokens=None, attr_dict=None, **attr):
        ODiGraph.add_node(self, n,
                          label=label,
                          tokens=tokens or [],
                          attr_dict=attr_dict, 
                          **attr)
        
        
    def add_nodes_from(self, *args, **kwargs):
        # Adding multiple nodes with the same label and tokens doesn't make a
        # lot of sense for our applications
        return NotImplemented
      
    
    def node_is_terminal(self, n, with_punct=True, with_empty=True):
        return ( not self[n] and
                 ( with_punct or not self.node_is_punct(n) ) and
                 ( with_empty or not self.node_is_empty(n) ) )    
    
    
    def node_is_non_terminal(self, n):
        return self[n]
    
    
    def terminals_iter(self, with_punct=True, with_empty=True):
        return ( node for node in self
                 if self.node_is_terminal(node, with_punct, with_empty) )
    
    
    def terminals(self, with_punct=True, with_empty=True):
        return list(self.terminals_iter(with_punct, with_empty))
    
    
    def non_terminals_iter(self):
        return ( node for node in self
                 if self.is_non_terminal(node) )
    
    
    def non_terminals(self):
        return list(self.non_terminals_iter())
    
    
    def node_is_empty(self, n):
        # tokens is either [] or None 
        return not self.node[n]["tokens"]
    
    
    def node_is_punct(self, n):
        # this assumes that a sequence of punctuation symbols is tokenized as
        # separate tokens
        tokens = self.node[n]["tokens"]
        
        if tokens:
            return all(t in string.punctuation
                       for t in tokens)
    
    
    def get_node_tokens(self, n):
        return self.node[n]["tokens"]
    
    
    def set_node_tokens(self, n, tokens):
        self.node[n]["tokens"] = tokens

    
    def get_node_token_string(self, n):
        try:
            return " ".join(self.node[n]["tokens"])
        except (TypeError, KeyError):
            # tokens is None
            pass
    
    
    def set_node_token_string(self, n, token_str):
        self.node[n]["tokens"] = token_str.split(" ")
        
        
    def terminal_yield(self, n=None, with_punct=True, with_empty=True):
        """
        return terminal yield of non-terminal node n, i.e., the list of
        terminal nodes dominated by non-terminal node n (in pre-order)
        """
        # should work for both trees and graphs
        queue = [n or self.root] # LIFO queue
        seen = {} # nodes seen      
        terminals = []  # list of terminal nodes in a DFS preorder
        
        while queue:
            v = queue[-1]
            
            if v not in seen:
                if self.node_is_terminal(v, with_punct=with_punct,
                                         with_empty=with_empty):
                    terminals.append(v)
                seen[v] = True

            done = True

            for w in self.successors_iter(v):
                if w not in seen:
                    queue.append(w)
                    done = False
                    break

            if done:
                queue.pop()
                
        return terminals
    
    #-----------------------------------------------------------------------------
    # Edge methods 
    #-----------------------------------------------------------------------------
            
    def add_edge(self, u, v, label=None, attr_dict=None, **attr):
        # nodes must already exist, because every node must have a label and
        # tokens
        for n in (u, v):
            if n not in self.succ:
                raise ValueError("graph has no node " + repr(n))
            
        # set up attribute dict
        if attr_dict is None:
            attr_dict=attr
        else:
            try:
                attr_dict.update(attr)
            except AttributeError:
                raise NetworkXError(\
                    "The attr_dict argument must be a dictionary.")
            
        attr_dict["label"] = label
            
        # add the edge
        datadict=self.adj[u].get(v,{})
        datadict.update(attr_dict)
        self.succ[u][v]=datadict
        self.pred[v][u]=datadict
        
        
    def add_edges_from(self, ebunch, label=None, attr_dict=None, **attr):
        # set up attribute dict
        if attr_dict is None:
            attr_dict=attr
        else:
            try:
                attr_dict.update(attr)
            except AttributeError:
                raise NetworkXError(\
                    "The attr_dict argument must be a dict.")
            
        attr_dict["label"] = label
            
        # process ebunch
        for e in ebunch:
            ne = len(e)
            if ne==3:
                u,v,dd = e
                assert hasattr(dd,"update")
            elif ne==2:
                u,v = e
                dd = {}
            else: 
                raise NetworkXError(\
                    "Edge tuple %s must be a 2-tuple or 3-tuple."%(e,))
                
            # nodes must already exist, because every node must have a label
            # and tokens
            for n in (u, v):
                if n not in self.succ:
                    raise ValueError("graph has no node " + repr(n))
            
            datadict=self.adj[u].get(v,{})
            datadict.update(attr_dict) 
            datadict.update(dd)
            self.succ[u][v] = datadict
            self.pred[v][u] = datadict  

        