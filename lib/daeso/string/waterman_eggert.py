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
Implementation of the Waterman-Eggert algorithm which performs a local alignment on two sequences
and returns all non-intersecting alignments

@article{WatermanEggert:1987,
	Author = {M.S. Waterman and M. Eggert},
	Journal = {Journal of Molecular Biology},
	Pages = {723-728},
	Title = {A new algorithm for best subsequence alignments with applications 
                to tRNA-rRNA comparisons},
	Volume = {197},
	Year = {1987}}
"""

__authors__ = "Erwin Marsi <e.marsi@gmail.com>"


# TODO:
# - follow-up work describes a more efficient single-pass method to accomplish this
#   Geoffrey J. Barton (1993), "An efficient algorithm to locate all locally 
#   optimal alignments between two sequences allowing for gaps"

import sys
import needleman_wunsch


def waterman_eggert(seq1, seq2, sim_score, gap_cost, limit=None):
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
        
    keyword arg: limit
    
        an optional limit on the number of possible alignments to return
        (default is to return all)

    Return value
    
        a tuple of two lists: 
        (1) a list of tables representing the initial and recalculated matrices,
            where the keys are (i,j) indices of elements from seq1 and seq2, 
            and the values are the alignment scores;
        (2) an n-best list of lists representing all non-intersecting local alignment,
            where the sublist elements are indices of aligned elements from seq1 and seq2
    """
    # this is a straight-forward implementation - 
    # there is certainly room for improvement
    scores = make_matrix(seq1, seq2, sim_score, gap_cost)
    
    all_scores = []
    all_alignments = []
    
    while not limit or len(all_alignments) < limit:
        # find highest score
        best_score, best_pair = find_best_score(seq1, seq2, scores)
        
        # terminate when matrix is filled with zero's
        if not best_score:
            break
        
        # backtrack
        alignment = trace_alignment(scores, best_pair)
        
        # save current state
        # this is expensive for large matrices, 
        # so an option to disable it would be a good thing 
        all_scores.append(scores.copy())
        all_alignments.append(alignment[:])
        
        # recalculate affected part of the matrix
        recalculate_matrix(seq1, seq2, scores, sim_score, gap_cost, alignment)
            
    return all_scores, all_alignments


def make_matrix(seq1, seq2, sim_score, gap_cost):
    """
    build the score matrix
    """
    # The matrix is represented as a dict where 
    # keys are (i,i) index pairs and
    # values are (score, step) tuples
    #
    # The symbols for the steps are:
    # D = Diagonal
    # U = Up
    # L = Left
    # T = Terminate
    
    # create scoring matrix
    scores = {(0,0): (0, "T")}
    
    # in contrast to Needleman-Wunsch, border values are initalized at zero
    for i in range(1, len(seq1) + 1):
        scores[i, 0] = (0, "U")
        
    for j in range(1, len(seq2) + 1):
        scores[0, j] = (0, "L")
    
    for i in range(1, len(seq1) + 1):
        for j in range(1, len(seq2) + 1):
            scores[i, j] = max_score(seq1, seq2, i, j, scores, sim_score, gap_cost)
            
    return scores


def max_score(seq1, seq2, i, j, scores, sim_score, gap_cost):
    """
    find the step that maximizes the score
    """
    return max(
        (scores[i-1, j][0] + gap_cost(seq1[i-1]), "U"),
        (scores[i-1, j-1][0] + sim_score(seq1[i-1],  seq2[j-1]), "D"),
        (scores[i, j-1][0] + gap_cost(seq2[j-1]), "L"),
        (0, "T") # now here's the big innovation ;-)
    )


def find_best_score(seq1, seq2, scores):
    """
    find the highest score in the score matrix,
    resolving ties in a consistent way, and
    returning the best score and the best pair
    """
    # ties are resolved according to the following two rules
    # (cf. eq 5 and 6 in Waterman & Eggert paper)
    #
    # (1) If score[i,j] == score[k,l] and 
    #     i+j < k+l,
    #     then traceback from (i,j)
    # 
    # (2) If score[i,j] == score[k,l] and
    #     i+j == k+l and
    #     i < k,
    #     then traceback from (i,j)
    
    best_score = 0
    best_pair = (len(seq1) + 2, len(seq2) + 2) 
    
    # this might not be the shortest statement,
    # but certainly one the clearest
    for (pair, score) in scores.items():
        if score[0] < best_score:
            continue
        elif score[0] == best_score:
            if sum(best_pair) < sum(pair):
                continue
            elif sum(best_pair) == sum(pair):
                if best_pair[0] < pair[0]:
                    continue
                
        best_score, best_pair = score[0], pair
        
    return best_score, best_pair
    

def trace_alignment(scores, (i,j)):
    """
    backtrack from pair (i,j) in scores matrix
    to reconstruct the alignment
    """
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
            
    return alignment


def recalculate_matrix(seq1, seq2, scores, sim_score, gap_cost, alignment):
    """
    update the score matrix by assigning a zero score to all pairs in the alignment
    and recalculating the scores of all other pairs affected by this change
    """
    for (i,j) in alignment:
        # tricky: correct for the fact that the alignment is zero-based
        i += 1
        j += 1
        
        scores[i,j] = (0, "T")

        # recalculate scores for j-th column,
        # starting from row i+1 and continuing downwards until score does not change
        for k in range(i+1, len(seq1) + 1):
            ms = max_score(seq1, seq2, k, j, scores, sim_score, gap_cost)
            
            if ms == scores[k, j]:
                break
            else:
                scores[k,j] = ms

        # recalculate scores for i-th row,
        # starting from column j+1 and continuing downwards until score does not change
        for l in range(j+1, len(seq2) + 1):
            ms = max_score(seq1, seq2, i, l, scores, sim_score, gap_cost)
            
            if ms == scores[i, l]:
                break
            else:
                scores[i,l] = ms

                
def print_all_scores_and_alignments(seq1, seq2, all_scores, all_alignments):
    for scores, alignment in zip(all_scores, all_alignments):
        needleman_wunsch.print_scores(seq1, seq2, scores)
        needleman_wunsch.print_alignment(seq1, seq2, alignment)
        print alignment
        