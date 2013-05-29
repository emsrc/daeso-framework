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
parallel text corpus diff

reports difference in text alignments between two parallel text corpora
"""

from daeso.utils.cli import DaesoArgParser
from daeso.ptc.diff import print_diff


__authors__ = 'Erwin Marsi <e.marsi@gmail.com>'

    

parser = DaesoArgParser(description=__doc__, version=__revision__)


parser.add_argument(
    "true_corpus", 
    help="parallel text corpus containing true alignments")

parser.add_argument(
    "pred_corpus", 
    help="parallel text corpus containing predicted alignments")


parser.add_argument(
    "-t", "--tag", 
    default="s", 
    help='only consider alignments involving this tag (defaults is "s"')

parser.add_argument(
    "-e", "--encoding", 
    default="utf-8",
    help='character encoding of output (default is "utf-8")')


args = parser.parse_args()

print_diff(args.true_corpus, args.pred_corpus, args.tag, args.encoding)

