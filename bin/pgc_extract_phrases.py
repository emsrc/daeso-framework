#!/usr/bin/env python
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
extract aligned phrases from parallel graph corpus

Reads one or more parallel graph corpus files and extracts the aligned
phrases. The output format consists of three fields:
1. the source phrase
2. the alignment relation
3. the target phrase.
Fields are separated by a delimiter which default to a tab character.
Output is written to standard output as utf-8 encoded text.
"""

__authors__ = 'Erwin Marsi <e.marsi@gmail.com>'



from daeso.utils.cli import DaesoArgParser
from daeso.pgc.corpus import ParallelGraphCorpus


def extract_phrases(file, delimiter="\t", verbose=False):
    corpus = ParallelGraphCorpus(inf=file)
    
    for graph_pair in corpus:
        graphs = graph_pair.get_graphs()
        
        for nodes, relation in graph_pair.alignments_iter():
            columns = [ 
                graphs.source.get_node_token_string(nodes.source),
                relation,
                graphs.target.get_node_token_string(nodes.target) ]
            
            if verbose:
                banks = graph_pair.get_banks()
                
                columns = [
                    banks.source.get_file_path(),
                    banks.target.get_file_path(),
                    graphs.source.id,
                    graphs.target.id,
                    nodes.source,
                    nodes.target
                    ] + columns
                
            print delimiter.join(columns).encode("utf-8")
            
            
parser = DaesoArgParser(description=__doc__.strip())

parser.add_argument(
    "corpus", 
    nargs="+",
    metavar="FILE",
    help="parallel graph corpus file"
    )

parser.add_argument(
    "-d", "--delimiter",
    default="\t",
    help="column delimiter string (default is tab character '\\t')"
    )

parser.add_argument(
    "-V", "--verbose",
    action="store_true",
    help="print graph pair number, from and to bank id's, from and to graph id's, "
    "and from and to node id's"
    )


args = parser.parse_args()          

for fn in args.corpus:
    extract_phrases(fn, args.delimiter, args.verbose)