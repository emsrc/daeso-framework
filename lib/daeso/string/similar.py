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
similarity measures on iterable sequences (strings, tuples, lists, dicts, sets)

Important assumptions:
- order is irrelvant
- mostly comparsion on level of types instead of level of tokens
- sequences are converted to sets, so items in sequence must immutable 
"""

__authors__ = "Erwin Marsi <e.marsi@gmail.com>"


import math


def type_match(seq1, seq2):
    """
    Return the number of identical types of two sequences, 
    which equals the lenght of the intersection when both sequences 
    are regarded as sets
    """
    # this is symmetric
    return len(set(seq1).intersection(seq2))


def token_match(seq1, seq2):
    """
    Return the number of tokens in seq1 which are also in seq2.
    Note that this relation is (potentially) asymmetric.
    """
    # Note that this relation is not symmetrical, i.e.
    # token_match(["a","a"], ["a"]) == 2 whereas
    # token_match(["a"], ["a", "a"]) == 1 !
    return len([e for e in seq1 if e in seq2])


def sym_token_match(seq1, seq2):
    """
    Return the symmetric token match of two sequences,
    wich is defined as:
    
    sym_token_match(seq1, seq2) = 
    
    token_match(seq1, seq2) + token_match(seq2, seq1)
    -------------------------------------------------
                            2
    """
    return  (token_match(seq1, seq2) + token_match(seq2, seq1)) / 2.0


def cosine(seq1, seq2):
    """
    return cosine of two sequences regarded as sets (types), 
    which is defined as
    
                         | intersection(seq1, seq2) | 
    cosine(seq1, seq2) = ----------------------------
                            sqrt(|seq1| * |seq2|)
    """
    intersection = set(seq1).intersection(seq2)
    
    try:
        return float(len(intersection)) / math.sqrt((len(seq1) * len(seq2)))
    except ZeroDivisionError:
        # one or more sequences empty 
        return 0.0
    
    
def tanimoto(seq1, seq2):
    """
    return tanimato coefficient of two sequences regarded as sets (types), 
    which is defined as
    
                                |intersection(seq1, seq2)| 
    tanimoto(seq1, seq2) = --------------------------------------------
                           |seq1| + |seq2| - |intersection(seq1, seq2)|
    """
    intersection = set(seq1).intersection(seq2)
    
    try:
        return float(len(intersection)) / (len(seq1) + len(seq2) - len(intersection))
    except ZeroDivisionError:
        # both sequences empty
        return 0.0
    
    
def dice(seq1, seq2):
    """
    return Dice coefficient of two sequences regarded as sets (types)
    which is defined as
    
                       2 * | intersection(seq1, seq2) | 
    dice(seq1, seq2) = --------------------------------
                             |seq1| + |seq2|)
    """
    intersection = set(seq1).intersection(seq2)
    
    try:
        return 2 * len(intersection) / float(len(seq1) + len(seq2))
    except ZeroDivisionError:
        # both sequences empty 
        return 0.0


def jaccard(seq1, seq2):
    """
    return Jaccard coefficient of two sequences regarded as sets (types)
    which is defined as
    
                         |intersection(seq1, seq2)|
    jaccard(seq1,seq2) = --------------------------
                            |union(seq1, seq2)|
    """
    union = set(seq1).union(seq2)
    intersection = set(seq1).intersection(seq2)
    
    try:
        return len(intersection) / float(len(union))
    except ZeroDivisionError:
        # both sequences empty 
        return 0.0
    
    
def overlap_min(seq1, seq2):
    """
    return overlap coefficient of two sequences
    normalized to the lenght of the shortest one
    """
    # same as type_match()
    intersection = set(seq1).intersection(seq2)
    
    try:
        return float(len(intersection)) / min(len(seq1), len(seq2))
    except ZeroDivisionError:
        # one or both sequences empty 
        return 0.0
    

def overlap_max(seq1, seq2):
    """
    return overlap coefficient of two sequences
    normalized to the lenght of the longest one
    """
    # same as type_match()
    intersection = set(seq1).intersection(seq2)
    
    try:
        return float(len(intersection)) / max(len(seq1), len(seq2))
    except ZeroDivisionError:
        # one or both sequences empty 
        return 0.0

# overlap_min is the common interpretation
overlap = overlap_min    


# ==============================================================================
# GENERALIZED VERSIONS
# ==============================================================================

def generalized_cosine(sequences):
    """
    return Cosine coefficient of multiple sequences
    """
    try:
        product = len(sequences[0])
        intersection = set(sequences[0])
    except IndexError:
        # sequences is empty
        return 0.0
    
    for seq in sequences[1:]:
        product *= len(seq)
        intersection.intersection_update(seq)
    
    try:
        return float(len(intersection)) / math.sqrt(product)
    except ZeroDivisionError:
        # one or more sequences empty
        return 0.0


def generalized_dice(sequences):
    """
    return Dice coefficient of multiple sequences
    """
    try:
        count = len(sequences[0])
        intersection = set(sequences[0])
    except IndexError:
        # sequences is empty
        return 0.0
    
    for seq in sequences[1:]:
        count += len(seq)
        intersection.intersection_update(seq)
    
    try:
        return float(len(sequences) * len(intersection)) / count
    except ZeroDivisionError:
        # all sequences empty
        return 0.0


def generalized_jaccard(sequences):
    """
    return Jaccard coefficient of multiple sequences
    """
    try:
        union = set(sequences[0])
        intersection = set(sequences[0])
    except IndexError:
        # sequences is empty
        return 0.0

    for seq in sequences[1:]:
        union.update(seq)
        intersection.intersection_update(seq)
            
    try:
        return len(intersection) / float(len(union))
    except ZeroDivisionError:
        # only empty sequences 
        return 0.0

            
    