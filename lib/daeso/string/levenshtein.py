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
Levenshtein distance
"""

# levenshtein implementation orginally by Magnus Lie Hetland

__authors__ = "Magnus Lie Hetland, Erwin Marsi <e.marsi@gmail.com>"


def levenshtein(s1, s2):
    """"
    Calculates the Levenshtein distance between two sequences
    with uniform costs for insertion, deletion and substitution
    """
    # code from Magnus Lie Hetland
    n, m = len(s1), len(s2)
    if n > m:
        # Make sure n <= m, to use O(min(n,m)) space
        s1, s2 = s2, s1
        n, m = m, n
        
    current = range(n + 1)
    
    for i in range(1, m + 1):
        previous, current = current, [i] + [0] * n
        for j in range(1, n + 1):
            add, delete = previous[j] + 1, current[j-1] + 1
            change = previous[j - 1]
            if s1[j - 1] != s2[i - 1]:
                change = change + 1
            current[j] = min(add, delete, change)
            
    return current[n]


def normalized_levenshtein(s1, s2):
    """"
    Calculates the normalized Levenshtein distance between two sequences
    """
    # This only works when add/delete/substitute have uniform costs.
    # For the generalized case, see e.g.
    # Enrique Vidal, Andres Marzal, Pablo Aibar, 
    # "Fast Computation of Normalized Edit Distances"
    # IEEE Transactions On Pattern Analysis and Machine Intelligence,
    # 17(9), 1995
    try:
        return levenshtein(s1,s2) / float(max(len(s1), len(s2)))
    except ZeroDivisionError:
        return 0.0

