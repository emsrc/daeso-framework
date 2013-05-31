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
evaluation of text alignment in parallel text corpora

reports precision, recall and F-score on alignment for a certain tag
for one or more pairs of true and predicted parallel text corpora
"""

from daeso.utils.cli import DaesoArgParser
from daeso.ptc.evaluate import eval_alignment


__authors__ = 'Erwin Marsi <e.marsi@gmail.com>'

    

parser = DaesoArgParser(description=__doc__)


parser.add_argument(
    "-t", "--true_corpora", 
    nargs = "+",
    help="parallel text corpus containing true alignments")

parser.add_argument(
    "-p", "--pred_corpora", 
    nargs = "+",
    help="parallel text corpus containing predicted alignments")

parser.add_argument(
    "--tag", 
    default="s", 
    help='only consider alignments involving this tag (defaults is "s"')


args = parser.parse_args()


assert len(args.true_corpora) == len(args.pred_corpora)

eval_alignment(zip(args.true_corpora, args.pred_corpora), args.tag)
