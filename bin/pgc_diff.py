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
parallel graph corpus diff

reports difference in node alignments between two parallel graph corpora
"""

from daeso.utils.cli import DaesoArgParser
from daeso.pgc.corpus import ParallelGraphCorpus
from daeso.pgc.diff import pgc_diff


__authors__ = 'Erwin Marsi <e.marsi@gmail.com>'

    

parser = DaesoArgParser(description=__doc__, version=__revision__)


parser.add_argument(
    "corpus1", 
    help="first parallel graph corpus")

parser.add_argument(
    "corpus2", 
    help="second parallel graph corpus")


parser.add_argument(
    "-1", "--first_annotator", 
    metavar="NAME", 
    default="First annotator", 
    help="name of annotator of first corpus")

parser.add_argument(
    "-2", "--second_annotator", 
    metavar="NAME", 
    default="Second annotator", 
    help="name of annotator of second corpus")

parser.add_argument(
    "-c", "--with_comments", 
    action="store_true", 
    help="show annotator's comments")

parser.add_argument(
    "-e", "--evaluate", 
    action="store_true", 
    help="show evaluation measures and statistics")

parser.add_argument(
    "-i", "--with_ident", 
    action="store_true", 
    help="include identical alignments")

parser.add_argument(
    "-r", "--relations",
    metavar="REL",
    nargs="*",
    help="limit output to given relations")

args = parser.parse_args()


corpus1 = ParallelGraphCorpus(inf=args.corpus1)
corpus2 = ParallelGraphCorpus(inf=args.corpus2)

pgc_diff(corpus1, corpus2, 
         corpus_name1=args.corpus1,
         corpus_name2=args.corpus2,
         annot1=args.first_annotator, 
         annot2=args.second_annotator,
         show_comments=args.with_comments,
         show_ident=args.with_ident,
         relations=args.relations)

if args.evaluate:
    from daeso.pgc.evaluate import AlignEval
    align_eval = AlignEval()
    align_eval.add(corpus1, corpus2)
    align_eval.run_eval()
    align_eval.write()
    



