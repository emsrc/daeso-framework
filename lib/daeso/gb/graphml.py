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
parser for graphbanks in GraphML format
"""

__authors__ = "Erwin Marsi <e.marsi@gmail.com>"


from daeso.gb.parser import XmlGraphbankParser
from daeso.graph.daesograph import DaesoGraph
from daeso.exception import DaesoError


    
class GraphmlParser(XmlGraphbankParser):
    """
    Parser for graphbanks in GraphML format as defined at
    http://graphml.graphdrawing.org/specification.html
    
    The parser performs no validation and assumes validated input. It will
    break down ungracefully on invalid input, e.g. when required 'id'
    attributes are missing.
    
    However, it does check the following addditional requirements which are
    specific to Daeso:
    
       1. Each graph must have a 'tokens' attribute
       2. Each node must have a 'label' and a 'tokens' attribute
       
    When any of these requirements are violated, the parser will raise an
    AssertionError.
    """
    
    def __init__(self):
        XmlGraphbankParser.__init__(self)
        
        # <data> can appear as a child of <node> or <edge> so we need to keep
        # track of the context self._context is a stack of all open elements,
        # where self._context[-1] provides the parent element.
        self._context = []   
       
        
    def _start_element(self, tag, attrs):            
        self._context.append(tag)
        self._char_data_buf = ""
        
        if tag == "graphml":
            self._start_graphml(attrs)
        elif tag == "key":
            self._start_key(attrs)
        elif tag == "graph":
            self._start_graph(attrs)
        elif self._graph_wanted():
            if tag == "node":
                self._start_node(attrs)
            elif tag == "edge":
                self._start_edge(attrs)
            elif tag == "data":
                self._start_data(attrs)
                
                
    def _start_graphml(self, attrs): 
        # Table which holds the keys of the graph components as defined by the
        # <key> elements. The dict keys are the graph components (graph, node,
        # edge, or all) for which the key is defined (cf. "for" attribute).
        # The values are again tables which map a key id to yet another dict
        # mapping attribute properties (e.g. "attr.name") to attribute values
        # (e.g. "tokens").
        self._key_table = dict(graph={}, node={}, edge={}, all={})
        
        # The most recently added key. We need this to set an optional default
        # value as defined by a <default> element inside a <key> element.
        self._current_key = None
        
        # Value of the "key" attribute on the current <data> element
        self._data_key = None

        # The DaesoGraph currently under contruction, or None if the graph is
        # unwanted (cf. self._sparse and SparseGrapBank).
        self._graph = None
         
          
    def _start_key(self, attrs):
        key_for = attrs.get("for", "all")
        self._current_key = dict(name=attrs["attr.name"],
                                 type=attrs.get("attr.type", "string"))
        self._key_table[key_for][attrs["id"]] =  self._current_key
                
        
    def _start_graph(self, attrs):
        id = attrs.get("id")
        
        if not self._sparse or id in self._id2graph:
            self._graph = self._id2graph[id] = DaesoGraph(id=attrs["id"])
            self._comp_attrs = self._graph.graph
            self._set_defaults()
    
            
    def _start_node(self, attrs):
        n = attrs.get("id")
        # temporarily assign None to required arg label
        self._graph.add_node(n, label=None)
        self._comp_attrs = self._graph.node[n]
        self._set_defaults()
        self._node = n 
        
            
    def _start_edge(self, attrs):
        sn = attrs["source"]
        tn = attrs["target"]
        self._graph.add_edge(attrs["source"], attrs["target"])
        self._comp_attrs = self._graph[sn][tn]
        self._set_defaults()
            
            
    def _start_data(self, attrs):
        self._data_key = attrs["key"]
            
            
    def _graph_wanted(self):
        # graph will also return 0 if empty
        return self._graph is not None
    

    def _end_element(self, tag):
        if tag == "graph":
            self._end_graph()
        elif self._graph_wanted():
            if tag in "node":
                self._end_node()
            elif tag == "data":
                self._end_data()
            elif tag == "default":
                self._end_default()
                
        self._context.pop()
        
        
    def _end_graph(self):
        if self._graph_wanted():
            if self._graph.tokens is None:
                raise DaesoError("graph must have a 'tokens' attribute")
            
            # set the root node, defined as a graph attribute like 
            # <data key="root">n0</data>
            self._graph.root = self._graph.graph.get("graph")
            
            self._graph = None
            self._comp_attrs = None
        
        
    def _end_node(self):
        # TODO: make error msg more specific
        if not self._comp_attrs.get("label"):
            raise DaesoError("node must have a 'label' attribute")
        if not self._comp_attrs.get("tokens"):
            raise DaesoError("node must have a 'tokens' attribute")
        
        self._node = None
        self._comp_attrs = None
        
        
    def end_edge(self):
        self._comp_attrs = None
    
     
    def _end_data(self):
        attr_name = self._lookup_attr_name()
        attr_value = self._char_data_buf
            
        # the "tokens" key requires special treatment            
        if attr_name == "tokens" and self._context[-2] == "graph":
            self._graph.set_graph_token_string(attr_value)
        elif attr_name == "tokens" and self._context[-2] == "node":  
            self._graph.set_node_token_string(self._node, attr_value)
        else:
            # set attribute of Daeso graph, node or edge,
            # depending on the context
            self._comp_attrs[attr_name] = attr_value
            
        self._data_key = None
        
        
    def _end_default(self):
        # Set default value for the property defined by the parent <key>
        # element element.
        self._current_key["default"] = self._char_data_buf
        
 
    def _char_data(self, data):
        if self._graph_wanted():
            self._char_data_buf += data   
            
            
    def _lookup_attr_name(self):
        # lookup the name of the component attribute for the current key id in
        # self._data_key, which is the value of the "key" attribute on the
        # current <data> element

        # the tag of the parent of <data>
        key_for = self._context[-2]
        
        try:
            return self._key_table[key_for][self._data_key]["name"]
        except KeyError:
            pass
        
        # if the name is not in the key table specifically for this component,
        # then it _must_ be in the general property table
        try:
            return self._key_table["all"][self._data_key]["name"]
        except:
            raise DaesoError("encountered undefined key " + 
                             repr(self._data_key))
    
    
    def _set_defaults(self):
        key_for = self._context[-1]
        
        # set general default values for all, 
        # and specific default values for component
        for key in ( self._key_table["all"].values() +
                     self._key_table[key_for].values() ):
            attr_name = key["name"]
            
            try:
                attr_value = key["default"]
            except KeyError:
                # key has no default, thus skip
                continue
            
            # the "tokens" key requires special treatment            
            if attr_name == "tokens" and key_for == "graph":
                self._graph.set_graph_token_string(attr_value)
            elif attr_name == "tokens" and key_for == "node":  
                self._graph.set_node_token_string(self._node, attr_value)
            else:
                # set attribute of Daeso graph, node or edge,
                # depending on the context
                self._comp_attrs[attr_name] = attr_value

