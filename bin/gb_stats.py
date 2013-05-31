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
prints graph bank statistics
"""

# TODO:
# * error msg for unrecognized format


__authors__ = 'Erwin Marsi <e.marsi@gmail.com>'

from glob import glob

from daeso.utils.cli import DaesoArgParser, epilog
from daeso.gb.gbstats import gb_stats


epilog = """
Remarks:
  * Many columns will have zero values, because a parallel graph corpus 
    is required to get alignment information; see pgc_stats.py
  * Failed parses will only be excluded for graph banks in 'alpino' format.
  
""" + epilog  


parser = DaesoArgParser(description=__doc__, epilog=epilog)

parser.add_argument(
    "pattern", 
    help="*quoted* pattern for graph bank files")

parser.add_argument(
    "-F", "--format", 
    metavar="STRING",
    default="alpino", 
    dest="format", 
    help="treebank format (defaults to 'alpino')")

parser.add_argument(
    "-a", "--with-all", 
    action="store_true", 
    dest="with_all", 
    help="include all, sets options -efp")

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
    "-t", "--token_diff_threshold", 
    type=int, 
    metavar="THRESHOLD",
    default=0, 
    dest="threshold", 
    help="exclude graph pairs with a token difference below the threshold")

args = parser.parse_args()

files = glob(args.pattern)

if not files:
    exit("gb_stats.py: warning: no matching files")
        
if args.with_all:
    args.with_empty_nodes = True
    args.with_failed_parses = True
    args.with_punc = True

gb_table = gb_stats(files, 
                    format=args.format,
                     with_empty_nodes=args.with_empty_nodes,
                     with_failed_parses=args.with_failed_parses,
                     with_punc=args.with_punc,
                     threshold=args.threshold,)

gb_table.write(legenda=args.legenda)