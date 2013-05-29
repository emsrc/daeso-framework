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
Ordered directed graph derived from NetworkX's DiGraph class.
(for NetworkX version >= 1.0rc1)

An OrderedDict (http://www.xs4all.nl/~anthon/Python/ordereddict/) is a dict
that keeps keys in insertion order. By using an ordered rather than a a normal
dict for the graph's predecessor and successor dicts, we keep track of the
order in which incoming/outgoing edges were added to a node (graph).

The beauty of this approach is that it allows us to reuse basically all the
(inherited) methods of DiGraph, because they are unaware of the fact that they
operate on an ordered rather than a normal dict. Still, their behaviour and
output may reflect the insertion order.

For example, the self.out_edges_iter method iterates over the ordeded dict
self.succ, and therefore yields the edges in the order in which they were
originally added.

OrderedDict comes at a slight performance penalty in terms of both time and
memory, which might become signifcant for large graphs. A possible solution
then is to use the ordereddict extension module from
http://www.xs4all.nl/~anthon/Python/ordereddict/
"""

# I entertained the idea of overloading dict with OrderedDict. However,
# networkx inits dicts using {}, so that wouldn't work. And even if those
# would be changed into dict(), that would also turn other dicts such as
# self.graph and self.node into ordered dicts, which is obviously undesirable.

__authors__ = "Erwin Marsi <e.marsi@gmail.com>"



from distutils.version import LooseVersion
import networkx

if LooseVersion(networkx.__version__) < LooseVersion('1.0'):
    raise ImportError("networkx version 1.0 or later required" +
                      "(this is version {0!r}".format(networkx.__version__))

try:
    from collections import OrderedDict
except ImportError:
    from daeso.thirdparty.odict import OrderedDict

    

class ODiGraph(networkx.DiGraph):
    """ 
    Ordered directed graph 
    
    This overrules all relevant methods of DiGraph which init a new dict in
    self.pred or self.succ using {}, and substitutes OrderedDict(). There are
    no relevant inherited methods from Graph for which we have to do the same.
    """

    def __init__(self, data=None, name='', **attr):
        """Initialize a graph with edges, name, graph attributes.

        Parameters
        ----------
        data : input graph
            Data to initialize graph.  If data=None (default) an empty
            graph is created.  The data can be an edge list, or any
            NetworkX graph object.  If the corresponding optional Python
            packages are installed the data can also be a NumPy matrix
            or 2d ndarray, a SciPy sparse matrix, or a PyGraphviz graph.
        name : string, optional (default='')
            An optional name for the graph.
        attr : keyword arguments, optional (default= no attributes)
            Attributes to add to graph as key=value pairs.

        See Also
        --------
        convert
            
        Examples
        --------
        >>> G = nx.Graph()   # or DiGraph, MultiGraph, MultiDiGraph, etc
        >>> G = nx.Graph(name='my graph')
        >>> e = [(1,2),(2,3),(3,4)] # list of edges
        >>> G = nx.Graph(e)

        Arbitrary graph attribute pairs (key=value) may be assigned

        >>> G=nx.Graph(e, day="Friday")
        >>> G.graph
        {'day': 'Friday'}

        """
        self.graph = {} # dictionary for graph attributes
        self.node = {} # dictionary for node attributes
        # We store two adjacency lists:
        # the  predecessors of node n are stored in the dict self.pred
        # the successors of node n are stored in the dict self.succ=self.adj
        self.adj = OrderedDict()  # empty adjacency dictionary
        self.pred = OrderedDict()  # predecessor
        self.succ = self.adj  # successor

        # attempt to load graph with data
        if data is not None:
            convert.from_whatever(data,create_using=self)
        # load graph attributes (must be after convert)
        self.graph.update(attr)

        self.name=name
        self.edge=self.adj

        
    def add_node(self, n, attr_dict=None, **attr):
        """Add a single node n and update node attributes.

        Parameters
        ----------
        n : node
            A node can be any hashable Python object except None.
        attr_dict : dictionary, optional (default= no attributes)
            Dictionary of node attributes.  Key/value pairs will
            update existing data associated with the node.
        attr : keyword arguments, optional
            Set or change attributes using key=value.

        See Also
        --------
        add_nodes_from

        Examples
        --------
        >>> G = nx.Graph()   # or DiGraph, MultiGraph, MultiDiGraph, etc
        >>> G.add_node(1)
        >>> G.add_node('Hello')
        >>> K3 = nx.Graph([(0,1),(1,2),(2,0)])
        >>> G.add_node(K3)
        >>> G.number_of_nodes()
        3

        Use keywords set/change node attributes:

        >>> G.add_node(1,size=10)
        >>> G.add_node(3,weight=0.4,UTM=('13S',382871,3972649))

        Notes
        -----
        A hashable object is one that can be used as a key in a Python
        dictionary. This includes strings, numbers, tuples of strings
        and numbers, etc.

        On many platforms hashable items also include mutables such as
        NetworkX Graphs, though one should be careful that the hash
        doesn't change on mutables.
        """
        # set up attribute dict
        if attr_dict is None:
            attr_dict=attr
        else:
            try:
                attr_dict.update(attr)
            except AttributeError:
                raise NetworkXError(\
                    "The attr_dict argument must be a dictionary.")
        if n not in self.succ:
            self.succ[n] = OrderedDict()
            self.pred[n] = OrderedDict()
            self.node[n] = attr_dict
        else: # update attr even if node already exists            
            self.node[n].update(attr_dict)

    def add_nodes_from(self, nodes, **attr):
        """Add multiple nodes.

        Parameters
        ----------
        nodes : iterable container
            A container of nodes (list, dict, set, etc.).  The
            container will be iterated through once.
        attr : keyword arguments, optional (default= no attributes)
            Update attributes for all nodes in nodes.

        See Also
        --------
        add_node

        Examples
        --------
        >>> G = nx.Graph()   # or DiGraph, MultiGraph, MultiDiGraph, etc
        >>> G.add_nodes_from('Hello')
        >>> K3 = nx.Graph([(0,1),(1,2),(2,0)])
        >>> G.add_nodes_from(K3)
        >>> sorted(G.nodes())
        [0, 1, 2, 'H', 'e', 'l', 'o']

        Use keywords to update specific node attributes for every node.

        >>> G.add_nodes_from([1,2], size=10)
        >>> G.add_nodes_from([3,4], weight=0.4)

        """
        for n in nodes:
            if n not in self.succ:
                self.succ[n] = OrderedDict()
                self.pred[n] = OrderedDict()
                self.node[n] = attr
            else: # update attr even if node already exists            
                self.node[n].update(attr)

                
    def add_edge(self, u, v, attr_dict=None, **attr):  
        """Add an edge between u and v.

        The nodes u and v will be automatically added if they are 
        not already in the graph.  

        Edge attributes can be specified with keywords or by providing
        a dictionary with key/value pairs.  See examples below.

        Parameters
        ----------
        u,v : nodes
            Nodes can be, for example, strings or numbers. 
            Nodes must be hashable (and not None) Python objects.
        attr_dict : dictionary, optional (default= no attributes)
            Dictionary of edge attributes.  Key/value pairs will
            update existing data associated with the edge.
        attr : keyword arguments, optional
            Edge data (or labels or objects) can be assigned using
            keyword arguments.   

        See Also
        --------
        add_edges_from : add a collection of edges

        Notes 
        -----
        Adding an edge that already exists updates the edge data.

        NetworkX algorithms designed for weighted graphs use as
        the edge weight a numerical value assigned to the keyword
        'weight'.

        Examples
        --------
        The following all add the edge e=(1,2) to graph G:
        
        >>> G = nx.Graph()   # or DiGraph, MultiGraph, MultiDiGraph, etc
        >>> e = (1,2)
        >>> G.add_edge(1, 2)           # explicit two-node form
        >>> G.add_edge(*e)             # single edge as tuple of two nodes
        >>> G.add_edges_from( [(1,2)] ) # add edges from iterable container

        Associate data to edges using keywords:

        >>> G.add_edge(1, 2, weight=3)
        >>> G.add_edge(1, 3, weight=7, capacity=15, length=342.7)
        """
        # set up attribute dict
        if attr_dict is None:
            attr_dict=attr
        else:
            try:
                attr_dict.update(attr)
            except AttributeError:
                raise NetworkXError(\
                    "The attr_dict argument must be a dictionary.")
        # add nodes            
        if u not in self.succ: 
            self.succ[u]=OrderedDict()
            self.pred[u]=OrderedDict()
            self.node[u] = {}
        if v not in self.succ: 
            self.succ[v]=OrderedDict()
            self.pred[v]=OrderedDict()
            self.node[v] = {}
        # add the edge
        datadict=self.adj[u].get(v,{})
        datadict.update(attr_dict)
        self.succ[u][v]=datadict
        self.pred[v][u]=datadict

        
    def add_edges_from(self, ebunch, attr_dict=None, **attr):  
        """Add all the edges in ebunch.

        Parameters
        ----------
        ebunch : container of edges
            Each edge given in the container will be added to the
            graph. The edges must be given as as 2-tuples (u,v) or
            3-tuples (u,v,d) where d is a dictionary containing edge
            data.
        attr_dict : dictionary, optional (default= no attributes)
            Dictionary of edge attributes.  Key/value pairs will
            update existing data associated with each edge.
        attr : keyword arguments, optional
            Edge data (or labels or objects) can be assigned using
            keyword arguments.   


        See Also
        --------
        add_edge : add a single edge
        add_weighted_edges_from : convenient way to add weighted edges

        Notes
        -----
        Adding the same edge twice has no effect but any edge data
        will be updated when each duplicate edge is added.

        Examples
        --------
        >>> G = nx.Graph()   # or DiGraph, MultiGraph, MultiDiGraph, etc
        >>> G.add_edges_from([(0,1),(1,2)]) # using a list of edge tuples
        >>> e = zip(range(0,3),range(1,4))
        >>> G.add_edges_from(e) # Add the path graph 0-1-2-3
  
        Associate data to edges

        >>> G.add_edges_from([(1,2),(2,3)], weight=3)
        >>> G.add_edges_from([(3,4),(1,4)], label='WN2898')
        """
        # set up attribute dict
        if attr_dict is None:
            attr_dict=attr
        else:
            try:
                attr_dict.update(attr)
            except AttributeError:
                raise NetworkXError(\
                    "The attr_dict argument must be a dict.")
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
            if u not in self.succ: 
                self.succ[u] = OrderedDict()
                self.pred[u] = OrderedDict()
                self.node[u] = {}
            if v not in self.succ: 
                self.succ[v] = OrderedDict()
                self.pred[v] = OrderedDict()
                self.node[v] = {}
            datadict=self.adj[u].get(v,{})
            datadict.update(attr_dict) 
            datadict.update(dd)
            self.succ[u][v] = datadict
            self.pred[v][u] = datadict


   
