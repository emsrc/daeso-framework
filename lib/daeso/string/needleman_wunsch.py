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
# 
"""
Implementation of the NeedlemanâWunsch algorithm which performs a global alignment on two sequences.

@article{NeedlemanWunsch:1970,
	Author = {Needleman, S.B. and Wunsch, C.D.},
	Journal = {Journal of Molecular Biology},
	Pages = {443-453},
	Title = {A general method applicable to the search for similarities in the amino acid sequences of two proteins},
	Volume = {48},
	Year = {1970}}
"""

__authors__ = "Erwin Marsi <e.marsi@gmail.com>"

import sys


def needleman_wunsch(seq1, seq2, sim_score, gap_cost):
    """
    Description
    
        performs a global alignment of two sequences using the
        Needleman-Wunsch algorithm
    
    1st arg: seq1
    
        a iterable sequence (string, tuple, list)
        
    2nd arg: seq2
    
        a iterable sequence (string, tuple, list)
        
    3rd arg: sim_score
    
        a function which takes two arguments - an element form seq1 and an
        element from seq2 - and returns a numerical similarity score
        
    4th arg: gap_cost
    
        a function which takes as argument an element from seq1 or seq2 and
        returns a (negative) numerical cost for skipping this element

    Return value
    
        a tuple consistig of (1) a table where the keys are (i,j) indices
        of elements from seq1 and seq2, and the values are alignment scores;
        (2) a list of (i,j) indices of aligned elements from seq1 and seq2
        
    """
    # this is a straight-forward implementation - 
    # there is certainly room for improvement
    
    # The symbols from the steps are:
    # T = Terminate
    # D = Diagonal
    # U = Up
    # L = Left
    
    # create scoring matrix
    scores = {(0,0): (0, "T")}
    
    for i in range(1, len(seq1) + 1):
        scores[i, 0] = (gap_cost(seq1[i-1]) * i, "U")
    
    for j in range(1, len(seq2) + 1):
        scores[0, j] = (gap_cost(seq2[j-1]) * j, "L")
    
    for i in range(1, len(seq1) + 1):
        for j in range(1, len(seq2) + 1):
            scores[i, j] = max(
                (scores[i-1, j][0] + gap_cost(seq1[i-1]), "U"),
                (scores[i-1, j-1][0] + sim_score(seq1[i-1], seq2[j-1]), "D"),
                (scores[i, j-1][0] + gap_cost(seq2[j-1]), "L") )
    
    # backtrack to find (a) best solution
    i  = len(seq1)
    j  = len(seq2)
    alignment = []
    
    while i + j > 0:
        if scores[i,j][1] == "U":
            # Up
            i -= 1
        elif scores[i,j][1] == "D":
            # Diagonal
            # tricky: the score matrix has an initial row/column for the base
            # scores, which means that the actual sequence start at index 1, so we
            # have to subtract 1 from both i and j to return to zero-based
            # indexing
            alignment.insert(0, (i-1, j-1))
            i -= 1
            j -= 1
        elif scores[i,j][1] == "L":
            # Left
            j -= 1
            
    return scores, alignment


        
def print_scores(seq1, seq2, scores, stdout=sys.stdout, 
                 header="SCORE MATRIX\n\n", trailer="\n\n"):
    space1a = len(str(len(seq1))) + 1
    space1b = max([len(str(e)) for e in seq1]) + 1
    space1 = space1a + space1b
    space2 = max([len(str(e)) for e in seq2]) + 1
    space2 = max(space2, 7)
    
    stdout.write(header)      
    
    stdout.write(space1 * " " +
                 "".join([str(i).rjust(space2) for i in range(len(seq2) + 1)]) +
                 "\n")

    stdout.write(space1 * " " + 
                 space2 * " " +
                 "".join([str(e).rjust(space2) for e in seq2]) +
                 "\n")
                     
    for i in range(len(seq1) + 1):
        stdout.write(str(i).ljust(space1a))
        
        if i > 0:
            label = str(seq1[i-1])
        else:
            label = ""
            
        stdout.write(label.ljust(space1b))
        
        for j in range(len(seq2) + 1):
            s = "%d:%s" % scores[i,j]
            stdout.write(s.rjust(space2))
            
        stdout.write("\n")
        
    stdout.write(trailer)        
            
            
def print_alignment(seq1, seq2, alignment, stdout=sys.stdout, 
                    header="ALIGNMENT\n\n", trailer="\n\n"):
    space1a = len(str(len(seq1))) + 1
    space1b = max([len(str(e)) for e in seq1]) + 1
    space1 = space1a + space1b
    space2 = max([len(str(e)) for e in seq2]) + 1
    space2 = max(space2, len(str(len(seq2))) + 1)
    
    stdout.write(header)      
        
    print >>stdout, space1 * " " + "".join([str(i).rjust(space2) for i in range(len(seq2))])
    print >>stdout, space1 * " " + "".join([str(e).rjust(space2) for e in seq2])
                     
    for i, e1 in enumerate(seq1):
        stdout.write(str(i).ljust(space1a))
        stdout.write(str(e1).ljust(space1b))
        
        for j in range(len(seq2)):
            if (i,j) in alignment:
                s = "x"
            else:
                s = "."
            stdout.write(s.rjust(space2))

        print >>stdout
        
    stdout.write(trailer)      

            
            
        
        
    