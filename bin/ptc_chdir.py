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
change directory of source and target files in parallel text corpora
"""


__authors__ = 'Erwin Marsi <e.marsi@gmail.com>'


from glob import glob
from os.path import basename, join
from sys import stdout, stderr
from string import uppercase

from daeso.utils.cli import ArgumentParser
from daeso.ptc.document import HitaextDoc


parser = ArgumentParser(description=__doc__)

parser.add_argument(
    "corpus",
    nargs="+",
    default="parallel text corpus",
    help=""
    )

parser.add_argument(
    "-d", "--dir",
    default="",
    help="new directory for source and target files "
    "(defaults to none, which means stripping the existing directory)"
    )

parser.add_argument(
    "-t", "--test",
    action="store_true",
    help="perform a dry run without actually changing the files (implies -v)"
    )


parser.add_argument(
    "-V", "--verbose",
    action="store_true",
    help="verbose output"
    )


args = parser.parse_args()


for fn in args.corpus:
    if args.verbose or args.test:
        print >>stderr, "Reading Hitaext document", fn
        
    htdoc = HitaextDoc(file=fn)
    
    for side in ("from", "to"):
        path = htdoc.get_filename(side)
        
        if args.verbose or args.test:
            print >>stderr, "Current %s path is %s" %  (side, path)
        
        # a heuristic to deal with windows paths        
        if path[0] in uppercase and path[1] == ":":
            # strip drive letter
            path = path[2:]
        path = path.replace("\\", "/")
        
        path = join(args.dir, basename(path))
        
        if args.verbose or args.test:
            print >>stderr, "Changing %s path to %s" %  (side, path)
        
        if not args.test:
            htdoc.set_filename(side, path)
        
    if args.verbose and not args.test:
        print >>stderr, "Writing Hitaext document\n", fn
    
    if not args.test:
        htdoc.write(fn)
