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
Longest common subsequence
"""

__authors__ = "David Epstein, Erwin Marsi <e.marsi@gmail.com>"


# copied from LCS.py by D. Eppstein, March 2002.
# at http://www.ics.uci.edu/~eppstein/PADS/LCS.py
# (with minor reformatting)

# this returns the actual LCS
# there are probably faster algorithms which returns only a number
# see e.g. 
# L. Bergroth, H. Hakonen and T. Raita, 
# A Survey of Longest Common Subsequence Algorithms, 
# Proceedings of the Seventh International Symposium on 
# String Processing Information Retrieval(SPIRE), 2000. 

import math


def longest_common_subsequence(seq1, seq2):
    """
    Find longest common subsequence of iterables seq1 and seq2
    """
    # why convert to lists?
    ##seq1 = list(seq1)
    ##seq2 = list(seq2)

    # Fill dictionary lcsLen[i,j] with length of LCS of seq1[:i] and seq2[:j]
    lcsLen = {}
    for i in range(len(seq1) + 1):
        for j in range(len(seq2) + 1):
            if i == 0 or j == 0:
                lcsLen[i,j] = 0
            elif seq1[i-1] == seq2[j-1]:
                lcsLen[i,j] = lcsLen[i-1,j-1] + 1
            else:
                lcsLen[i,j] = max(lcsLen[i-1,j], lcsLen[i,j-1])

    # Produce actual sequence by backtracking through pairs (i,j),
    # using computed lcsLen values to guide backtracking
    i = len(seq1)
    j = len(seq2)
    LCS = []
    while lcsLen[i,j]:
        while lcsLen[i,j] == lcsLen[i-1,j]:
            i -= 1
        while lcsLen[i,j] == lcsLen[i,j-1]:
            j -= 1
        i -= 1
        j -= 1
        LCS.append(seq1[i])

    LCS.reverse()
    
    # output same type as input seq
    if type(seq1) == type(seq2) == type(""):
        return "".join(LCS)
    elif type(seq1) == type(seq2) == type(()):
        return tuple(LCS)
    else:
        # list
        return LCS
    
    
def normalized_lcs(seq1, seq2):
    """
    return the normalized lenght of the longest common subsequence 
    of iterables seq1 and seq2
    """
    try:
        return float(len(lcs(seq1, seq2))) / math.sqrt(len(seq1) * len(seq2))
    except ZeroDivisionError:
        return 0.0
    


lcs = longest_common_subsequence




