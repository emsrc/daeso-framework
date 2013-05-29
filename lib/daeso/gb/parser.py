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
Abstract classes for graphbank parsers

Defines the interface that each graphbank parser is supposed to support, and
implements shared methods.
"""

__authors__ = "Erwin Marsi <e.marsi@gmail.com>"



from xml.parsers import expat

from daeso.exception import DaesoError

from daeso.gb.graphbank import GraphBank, SparseGraphBank

    
    

class XmlGraphbankParser(object):
    """
    Abstract class for expat-based parser of graphbanks in XML format
    """
    # This class is called while parsing a parallel graph corpus (from
    # PGCParser) or while aligning individual sentences in the  
    
    def __init__(self):
        self._parser = expat.ParserCreate()
        self._parser.StartElementHandler = self._start_element
        self._parser.EndElementHandler = self._end_element
        self._parser.CharacterDataHandler = self._char_data
        self._id2graph = None
        self._sparse = None
    
        
    def parse_string(self, data, id2graph=None, sparse=False):
        # supports incremental parsing
        self._id2graph = id2graph or {}
        self._sparse = sparse

        self._parser.Parse(data, 0)
        
        if self._sparse:
            self._check_for_unresolved_graphs()
            
        return self._id2graph

        
    def close(self):
        self._parser.Parse("", 1) # end of data
        del self._parser # get rid of circular references
        
        
    def parse_file(self, inf, id2graph=None, sparse=False):
        if not hasattr(inf, "read"):
            inf = open(inf)
            
        self._id2graph = id2graph
        self._sparse = sparse
        
        self._parser.ParseFile(inf)
        ##del self._parser 
        
        if self._sparse:
            self._check_for_unresolved_graphs(inf)
            
        return self._id2graph
    
            
    def _check_for_unresolved_graphs(self, inf):
        unresolved = [ '"{0}"'.format(id) 
                       for (id, graph) in self._id2graph.items() 
                       if graph is None ]
    
        if unresolved:
            msg = ( "graphs with the following id's were not found"
                    ' in graphbank file "{0}": {1}'.format(
                        inf.name, 
                        ", ".join(unresolved) ))
            raise DaesoError(msg)
        

    def _start_element(self, tag, attrs):
        NotImplemented

    
    def _end_element(self, tag):
        NotImplemented

    
    def _char_data(self, data):
        NotImplemented

    
    
