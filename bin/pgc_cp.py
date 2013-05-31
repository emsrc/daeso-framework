#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
copy a parallel graph corpus

Automatically takes care of the internal references to graph bank files.
Usage is similar to the "cp" shell command.
"""

__authors__ = 'Erwin Marsi <e.marsi@gmail.com>'


from os.path import isdir, basename, join, samefile, exists
from sys import stderr

from daeso.utils.cli import DaesoArgParser
from daeso.pgc.corpus import ParallelGraphCorpus, LOAD_NONE

parser = DaesoArgParser(description=__doc__)
                        

parser.add_argument(
    "source",
    nargs="+",
    help="source parallel graph corpus file"
    )

parser.add_argument(
    "target",
    help="either a target parallel graph corpus file or "
    "a target directory"
    )

parser.add_argument(
    "-o", "--overwrite",
    action="store_true",
    help="overwrite existing file")

args = parser.parse_args()


if isdir(args.target):
    target_is_dir = True
else:
    target_is_dir = False
    
    if len(args.source) > 1:
        parser.print_usage()
        exit("error: too many arguments")
    
    
for source in args.source:
    if not exists(source):
        stderr.write("warning: source " + repr(source) + " does not exist "
                     "(not copied)\n")
        continue

    try:
        corpus = ParallelGraphCorpus(inf=source, graph_loading=LOAD_NONE)
    except Exception, inst:
        stderr.write(str(inst) + "\n")
        stderr.write("warning: source " + repr(source) + 
                     " is not a valid parallel graph corpus (not copied) \n")
        continue
    
    if isdir(args.target):
        target = join(args.target, basename(source))
    else:
        target = args.target
        
    if exists(target) and samefile(source, target):
        stderr.write("warning: source " + repr(source) + " and target " + 
                     repr(target) + " are the same file (not copied) \n")
        continue
     
    if exists(target) and not args.overwrite:
        stderr.write("warning: target " + repr(target) + "exists "
                     "(not copied); use --overwrite to force copy\n")
        continue
    
    corpus.write(outf=target)

