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
calculate inter-annotator agreement over multiple parallel graph corpora

Reports inter-annotator agreement on labeled alignments from two or more
parallel graph corpora, and generates an analysis in terms of a number of
statistics.

For a more detailed analysis of the diferences between a pair of annotations,
use pgc_diff.py
"""

# TODO:
# - check for at least two input files


__authors__ = 'Erwin Marsi <e.marsi@gmail.com>'



from daeso.utils.cli import DaesoArgParser
from daeso.pgc.agreement import run_eval


parser = DaesoArgParser(description=__doc__, version=__revision__)

parser.add_argument(
    "corpus_fns",
    nargs="+",
    metavar="corpus",
    help="parallel graph corpus file (at least two are required)")

parser.add_argument(
    "-a", "--annotator",
    dest="annotators",
    metavar="CC", 
    action="append",
    help="initials of the annotator of a parallel graph corpus files "
    "(default is 'A1', 'A2', etc.) Repeat this option as many times as " 
    "there are corpus files")

parser.add_argument(
    "-p", "--pickle", 
    dest="pickle_fn",
    metavar="FILE",
    help="dump results to file as a Python pickle")

parser.add_argument(
    "-w", "--words-only", 
    action="store_true", 
    help="consider word alignments only, ignoring all alignments involving "
    "at a non-terminal node")

args = parser.parse_args()

run_eval(**args.__dict__)




