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
parallel graph corpus class, and parser/generator classes for reading/writing
a corpus in xml format
"""

__authors__ = "Erwin Marsi <e.marsi@gmail.com>"


# Although these classes are quite large, keeping them in separate files
# turned out to be hard, because of circular import errors.

# TODO:
# * support for GraphMapping & GraphMatching


import copy
import cStringIO
import os
import sys
import xml.etree.cElementTree as et
import warnings

from daeso.pgc.graphpair import GraphPair
from daeso.gb.graphbank import GraphBank, SparseGraphBank
from daeso.exception import DaesoWarning, DaesoError
from daeso.pair import Pair
from daeso.utils.etree import write, equals


# global flags for graph loading
LOAD_ALL, LOAD_SPARSE, LOAD_NONE = 1, 2, 3




class ParallelGraphCorpus(list):
    """
    The ParallelGraphCorpus class represents a corpus of parallel graphs as a
    list of GraphPair objects.  A corpus can be read from and
    written to a custom XML format.
    
    Graph pairs and graphbanks
    ---------------------------
    
    Each GraphPair consist of a source and a target graph pair, which are
    defined in separate graphbanks, plus a number of labeled node alignments.
    See the GraphPair class for details. Although the corpus file specifies
    the file paths for all the graphbanks providing source and target graphs,
    once a corpus file is read (parsed and processed), a ParallelGraphCorpus
    object does not contain any direct references to either graphs or graph
    banks. All references to graphs and graphbanks are kept in GraphPair
    objects. This avoids the need for a complicated administration which keeps
    track of which graphbanks are added (or have become redundant) after
    inserting or deleting graphs pairs. Moreover, graphbanks which are no
    longer in use by any graph pair are automatically garbage collected. Only
    when the corpus needs to be written to file, all graphbanks referred to
    are collected, and their file paths are included in the ouput.
    
    By default reading a corpus from file will automatically retrieve the
    required graphs from the graphbanks (cf. SparseTreeBank class). However,
    a corpus can be opened without really opening and parsing the graphbanks,
    which saves memory and time (cf. GraphStub class). This is usefull in
    cases where access to graph nodes is not required.
    
    Relations
    ---------
    
    The node alignments of pair of graphs are labeled according to a list of
    of alignment relations (stored in self._relations). The list of possible
    relations is fixed for all graph pairs in a corpus. It is initialized only
    when creating/reading a corpus, and must not be changed afterwards.
    
    Meta-data
    ---------
    
    The XML file format reserves a particular node in the XML tree (i.e
    <corpus_meta_data>) for arbitrary user-defined meta-data regarding the
    corpus. This information is stored as Element object (cf.
    xml.etree.Elementree).
    

    """
    
    def __init__(self, graph_pairs=None, relations=None, meta_data=None,
                 inf=None, graph_loading=LOAD_SPARSE):
        """
        Create a new ParallelGraphCorpus object
        
        @keyword graph_pairs: an iterable containing GraphPair instances, e.g.
        a list or another corpus
        
        @keyword relations: a list of alignment relations as used to
        label the node alignments in the Graphpair objects
        
        @keyword meta_data: an Element object (cf. xml.etree.ElementTree)
        containing arbitrary user-defined meta-data regarding the corpus
        
        @keyword inf: a inf object or name to read from; if supplied the
        corpus will be opened in sparse graph loading mode
        
        @keyword graph_loading: a flag defined on the PGCParser class 
            indicating how to load graphs:
            (1) LOAD_ALL: load all graphs from the graphbanks 
                involved
            (2) LOAD_SPARSE: read only those graphs  actually 
                aligned in the corpus
            (3) LOAD_NONE: do not read any graphs but use 
                graph stubs instead
    
        @return: ParallelGraphCorpus object
        """
        # FIXME: hmm, this allows adding non-graphpairs...
        list.__init__(self, graph_pairs or [])
        self.set_relations(relations)
        self._meta_data = meta_data
        self._graph_loading = None
        if inf: self.read(inf, graph_loading)
        
    
    def __add__(self, other):
        """
        corpus.__add__(other) <==> corpus + other
        
        If the two corpora share graphbanks, call "purge" afterwards to free
        memory of duplicate graphbanks.
        """
        self._check_compatibility(other)
            
        return ParallelGraphCorpus(
             graph_pairs=list.__add__(self, other), 
             relations=self._relations, 
             meta_data=self._meta_data)

    
    def __contains__(self, graph_pair):
        """
        corpus.__contains__(graph_pair) <==> graph_pair in corpus
        """
        return list.__contains__(self, graph_pair)

    
    def __deepcopy__(self, memo_dict):
        """
        Implements the copy protocol for copy.deepcopy(corpus), which makes a
        deepcopy of the graph pairs, the relations and the meta_data. Notice
        however that the deepcopy of the graph pairs does not include
        deepcopies of the graphbanks and graphs. graphs.
        
        @return: a new ParallelGraphCorpus object
        """
        return ParallelGraphCorpus(
            [copy.deepcopy(gp, memo_dict) for gp in self],
            self._relations[:],
            copy.deepcopy(self._meta_data, memo_dict))
    
    
    def __delitem__(self, index):
        """
        corpus.__delitem__(index) <==> del corpus[index]
        
        Index can be a an int or a slice object.
        """
        # redundant graphbanks are automatically garbage collected
        list.__delitem__(self, index)
      
        
    def __delslice__(self, i, j):
        """
        corpus.__delslice__(i, j) <==> del corpus[i:j]
        """
        # Although __delslice__ is deprecated, it is still provided by
        # built-in types like list. Hence we must override it. Notice though
        # that extended slicing, as in del corpus[i:j:k], calls __delitem__
        # with a slice object as index. We can therefore redirect the call to
        # __detitem__ by turning it into an extended slicing case. See Python
        # docs for an explanation of the max() parts.
        del self[max(0, i):max(0, j):]
        
        
    def __eq__(self, other):
        """
        corpus.__eq__(other) <==> corpus == other
        
        Test if two corpora are equal. This is true iff all of the
        following three conditions are true:
        
        1. Their alignment relations are equal.
        
        2. Their meta-data is equal. This means both are None or the Element
        objects are equal.
        
        3. Their graph pairs are equals (see GraphMapping.__eq__ ), where
        order is significant.
        """
        if self is other:
            return True
        elif isinstance(other, ParallelGraphCorpus):
            # For each pair of graph pairs, this will lead to a call to
            # GraphPair.__eq__ The order of the graph pairs in the corpus is
            # signficant.
            return ( self._relations == other._relations and
                     self._meta_data_equal(other) and
                     list.__eq__(self, other))

        
    def __ge__(self, other):
        """
        corpus.__ge__(other) <==> corpus >= other
        
        Ignores relations and meta-data.
        """
        return list.__ge__(self, other)

    
    def __getitem__(self, index):
        """
        corpus.__getitem__(index) <==> corpus[index]
        
        If index is an int object, then a GraphPair is returned.
        If index is a slice object, then a ParallelGraphCorpus object 
        is returned.
        """
        # catch slices to prevent that a list object is returned
        if isinstance(index, slice):
            return ParallelGraphCorpus(
                graph_pairs = list.__getitem__(self, index),
                relations = self._relations,
                meta_data = self._meta_data)
        else:
            # leave it to list to catch type errors
            return list.__getitem__(self, index)
 
 
    def __getslice__(self, i, j):
        """
        corpus.__getslice__(i, j) <==> corpus[i:j]
        
        @param i: start index
        
        @param j: end index
        
        @return: a new ParallelGraphInstance object which is a shallow copy of
        the corpus containing graph pairs in the given range
        
        Graph pairs (and thus indirectly graphbanks), alignment relations and
        corpus meta-data are still shared with the original. 
        """
        # Although __getslice__ is deprecated, it is still provided by
        # built-in types like list. Hence we must override it, or else
        # corpus[i:j] would return a list object. Notice though that extended
        # slicing, as in corpus[i:j:k], calls __getitem__ with a slice object
        # as index. We can therefore redirect the call to __getitem__ by
        # turning it into an extended slicing case. See Python docs for an
        # explanation of the max() parts.
        return self[max(0, i):max(0, j):]
    
      
    def __gt__(self, other):
        """
        corpus.__gt__(other) <==> corpus > other
        
        Ignores relations and meta-data.
        """
        return list.__gt__(self, other)

        
    def __iadd__(self, other):
        """
        corpus.__iadd__(other) <==> corpus += other
        
        If the two corpora share graphbanks, call "purge" afterwards to free
        memory of duplicate graphbanks.
        """
        self._check_compatibility(other)
        return list.__iadd__(self, other)
        

    def __imul__(self, n):
        """
        corpus.__imul__(n) <==> corpus *= n
        """
        return list.__imul__(self, n)
        

    def __iter__(self):
        """
        corpus.__iter__() <==> iter(corpus)
        
        Returns an iterator over the graph pairs in the corpus.
        """
        return list.__iter__(self)

    
    def __le__(self, other):
        """
        corpus.__le__(other) <==> corpus <= other
        
        Ignores relations and meta-data.
        """
        return list.__le__(self, other)

      
    def __len__(self):
        """
        corpus.__len__() <==> len(corpus)
        """
        return list.__len__(self)
      

    def __lt__(self, other):
        """
        corpus.__lt__(other) <==> corpus < other
        
        Ignores relations and meta-data.
        """
        return list.__lt__(self, other)

      
    def __mul__(self, n):
        """
        corpus.__mul__(n) <==> corpus * n
        """
        # shallow copies
        return ParallelGraphCorpus(
            graph_pairs=list.__mul__(self, n),
            relations=self._relations, 
            meta_data=self._meta_data)
      
    
    def __ne__(self, other):
        """
        corpus.__ne__(other) <==> corpsu != other
        """
        return not self.__eq__(self, other)
    
      
    def __repr__(self):
        """
        corpus.__repr__() <==> repr(corpus)
        """
        return ( "ParallelGraphCorpus(" +
                 "graph_pairs=" + list.__repr__(self) + ", "
                 "relations=" + repr(self._relations) + ", "
                 "meta_data=" + repr(self._meta_data) + ")" )
                 
      
    def __reversed__(self):
        """
        corpus.__reversed__() -- return a reverse iterator over the corpus
        """
        return list.__reversed__(self)
    
    
    def __rmul__(self, n):
        """
        corpus.__rmul__(n) <==> n * corpus
        """
        return self.__mul__()
         
    
    def __setitem__(self, index, value):
        """
        corpus.__setitem__(index, value) <==> x[index] = value
        
        If index is an int object, then value must be a GraphPair instance. 
        If index is a slice object, then value must be a ParallelGraphCorpus
        instance
        
        If the corpus and the new value share graphbanks, call "purge"
        afterwards to free memory of duplicate graphbanks.
        """
        # Redundant graphbanks are automatically garbage collected
        # TODO: check if relations are comptabible? 
        #
        if isinstance(index, slice):   
            self._check_compatibility(value)
        elif not isinstance(value, GraphPair):
            raise TypeError("only GraphPair instances are allowed") 
            
        list.__setitem__(self, index, value)
        
    
    def __setslice__(self, i, j, other):
        """
        corpus.__setslice__(i, j, other) <==> corpus[i:j] = other
        
        If the two corpora share graphbanks, call "purge" afterwards to free
        memory of duplicate graphbanks.
        """
        # Although __setslice__ is deprecated, it is still provided by
        # built-in types like list. Hence we must override it. Notice though
        # that extended slicing, as in corpus[i:j:k] = ..., calls __setitem__
        # with a slice object as index. We can therefore redirect the call to
        # __setitem__ by turning it into an extended slicing case. See Python
        # docs for an explanation of the max() parts.
        self[max(0, i):max(0, j):] = other            

    
    def __sizeof__(self):
        """
        corpus.__sizeof__() -- size of corpus in memory, in bytes
        """
        return NotImplemented
    
    
    def __str__(self):
        strbuf = cStringIO.StringIO() 
        self.write(outf=strbuf, pprint=True)
        return strbuf.getvalue()

        
    def set_relations(self, relations=None):
        self._relations = relations or []
        self._relations.sort()

    
    def append(self, graph_pair):
        """
        corpus.append(graph_pair) -- append graph_pair to end
        
        If the corpus and the graph pair share graphbanks, call "purge"
        afterwards to free memory of duplicate graphbanks.
        """
        # TODO: check if relations are comptabible? 
        if not isinstance(graph_pair, GraphPair):
            raise TypeError("can only append GraphPair instances")
        
        list.append(self, graph_pair)
        
        
    def clear(self):
        """
        corpus.clear() <==> del corpus[:]
        
        Clear corpus from all graph pairs
        """
        del self[:]
        
        
    def count(self, graph_pair):
        """
        corpus.count(graph_pair) -> integer -- 
        return number of occurrences of graph_pair
        
        This should always return 0 or 1.
        """
        return list.count(self, graph_pair)
    
    
    def extend(self, iterable):
        """
        corpus.extend(iterable)
        extend corpus by appending graph pairs from the iterable
            
        If the two corpora share graphbanks, call "purge" afterwards to free
        memory of duplicate graphbanks.
        
        Warning: to improve efficiency, it is not checked if the iterable
        really generates GraphPair object!
        """
        # this is different from __iadd__, which requires a corpus as argument
        list.extend(self, iterable)
        

    def get_meta_data(self):
        return self._meta_data
    
        
    def get_relations(self):
        return self._relations
    
    
    def index(self, graph_pair):
        """
        corpus.index(graph_pair, [start, [stop]]) -> integer -- 
        return first index of graph_pair.
        Raises ValueError if the graph_pair is not present.
        """
        return list.index(self, graph_pair)
    
          
    def insert(self, graph_pair):
        """
        corpus.insert(index, graph_pair) -- insert graph_pair before index
        
        If the corpus and the graph pair share graphbanks, call "purge"
        afterwards to free memory of duplicate graphbanks.
        """
        # TODO: check if relations are comptabible? 
        if not isinstance(graph_pair, GraphPair):
            raise TypeError("only GraphPair instances are allowed")
        
        list.insert(self, i, graph_pair)
    
    
    def read(self, inf, graph_loading=LOAD_SPARSE, relax_gb_paths=False):
        """
        Read parallel graph corpus in XML format from file
        
        @param inf: file object or file name
        
        @keyword graph_loading: a flag defined on the PGCParser class 
            indicating how to load graphs:
            (1) LOAD_ALL: load all graphs from the graphbanks 
                involved
            (2) LOAD_SPARSE: read only those graphs  actually 
                aligned in the corpus
            (3) LOAD_NONE: do not read any graphs but use 
                graph stubs instead
                
        @keyword relax_gb_paths: if true, graphbank files may also be present
        in the same direcory as the corpus file instead of the location
        specified in the <file> element; this allows packing corpus and
        graphbank files for annotation at another site without changing the
        original graphbank file paths
        """
        assert graph_loading in (LOAD_ALL, 
                                 LOAD_SPARSE,
                                 LOAD_NONE)
        self._graph_loading = graph_loading
        parser = PGCParser()
        parser.parse(inf, self, graph_loading=graph_loading,
                     relax_gb_paths=relax_gb_paths)

          
    def pop(self, index=None):
        """
        corpus.pop([index]) -> GraphPair -- 
        remove and return graph pair at index (default last)

        Raises IndexError if corpus is empty or index is out of range.
        """
        # redundant graphbanks are automatically garbage collected
        list.pop(self, index)
    
    
    def purge(self, graph_pair=None):
        """
        Purge the corpus of duplicate graphbanks held in memory, which may
        arise after modifications such as adding graph pairs or concatenating
        corpora. Notice however that the released duplicate graphbanks will
        not be garbage collected as long as the original objects from which
        they were derived (i.e. GraphPair, GraphBank or ParallelGraphCorpus
        instances) are still alive.
        
        @keyword graph_pair: limit purge to this particular graph pair
        """
        # a table for remapping old graphbanks to new graphbanks
        # (difference between source and target banks is irelevant)
        old2new = {}
        
        if graph_pair:
            to_purge = [graph_pair]
        else:
            to_purge = self
        
        for graph_pair in to_purge:
            new_banks = []
            
            for old_gb in graph_pair._banks:
                try:
                    new_gb = old2new[old_gb]
                except KeyError:
                    # see if the old bank matches any of the known new banks
                    for new_gb in old2new.itervalues():
                        # recall that equality is implemented as os.path.samepath
                        if old_gb == new_gb:
                            # match found
                            old2new[old_gb] = new_gb
                            break
                    else:
                        # old bank has not been seen yet,
                        # so we add it by mapping it onto itself
                        new_gb = old2new[old_gb] = old_gb
                        
                new_banks.append(new_gb)
                
            # Pair is a named tuple, so we cannot reassign its fields but have
            # to create a new one
            graph_pair._banks = Pair(*new_banks)

          
    def remove(self, graph_pair):
        """
        corpus.remove(graph_pair) -- remove first occurrence of graph_pair

        Raises ValueError if the graph pair is not present.        
        """
        # notice that dependencies on graphbanks are resolved automatically
        list.remove(self, graph_pair)


    def reverse(self):
        """
        corpus.reverse() -- reverse *IN PLACE*
        """
        list.reverse(self)

    
    def set_meta_data(self, meta_data):
        self._meta_data = meta_data

        
    def sort(self, cmp=None, key=None, reverse=False):
        """
        corpus.sort(cmp=None, key=None, reverse=False)
        stable sort *IN PLACE*; 
        cmp(x, y) -> -1, 0, 1
        """
        list.sort(self, cmp, key, reverse)
        
        
    def write(self, outf=sys.stdout, encoding="utf-8", abs_path=False,
              pprint=False):
        """
        Write parallel graph corpus in XML format to file
        
        @keyword outf: output filename or file object
        
        @keyword encoding: character encoding
        
        @keyword abs_path: use absolute graphbank file paths; the default is
        to use graphbank file paths which are relative to the corpus file path
        
        @keyword pprint: pretty print (indent) xml output
        """
        generator = PGCGenerator()
        generator.generate(self, outf=outf, encoding=encoding,
                           abs_path=abs_path, pprint=pprint)
        
        
    # annotator info
    
    def get_annotator(self):
        try:
            return self._meta_data.find("annotator").text
        except AttributeError:
            pass
        
    def set_annotator(self, annot, append=True):
        annot_el = self._meta_data.find("annotator")
        
        if annot_el is None:
            annot_el = et.SubElement(self._meta_data, "annotator")
            
        if not annot_el.text or not append:
            annot_el.text = annot
        else:
            # add to list of annotators
            annot_el.text += " + " + annot

    #-------------------------------------------------------------------------------
    # Private
    #-------------------------------------------------------------------------------
        
    def _meta_data_equal(self, other):
        """
        test if self and other corpus have the same meta-data (if any)
        """
        if self._meta_data is other._meta_data:
            # both None or same object 
            return True
        else: 
            return equals(self._meta_data, other._meta_data)

        
    def _check_compatibility(self, other):
        """
        Check if another corpus is compatible w.r.t. relations and meta-data
        """
        if not isinstance(other, ParallelGraphCorpus):
            raise TypeError("cannot concatenate 'ParallelGraphCorpus' and " 
                            "'{0}' objects".format(
                            other.__class__.__name__))
        
        if self._relations != other._relations:
            raise ValueError("alignment relations of corpora must be identical")
        
        if self._meta_data != other._meta_data:
            warnings.warn("meta data of other corpus is discarded!",
                          DaesoWarning)
        
            
    def _graphbanks(self):
        """
        Return a list of all graphbanks in use.  
        
        @return: list of Graphbank instances
        """
        graphbanks = set()
        
        for graph_pair in self:
            graphbanks.add(graph_pair._banks.source)
            graphbanks.add(graph_pair._banks.target)
            
        return graphbanks        
    
    
    
class PGCParser(object):
    """
    Parser for parallel graph corpus in XML format.
    
    There are two requirements in parsing a corpus:
    
    (1) A graph pair defines an alignment between two graphs which are
        stored in separate graphbanks (see GraphBank class). A graphbank may 
        contain many graphs which are not involved in any graph pair. Therefore,
        when loading a graphbank we want to skip unaligned graphs, which saves
        time and memory. This is called "sparse graph loading"  and uses the
        SparseGraphBank class.
        
    (2) Alternatively, a corpus can be opened without really opening and
        parsing the graphbanks, which is usefull in cases where access to the 
        graph nodes is not required.
        
    Both use cases are addressed using a "graph stub", as explained below.
    
    When parsing the corpus xml, we first encounter the <graphbanks> and
    <file> elements. Empty graphbanks are created, containing only the file
    path and the format. Next, we encounter the graph pairs. The problem is
    that in order to create a GraphPair object, we need a pair of graphbanks
    and a pair of graphs. Since we have not parsed the graphs yet, we create
    graph stubs, which just record the id of the requested graph and the
    graph pair(s) which use it (the "clients"); see the GraphStub class. Only
    after all graph pairs are read do we load the required graphs from the
    graphbanks, replacing the graph stubs with real graphs (to be precise,
    replacing the reference to a graph stub in a graph pair by a reference to
    a full graph).
    """
    
    def __init__(self):
        self.in_meta_data=False
        self.graph_pair = None
        self.default_format = None
        self.relations = []
        self.dir = None
        self.relax_gb_paths = False
        # A dict of id to graphbanks used during parsing to link graph pairs
        # to graphbanks. Notice however that once parsing is finished the
        # ParallelGraphCorpus object holds no direct reference to
        # (Sparse)GraphBank objects; only the GraphPair objects do.
        self.graphbanks = {}
        
        
    def parse(self, inf, pg_corpus=None, graph_loading=LOAD_SPARSE,
              relax_gb_paths=False):
        """
        Parse corpus in XML format from file
        
        @param inf: input filename or file object
        
        @keyword pg_corpus: optional ParallelGraphObject receiving the parsed
        information
        
        @keyword graph_loading: a flag indicating how to load graphs:
            (1) LOAD_ALL: load all graphs from the graphbanks involved
            (2) LOAD_SPARSE: read only those graphs actually aligned in the corpus
            (3) LOAD_NONE: do not read any graphs but use graph stubs instead
            
        @keyword relax_gb_paths: if true, graphbank files may also be present
        in the same direcory as the corpus file instead of the location
        specified in the <file> element; this allows packing corpus and
        graphbank files for annotation at another site without changing the
        original graphbank file paths
            
        @return: (new) ParallelGraphCorpus object
        """
        if isinstance(inf, basestring):
            self.dir = os.path.dirname(inf)
        elif isinstance(inf, file):
            # if input is a tty, dir becomes ""
            self.dir = os.path.dirname(inf.name)
            
        if pg_corpus is not None:
            assert isinstance(pg_corpus, ParallelGraphCorpus)
            self.pg_corpus = pg_corpus
        else:
            self.pg_corpus = ParallelGraphCorpus()
            
        self.graph_loading = graph_loading
        self.relax_gb_paths = relax_gb_paths

        # use ElementTree's iterparse rather than expat, because we want to
        # store the meta-data as an Element
        for event, elem in et.iterparse(inf, ("start", "end")):
            if event == "start":
                try:
                    # search handler only
                    handler = self.start_handlers[elem.tag]
                except KeyError:
                    if not self.in_meta_data:
                        warnings.warn(
                            "Encountered illegal element <{0}>".format(elem.tag),
                            DaesoWarning)
                    continue
            else:
                try:
                    handler = self.end_handlers[elem.tag]
                except KeyError:
                    # illegal elements are already caught at their start,
                    # and if unbalanced by expat
                    continue
                
            # call handler outside try/except clause, so any KeyError
            # raised while executing the handler is not accidently caught
            handler(self, elem)
                
            
        return self.pg_corpus
    
    
    def load_graphbanks(self):
        for gb in self.graphbanks.values():
            try:
                gb.load()
            except IOError, inst:
                msg = 'Cannot load graphbank from "{0}" ({1})'.format(
                    inst.filename,
                    inst.strerror)
                raise DaesoError(msg)
                
                    
                
                
    
    #-------------------------------------------------------------------------------
    # Element start handlers
    #-------------------------------------------------------------------------------

    def handle_meta_data_elem_start(self, elem):
        self.in_meta_data = True

        
    def handle_graphbanks_elem_start(self, elem):
        # for backward compatibility, as use of a "format" on <graphbanks> is
        # deprecated
        self.default_format = elem.get("format")
        if self.default_format:
            warnings.warn('use of "format" attribute on <graphbank>" '
                          'tag is deprecated!', DaesoWarning)

            
    def handle_graph_pair_elem_start(self, elem):
        banks = self._get_banks(elem)
        graphs = self._get_graphs(elem, banks)
        self.graph_pair = GraphPair(banks, graphs)
            
        if self.graph_loading != LOAD_ALL:
            # Important: set link back to graph_pair on graphs stubs, so full
            # blown graphs can be substituted when graphs are loaded in the
            # graphbank
            graphs.source.add_client(self.graph_pair)
            graphs.target.add_client(self.graph_pair)
            
        self.pg_corpus.append(self.graph_pair)
        
        
        
    def _get_banks(self, graph_pair_elem):
        try:
            from_bank_id = graph_pair_elem.attrib["from_bank_id"]
        except  KeyError:
            self._missing_attrib_error(graph_pair_elem, "from_bank_id")
            
        try:
            to_bank_id = graph_pair_elem.attrib["to_bank_id"]
        except  KeyError:
            self._missing_attrib_error(graph_pair_elem, "to_bank_id")
            
        try:
            from_bank = self.graphbanks[from_bank_id]
        except KeyError:
            self._missing_graph_bank_error(from_bank_id)
               
        try:
            to_bank = self.graphbanks[to_bank_id]
        except KeyError:
            self._missing_graph_bank_error(to_bank_id)
            
        return Pair(from_bank, to_bank)
        
    
    def _get_graphs(self, graph_pair_elem, banks):
        try:
            from_graph_id = graph_pair_elem.attrib["from_graph_id"]
        except KeyError:
            self._missing_attrib_error(graph_pair_elem, "from_graph_id")
            
        try:
            to_graph_id = graph_pair_elem.attrib["to_graph_id"]
        except KeyError:
            self._missing_attrib_error(graph_pair_elem, "to_graph_id")
        
        if self.graph_loading == LOAD_ALL:
            # get full graphs
            try:
                from_graph = banks.source.get_graph(from_graph_id)
            except KeyError:
                self._missing_source_graph_error(graph_pair_elem)
                
            try:
                to_graph = banks.target.get_graph(to_graph_id)
            except KeyError:
                self._missing_target_graph_error(graph_pair_elem)
        else:
            # get graph stubs - we do not know whether the graph id's are
            # correct or not until we load the graphbanks
            from_graph = banks.source.get_graph_stub(from_graph_id)
            to_graph = banks.target.get_graph_stub(to_graph_id)
            
        return Pair(from_graph, to_graph)
        
        
    def handle_node_pair_start(self, elem):
        nodes = Pair( elem.get("from_node_id"), 
                      elem.get("to_node_id"))
        relation = elem.get("relation")
        self.graph_pair.add_align(nodes, relation)
    
    #-------------------------------------------------------------------------------
    # Element end handlers
    #-------------------------------------------------------------------------------
                        
    def handle_corpus_meta_data_elem_end(self, elem):
        self.pg_corpus.set_meta_data(elem)
        self.in_meta_data = False
        
        
    def handle_file_elem_end(self, elem):
        # TODO
        # - raise exceptions if required attribs are missing
        # - raise warnings if other attribs are found?
        id = elem.get("id")
        assert id not in self.graphbanks
        format = elem.get("format") or self.default_format
        file_path = elem.text.strip()
        
        if not os.path.isabs(file_path):
            # create absolute path, using os.path.realpath rather than
            # os.path.abspath because it also eliminates symbolic links
            file_path = os.path.join(self.dir, file_path) 
            file_path = os.path.realpath(file_path)
            
        # If relax_gb_paths is true, graphbank files may alternatively be
        # present in the same direcory as the corpus. This allows packing
        # corpus and graphbank files for annotation at another site without
        # changing the original graphbank file paths.
        # This is a bit of hack, but it serves a very real practical need
        # and I see no other way to provide for it.
        if ( not os.path.exists(file_path) and 
             self.relax_gb_paths ):
            file_path = os.path.join(self.dir, 
                                     os.path.basename(file_path))
            file_path = os.path.realpath(file_path) 
        
        if self.graph_loading == LOAD_ALL:
            self.graphbanks[id] = GraphBank(file_path, format)
        else:
            self.graphbanks[id] = SparseGraphBank(file_path, format)
            
        # until loading, we don't care if file_path really exists
        
    
    def handle_relation_elem_end(self, elem):
        self.relations.append(elem.text.strip())
        
    
    def handle_node_relations_elem_end(self, elem):
        self.pg_corpus.set_relations(self.relations)
        
        
    def handle_graph_meta_data_elem_end(self, elem):
        self.graph_pair._meta_data = elem
        self.in_meta_data = False
        
        
    def handle_graphbanks_elem_end(self, elem):
        if self.graph_loading == LOAD_ALL:
            self.load_graphbanks()
            
            
    def handle_aligned_graphs_elem_end(self, elem):
        if self.graph_loading == LOAD_SPARSE:
            self.load_graphbanks()
            
        
    
    #-------------------------------------------------------------------------------
    # Errors
    #-------------------------------------------------------------------------------
    
    def _missing_attrib_error(self, elem, attrib):
        # TODO: report line number
        raise DaesoError('<{0}> element lacks required "{1}"'
                         'attribute'.format(
                             elem.tag,
                             attrib))
    
    
    def _missing_source_graph_error(self, elem):
        # TODO: report line number
        raise DaesoError('source graph with id "{0}" not found in '
                         'source graphbank with id "{1}"'.format(
                             elem.get("from_graph_id"),
                             elem.get("from_bank_id")))
    
    def _missing_target_graph_error(self, elem):
        # TODO: report line number
        raise DaesoError('target graph with id "{0}" not found '
                         'in target graphbank with id "{1}"'.format(
                             elem.get("to_graph_id"),
                             elem.get("to_bank_id")))  
    
    def _missing_graph_bank_error(self, bank_id):
        raise DaesoError('graphbank with id "{0}" not found'.format(
            bank_id))
    
    
    #-------------------------------------------------------------------------------
    # Handler assignment
    #-------------------------------------------------------------------------------
    
    def handle_any_elem(self, elem):
        # handler to define any other *valid* element;
        # unknown elements raise an error
        pass
    
    
    start_handlers = dict(
        corpus_meta_data = handle_meta_data_elem_start,
        graphbanks = handle_graphbanks_elem_start,
        graph_pair = handle_graph_pair_elem_start,
        graph_meta_data = handle_meta_data_elem_start,
        node_pair = handle_node_pair_start,
        parallel_graph_corpus = handle_any_elem,
        file = handle_any_elem,
        node_relations = handle_any_elem,
        relation = handle_any_elem,
        aligned_graphs = handle_any_elem,
        aligned_nodes = handle_any_elem,
     )
        
    end_handlers = dict(
        corpus_meta_data = handle_corpus_meta_data_elem_end,
        file = handle_file_elem_end,
        graphbanks = handle_graphbanks_elem_end,
        relation = handle_relation_elem_end,
        node_relations = handle_node_relations_elem_end,
        graph_meta_data = handle_graph_meta_data_elem_end,
        aligned_graphs = handle_aligned_graphs_elem_end
     )
        
        
        



class PGCGenerator(object):
    """
    Generator for parallel graph corpus in XML format.
    """
    # stateless and therefore reuseable
    
    def generate(self, pg_corpus, outf=sys.stdout, encoding="utf-8",
                 abs_path=False, pprint=False):
        """
        Generate parallel graph corpus in XML format
        
        @param pg_corpus: ParallelGraphCorpus instance
        
        @keyword outf: output filename or file object
        
        @keyword encoding: character encoding
        
        @keyword abs_path: use absolute graphbank file paths; the default is
        to use graphbank file paths which are relative to the corpus file path
        
        @keyword pprint: pretty print (indent) xml output
        
        @return: ElementTree object
        """
        if isinstance(outf, basestring):
            out_dir = os.path.dirname(outf)
        elif isinstance(outf, file):
            # if output is a tty, dir becomes ""
            out_dir = os.path.dirname(outf.name)
        else:
            out_dir = os.getcwd()
            
        root_elem = self._gen_pg_corpus(pg_corpus, out_dir, abs_path)
        tree = et.ElementTree(root_elem)
        write(tree, outf, encoding=encoding, pprint=pprint)
        return tree
        
    
    def _gen_pg_corpus(self, pg_corpus, out_dir, abs_path):
        root_elem = et.Element("parallel_graph_corpus")
        
        if pg_corpus._meta_data:
            root_elem.append(pg_corpus._meta_data)
        
        graphbanks_elem = et.SubElement(root_elem, "graphbanks")
        self._gen_node_relations(root_elem, pg_corpus)
        graphbanks = self._gen_aligned_graphs(root_elem, pg_corpus)
        self._gen_graphbanks(graphbanks_elem, graphbanks, out_dir, abs_path)
        return root_elem
        
        
    def _gen_node_relations(self, root_elem, pg_corpus):
        node_rels_elem = et.SubElement(root_elem, "node_relations")
        
        for relation in pg_corpus._relations:
            et.SubElement(node_rels_elem, "relation").text = relation
            
            
    def _gen_aligned_graphs(self, root_elem, pg_corpus):
        # This is similar to the ParallelGraphCorpus.purge() method. It purges
        # the corpus of duplicate grapbanks held in memory, which may arise
        # after modifications such as adding graph pairs or concatenating
        # corpora. In addition, it assigns a unique id to the remaining
        # graphbanks and makes sure that "id" attribute in <graphpair>
        # elements refers to the right graphbank.
        aligned_graphs_elem = et.SubElement(root_elem, "aligned_graphs")
        # A table for remapping old graphbanks to new graphbanks
        # (difference between source and target banks is irelevant)
        old2new = {}
        # A list 
        graphbanks = []
        bank_id_attr = "from_bank_id", "to_bank_id"

        
        for n, graph_pair in enumerate(pg_corpus):
            graph_pair_elem = et.SubElement(
                aligned_graphs_elem,
                "graph_pair",
                n=str(n+1),
                from_graph_id=graph_pair._graphs.source.id,
                to_graph_id=graph_pair._graphs.target.id)
            
            if graph_pair._meta_data:
                graph_pair_elem.append(graph_pair._meta_data)
            
            self._gen_node_pairs(graph_pair_elem, graph_pair)
                
            for old_gb, attrib in zip(graph_pair._banks,
                                      bank_id_attr):
                try:
                    new_gb = old2new[old_gb]
                except KeyError:
                    # see if the old bank matches any of the known new banks
                    for new_gb in old2new.itervalues():
                        # recall that equality is implemented as
                        # os.path.samepath
                        if old_gb == new_gb:
                            # match found
                            old2new[old_gb] = new_gb
                            break
                    else:
                        # old bank has not been seen yet,
                        # so we add it by mapping it onto itself
                        new_gb = old2new[old_gb] = old_gb
                        # we add it to the list of required graphbanks
                        graphbanks.append(new_gb)
                        # and finally we give it a new unique id
                        new_gb._id = str(len(graphbanks))
                        
                graph_pair_elem.set(attrib, new_gb._id)
            
        return graphbanks
    
    
    def _gen_node_pairs(self, graph_pair_elem, graph_pair):
        for nodes, relation in graph_pair.alignments_iter():
            et.SubElement(
                graph_pair_elem,
                "node_pair",
                from_node_id=nodes.source,
                to_node_id=nodes.target,
                relation=relation)
            
    
    def _gen_graphbanks(self, graphbanks_elem, graphbanks, out_dir, abs_path):
        for gb in graphbanks:
            file_elem = et.SubElement(
                graphbanks_elem,
                "file",
                id=gb._id,
                format=gb._format)
            
            if abs_path:
                file_elem.text = gb._file_path
            else:
                # Create filename relative to corpus dir.
                # Use realpath to eliminate symlinks in out_dir, 
                # because otherwise relpath may become confused 
                out_dir = os.path.realpath(out_dir)
                file_elem.text = os.path.relpath(gb._file_path, out_dir)
                
        

            
