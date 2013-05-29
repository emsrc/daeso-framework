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
Read-only graphbank
"""

__authors__ = "Erwin Marsi <e.marsi@gmail.com>"


import os
import weakref

from daeso.gb.graphstub import GraphStub

import daeso.gb.register 



class GraphBank(object):
    """
    A read-only graph bank which maps graph id's to graph objects
    """
    
    def __init__(self, file_path, format):
        """
        Create an empty GraphBank object
        
        @param file_path: path to the graphbank file
        
        @param format: format of the graphs in the graphbank
        
        The file is not opened and the graphs are not loaded until the "load"
        method is called.
        """
        # This enables one to create an empty graphbank, that is, with
        # file_path and format info obtained from the pgc xml, but without
        # actually reading and parsing the graphbank file. This also enforces
        # the requirement from the pgc that every graphbank must have an
        # absolute file path and a graph format.
        self._set_file_path(file_path)
        self._format = format
        self._loaded = False
        # The mapping from graph id's to graphs
        self._id2graph = {}
        
        
    def __str__(self):
        return '{0}(\n\tfile_path="{1}",\n\tformat="{2}\n\t_id2graph={3}")'.format( 
            self.__class__.__name__,
            self._file_path,
            self._format,
            self._id2graph)
        
        
    def __len__(self):
        """
        Return number of graphs in graphbank
        """
        return len(self._id2graph)
        
        
    def __eq__(self, other):
        """
        self.__eq__(other) <==> self == other
        
        Two graphbanks are equal if and only if their file paths point to the
        same file. Unless the paths are string identical, the OS is invoked
        the check if the paths point to the same existing file.
        
        (Two graphbanks in different files may in fact be equal, but for
        reasons of simplicity and efficiency no attempt is made to analyse
        their contents.)
        """
        return ( self._file_path == other._file_path or
                 os.path.samefile(self._file_path, other._file_path))
    
    
    def __ne__(self, other):
        """
        self.__ne__(other) <==> self != other

        Two graphbanks are assumed to be different if their file paths point
        to the same file.
        """
        return not self.__eq__(other)
    
    
    def __iter__(self):
        return (graph for graph in self._id2graph.itervalues())
        

    def get_format(self):
        """
        Return format of graphs in graphbank
        """
        return self._format
    
    
    def get_file_path(self):
        """
        Return absolute path to graphbank file
        """
        return self._file_path
    
    
    def _set_file_path(self, file_path):
        """
        Change graphbank file path
        
        @param file_path: path to the graphbank file

        Warning: use with care! Changing graphbank file paths may result in
        ill-formed parallel graph corpora.
        """
        # Two graphbanks are considered equal iff their file paths point to
        # the same file. For this to work, the file path must be absolute.
        
        #if not os.path.isabs(file_path):
        #    raise ValueError("file_path must be an absolute path")
        
        self._file_path = os.path.realpath(file_path)
        
        
    def get_graph(self, graph_id):
        """
        Return graph object with given id
        
        Raises KeyError if graph_id does not exists 
        """
        return self._id2graph[graph_id]
     
    
    def load(self):
        """
        Open graphbank file and load all graphs
        """
        assert not self._loaded
        parser = self._get_parser(self._format)
        parser.parse_file(self._file_path, self._id2graph,
                          sparse=False)
        self._loaded = True 
            
    
    def _get_parser(self, format):
        try:
            parser_module_name, parser_class_name = getattr(daeso.gb.register, 
                                                            format.lower())
        except KeyError:
            # TODO: use own error class
            AssertionError("no parser available for graphbank in '%s' format" % format)
            
        try:
            parser_module = __import__(parser_module_name, 
                                       fromlist=[parser_class_name])
            parser_class = getattr(parser_module, parser_class_name)
        except (ImportError, AttributeError):
            raise AssertionError("import of parser class %s from module %s failed" % 
                                 (parser_class_name, parser_module_name))
        
        return parser_class()
    
    
    
    


class SparseGraphBank(GraphBank):
    
    def __init__(self, file_path, format):
        GraphBank.__init__(self, file_path, format)
        # A weak reference from graph id's to graphs. If no other strong
        # reference to the Graph object remains, it will be automatically
        # removed from the dictionary. That is, if there are no Graphpair
        # objects holding a reference to the graph left, the graph will be
        # garbage collected.
        self._id2graph = weakref.WeakValueDictionary()
        
        
    def get_graph_stub(self, graph_id):
        # The caller should make sure it holds a strong reference to the
        # returned graph stub, otherwise it will be garbage collected!!!
        assert not self._loaded
        return self._id2graph.setdefault(graph_id, GraphStub(graph_id))
        
        
    def load(self):
        assert not self._loaded
        
        full_graphs = dict.fromkeys(self._id2graph)
            
        parser = self._get_parser(self._format)
        parser.parse_file(self._file_path, full_graphs,
                          sparse=True)
        
        for graph_id, graph_stub in self._id2graph.items():
            graph_full = full_graphs[graph_id]
            # replace stub in graph_pair
            graph_stub.replace_stub(graph_full)
            # and replace stub in weak dict
            self._id2graph[graph_id] = graph_full
        
        self._loaded = True 
    
    

# this funny statement is to trick py2exe into including these modules
# in the list of dependencies when building an exe
if False:
    from daeso.gb import alpino, graphml
        
    
    
    