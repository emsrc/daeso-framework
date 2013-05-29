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
GraphStub class
"""

__authors__ = "Erwin Marsi <e.marsi@gmail.com>"



from daeso.graph.daesograph import DaesoGraph


class GraphStub(object):
    """
    A GraphStub is a stub for a Daeso graph instance. Its only content is the
    graph's id. It used in the PGCParser class and SparseGraphBank class to
    prevent parsing unaligned graphs (creating sparse graph bank) or to avoid
    parsing alltogether (reading a corpus without actually opening graph
    banks). See those classes for details.
    
    A GraphStub object maintains a list of GraphPair objects, called "clients"
    (in self.clients), which use the stub as their source and/or target graph.
    This enables us to replace the stub by a real graph later on, using the
    method "replace_stub".
    
    GraphStub object are not supposed to be reused.
    """
    def __init__(self, id):
        """
        Create a new GraphStub object
        
        @param id: graph id
        
        @return: GraphStub object
        """
        assert id
        self.id = id
        # clients is a list of GraphPair objects which use this graph stub as
        # their source and/or target graph
        self.clients = []
        
        
    def add_client(self, graph_pair):
        """
        Register a graph pair as a client of this graph stub
        
        @param graph_pair: GraphPair object
        """
        # cannot use assert isinstance(graph_pair, GraphPair)
        # becausse importing GraphPair causes a cyclic import problem
        assert graph_pair._graphs.source  and graph_pair._graphs.target
        self.clients.append(graph_pair)
        
        
    def replace_stub(self, graph):
        """
        Replace the reference to this graph stub by a reference to a full
        graph in all the clients.
        
        @param graph: DaesoGraph instance
        """
        assert self.clients
        assert isinstance(graph, DaesoGraph)
        
        # In each client graph pair,
        # replace the graph stub by a full blown graph
        for graph_pair in self.clients:
            # The logic below fails if source and target graph are identical,
            # which should not occur anyway
            assert not graph_pair._graphs.source is graph_pair._graphs.target
            
            if graph_pair._graphs.source is self:
                graph_pair._graphs.source = graph
            elif graph_pair._graphs.target is self:
                graph_pair._graphs.target = graph
            else:
                raise ValueError( "{0} is no client of {}".format(
                    graph_pair, self))
        
        # If any of the graph pairs is deleted while for some reason the graph
        # stub is still alive, we don't want the stub to keep the graph alive
        del self.clients
        
                
