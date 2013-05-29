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
Joins multiple parallel graph corpora into a single parallel graph corpus and
writes it to standard output.

Meta-data of everything but the first corpus is discarded!
"""

# TODO:
# - silence warning about meta-data


__authors__ = 'Erwin Marsi <e.marsi@gmail.com>'


import sys

from daeso.utils.cli import DaesoArgParser
from daeso.utils.opsys import multiglob
from daeso.pgc.corpus import ParallelGraphCorpus


parser = DaesoArgParser(description=__doc__, version=__revision__)

    
parser.add_argument(
    "file",
    nargs="+",
    metavar="FILE",
    help="parallel graph corpus filename, "
    "or quoted file name pattern for parallel graph corpora"
    )

parser.add_argument(
    "-f", "--format",
    action="store_true",
    help="output indented XML"
    )

parser.add_argument(
    "-V", "--verbose",
    action="store_true",
    help="verbose ouput to stderr"
    )


args = parser.parse_args()

pgc_fns = multiglob(args.file)

def log(s):
    if args.verbose:
        print >>sys.stderr, "***", s
        
        
log("Reading corpus from " + pgc_fns[0])
        
corpus = ParallelGraphCorpus(inf=pgc_fns[0])

for fn in pgc_fns[1:]:
    log("Joining corpus from " + fn)
    # __iadd__ also checks if another corpus is compatible w.r.t. relations
    # and meta-data
    corpus += ParallelGraphCorpus(inf=fn)
    

# Purge the corpus of duplicate graphbanks held in memory    
log("Purging corpus")    
corpus.purge()

log("Writing corpus")
corpus.write(pprint=args.format)

