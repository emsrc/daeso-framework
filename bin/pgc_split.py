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
Split a parallel graph corpus into multiple parts
"""

__authors__ = 'Erwin Marsi <e.marsi@gmail.com>'


import os
import sys

from daeso.utils.cli import DaesoArgParser
from daeso.pgc.corpus import ParallelGraphCorpus


def log(s):
    if args.verbose:
        print >>sys.stderr, "***", s
        
parser = DaesoArgParser(description=__doc__, version=__revision__)

parser.add_argument(
    "filename",
    metavar="FILE",
    help="parallel graph corpus"
    )

parser.add_argument(
    "-f", "--format",
    action="store_true",
    help="output indented XML"
    )

parser.add_argument(
    "-p", "--parts",
    default=2,
    type=int,
    metavar="N",
    help="number of parts"
    )

parser.add_argument(
    "-s", "--size",
    type=int,
    metavar="N",
    help="number of graph pairs per part"
    )

parser.add_argument(
    "-V", "--verbose",
    action="store_true",
    help="verbose ouput to stderr"
    )

args = parser.parse_args()

log("Reading corpus from " + args.filename)
corpus = ParallelGraphCorpus(inf=args.filename)
root, ext = os.path.splitext(args.filename)

if not args.size:
    args.size = int(round(len(corpus) / args.parts + 0.5))

for i in range(0, len(corpus), args.size): 
    j = min(i + args.size, len(corpus))
    part_corpus = corpus[i:j]
    part_filename = "{0}_{1:04d}-{2:04d}{3}".format(root, i + 1, j, ext)
    log("Writing corpus part " + part_filename)
    part_corpus.write(outf=part_filename, pprint=args.format)
    
    
    