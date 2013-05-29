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
convert a parallel text corpus from n-based alignment to id-based alignment
"""


from sys import stderr
from os.path import splitext, join

from daeso.utils.cli import ArgumentParser
from daeso.ptc.document import HitaextDoc



    


parser = ArgumentParser(description=__doc__, version=__revision__)

parser.add_argument(
    "corpus",
    nargs="+",
    default="parallel text corpus",
    help=""
    )


parser.add_argument(
    "-V", "--verbose",
    action="store_true",
    help="verbose output"
    )


args = parser.parse_args()

if args.verbose:
    print >>stderr, "Reading corpus from", args.corpus
    
corpus = HitaextDoc(file=args.corpus)

from_tree = corpus.get_doc_tree("from")
to_tree = corpus.get_doc_tree("to")

from_tree.update()
to_tree.update()

corpus.inject_alignments(from_tree, to_tree)

corpus.alignment.set("method", "id")

corpus.extract_alignments(from_tree, to_tree)

if args.verbose:
    print >>stderr, "Writing corpus to", args.corpus
    
corpus.write(args.corpus)

