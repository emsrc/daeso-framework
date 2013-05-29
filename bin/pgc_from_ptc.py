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
create a parallel graph corpus from a parallel text corpus and corresponding graph banks
"""

__authors__ = 'Erwin Marsi <e.marsi@gmail.com>'


import sys
import os

from daeso.utils.cli import DaesoArgParser, epilog
from daeso.pgc.creation import pgc_from_ptc
from daeso.pair import Pair
from daeso.relations import RELATIONS
    
 
epilog=""" 
Remarks: 
   To avoid specifing all the parallel text corpora and graphbanks by hand,
   you can use the shell "back tick" trick (in bash at least) like this:
  
    %prog -p `ls corpus*.ptc` -s `ls source-grapbank*.xml` -t `ls target-graphbank*.xml`
    
  or in the more readable form:
  
      %prog -p $(ls corpus*.ptc) -s $(ls source-grapbank*.xml) -t $(ls target-graphbank*.xml)
  
  Writes the new parallel graph corpus under a name which is derived from the
  basename of the parallel text corpus with the extension changed to ".pgc".

  The references in each parallel text corpus to a "from" and "to" file
  containing marked up text must be valid.
  
  The method of alignment (cf. the "method" attribute on the <alignment> tag)
  must be "id" rather than "n". By default, the only alignments considered are
  those <link>'s where both the "from_tag" and "to_tag" are "s" and all others
  are ignored. The --source-tag and --target-tag options allows you change
  this default.
  
  The graphs must have an "id" attribute which is identical to the "id" of a
  corresponding sentence (<s> element, by default) in the marked-up text
  files. That is, a <links>'s "from_id" and "to_id" must identify
  corresponding graphs in the "from" and "to" graphbanks respectively.
  
  The graphbanks are assumed to be in GraphML format, unless specified
  otherwise by means of the --source-graphbank-format and
  --target-graphbank-format option.
  
  The default set of alignment relations for the parallel graph corpus is the
  Daeso set, but you can change it using the --relations option.
  
""" + epilog 

parser = DaesoArgParser(description=__doc__, version=__revision__, epilog=epilog)


parser.add_argument(
    "-p", "--parallel-text-corpora", 
    metavar="CORPUS",
    nargs="+",
    default=(),
    help='parallel text corpora')

parser.add_argument(
    "-s", "--source-graphbanks", 
    metavar="GRAPHBANK",
    nargs="+",
    default=(),
    help='source graphbanks')

parser.add_argument(
    "-t", "--target-graphbanks", 
    metavar="GRAPHBANK",
    nargs="+",
    default=(),
    help='target graphbanks')


parser.add_argument(
    "--source-format", 
    metavar="alpino|graphml",
    default="alpino", 
    help='format of source graphbanks (default is "alpino")')

parser.add_argument(
    "--target-format", 
    metavar="alpino|graphml",
    default="alpino", 
    help='format of target graphbanks (default is "alpino")')


parser.add_argument(
    "--source-tag",
    metavar="TAG",
    default="s", 
    help='value of "from_tag" in <link> elements (default is "s")')

parser.add_argument(
    "--target-tag",
    metavar="TAG",
    default="s", 
    help='value of "to_tag" in <link> elements (default is "s")')


parser.add_argument(
    "--relations",
    nargs="+",
    metavar="REL",
    default=RELATIONS,
    help='alignment relations (default is "%s")' % " ".join(RELATIONS))

parser.add_argument(
    "--max-token-len", 
    type=int, 
    metavar="N",
    default=99999, 
    help='maximum number of tokens allowed in either of the aligned sentences '
    '(default is 99999)')

parser.add_argument(
    "--min-token-diff", 
    type=int, 
    metavar="N",
    default=0, 
    help='minimum difference in tokens allowed between the aligned sentences '
    '(default is 0)')

args = parser.parse_args()

if len(args.parallel_text_corpora) != len(args.source_graphbanks):
    exit("Error: too few or to many source graphbanks")
    
if len(args.parallel_text_corpora) != len(args.target_graphbanks):
    exit("Error: too few or to many target graphbanks")
    

for text_corpus, source_graphbank, target_graphbank in zip(args.parallel_text_corpora,
                                                           args.source_graphbanks,
                                                           args.target_graphbanks):
    graph_corpus = pgc_from_ptc(
        text_corpus, 
        source_graphbank,
        target_graphbank,
        focus_tags=Pair(args.source_tag, args.target_tag),
        graph_formats=Pair(args.source_format, args.target_format),
        relations=args.relations,
        min_token_diff=args.min_token_diff,
        max_token_len=args.max_token_len)
    
    outfn = os.path.splitext(os.path.basename(text_corpus))[0] + ".pgc"
    graph_corpus.write(outfn, pprint=True)
    
    

