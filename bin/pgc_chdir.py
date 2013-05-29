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
change prefix of path to graph bank files in parallel graph corpora

Example:
  pgc_chdir.py -p ../gb ../../gb *.pgc 
"""


__authors__ = 'Erwin Marsi <e.marsi@gmail.com>'


from glob import glob
from sys import stderr
from xml.etree.cElementTree import ElementTree, tostring

from daeso.utils.cli import DaesoArgParser
from daeso.utils.etree import write


# TODO:
# - this is not too smart yet - you can do this with sed, 
#   but escaping all the slashes is a pain
# - windows support


parser = DaesoArgParser(description=__doc__, version=__revision__)
                        

parser.add_argument(
    "corpus",
    nargs="+",
    help="parallel graph corpus"
    )

parser.add_argument(
    "-p", "--path-prefix-pair",
    nargs=2,
    default=["", ""],
    metavar="DIR",
    help="a pair of path prefixes specifying what to change from and to"
    )

parser.add_argument(
    "-t", "--test",
    action="store_true",
    help="perform a dry run without changing anything for real (implies -V)"
    )


parser.add_argument(
    "-V", "--verbose",
    action="store_true",
    help="verbose output"
    )


args = parser.parse_args()


for fn in args.corpus:
    if args.verbose or args.test:
        print >>stderr, "Reading parallel graph corpus", fn
        
    # using plain ET instead of pgc Corpus class,
    # because of all the overhead of reading the treebanks etc.
    tree = ElementTree(file=fn)
        
    for file_el in tree.findall("//file"):
        from_path, to_path = args.path_prefix_pair
        
        if file_el.text.startswith(from_path):
            if args.verbose or args.test:
                print >>stderr, "  Changing ", tostring(file_el).strip()

            i = len(from_path)
            file_el.text = to_path + file_el.text[i:]
            
            if args.verbose or args.test:
                print >>stderr, "  to       ", tostring(file_el).strip()
            
    if args.verbose and not args.test:
        print >>stderr, "Writing parallel graph corpus", fn
        
    if not args.test:
        write(tree, fn)
        
