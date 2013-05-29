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
Implementation of the Smith-Waterman algorithm which performs a local alignment on two sequences.

@article{SmithWaterman:1981,
	Author = {Smith, TF and Waterman, MS},
	Journal = {Journal of Molecular Biology},
	Pages = {195--197},
	Title = {{Identification of Common Molecular Subsequences}},
	Volume = {147},
	Year = {1981}}
"""

__authors__ = "Erwin Marsi <e.marsi@gmail.com>"


import sys


def smith_waterman(seq1, seq2, sim_score, gap_cost):
    """
    Description
    
        performs a local alignment of two sequences using the
        Smith-Waterman algorithm
    
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
    
    # The matrix is represented as a dict where 
    # keys are (i,i) index pairs and
    # values are (score, step) tuples
    #
    # The symbols from the steps are:
    # T = Terminate
    # D = Diagonal
    # U = Up
    # L = Left
    
    # create scoring matrix
    scores = {(0,0): (0, "T")}
    
    # in contrast to Needleman-Wunsch, border values are initalized at zero
    for i in range(1, len(seq1) + 1):
        scores[i, 0] = (0, "U")
        
    for j in range(1, len(seq2) + 1):
        scores[0, j] = (0, "L")
    
    for i in range(1, len(seq1) + 1):
        for j in range(1, len(seq2) + 1):
            scores[i, j] = max(
                (scores[i-1, j][0] + gap_cost(seq1[i-1]), "U"),
                (scores[i-1, j-1][0] + sim_score(seq1[i-1],  seq2[j-1]), "D"),
                (scores[i, j-1][0] + gap_cost(seq2[j-1]), "L"),
                (0, "T")
                )
            
    # find highest score
    positives = [(score, pair) for (pair, score) in scores.items() if score[0] > 0]
    positives.sort()
    i,j = positives[-1][1]
    
    # backtrack to reconstruct (a) best alignment
    # start from highest score and stop when score is zero
    alignment = []
    
    while scores[i,j][0] > 0:
        
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
  