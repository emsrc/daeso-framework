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
prints parallel graph corpus statistics
"""

__authors__ = 'Erwin Marsi <e.marsi@gmail.com>'


from glob import glob
from sys import exit

from daeso.utils.cli import DaesoArgParser, epilog
from daeso.pgc.pgcstats import pgc_stats 


epilog = """
Examples:
  $ pgc_stats.py -efpu "*.pgc" 
  
Remarks:
  * Failed parses will only be exluded for graph banks in 'alpino' format.

""" + epilog


parser = DaesoArgParser(description=__doc__,
                        epilog=epilog)

parser.add_argument(
    "pattern",
               help="*quoted* pattern for parallel graph corpus files")

parser.add_argument(
    "-a", "--with-all", 
    action="store_true", 
    dest="with_all", 
    help="include all, sets options -efpru")

#parser.add_argument("-c", "--csv", action="store_true", 
                  #dest="csv", 
                  #help="output in comma separated values")

parser.add_argument(
    "-e", "--with-empty-nodes", 
    action="store_true", 
    dest="with_empty_nodes", 
    help="include empty nodes (traces)")

parser.add_argument(
    "-f", "--with-failed-parses", 
    action="store_true", 
    dest="with_failed_parses", 
    help="include failed parses")
               
parser.add_argument(
    "-l", "--legenda", 
    action="store_true", 
    dest="legenda",
    help="print legenda")

parser.add_argument(
    "-p", "--with-punc-nodes", 
    action="store_true", 
    dest="with_punc", 
    help="include punctuation tokens/nodes")

parser.add_argument(
    "-r", "--with-unaligned-roots", 
    action="store_true", 
    dest="with_unaligned_roots", 
    help="include graphs with unaligned root nodes")

parser.add_argument(
    "-t", "--token_diff_threshold", 
    type="int", 
    metavar="THRESHOLD",
    default=0, dest="threshold", 
    help="exclude graph pairs with a token difference below the threshold")

parser.add_argument(
    "-u", "--with_unaligned-graphs",
    action="store_true", 
    dest="with_unaligned_graphs", 
    help="include unaligned graphs")


args = parser.parse_args()

files = glob(args.pattern)

if not files:
    exit("pgc_stats.py: warning: no matching files")
    
if args.with_all:
    args.with_empty_nodes = True
    args.with_failed_parses = True
    args.with_punc = True
    args.with_unaligned_roots = True
    args.with_unaligned_graphs = True
    

pgc_table, gb_table = pgc_stats(
    files, 
    with_empty_nodes=args.with_empty_nodes,
    with_failed_parses=args.with_failed_parses,
    with_punc=args.with_punc,
    with_unaligned_roots=args.with_unaligned_roots,
    threshold=args.threshold,
    with_unaligned_graphs=args.with_unaligned_graphs)

pgc_table.write(legenda=args.legenda)
gb_table.write(legenda=args.legenda)


