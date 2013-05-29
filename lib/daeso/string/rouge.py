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
Implementation of several of the rouge metrics as described in 
Lin, Chin-Yew, 'ROUGE: a Package for Automatic Evaluation of Summaries'. 
In: Proceedings of the Workshop on Text Summarization Branches Out (WAS 2004),
Barcelona, Spain, July 25 - 26, 2004. 
"""

__authors__ = "Erwin Marsi <e.marsi@gmail.com>"



import sys
from daeso.string.ngram import n_gram_slices
from daeso.string.lcs import longest_common_subsequence
from daeso.string.sgram import skip_bigram_slices


# TODO:
# ROUGE-W

# ==============================================================================
# ROUGE-N
# ==============================================================================

def rouge_n(candidate_tokens, reference_tokens_list, n):
    """
    Return the ROUGE-N score (aka N-gram co-occurrence statistic), where
    candidate_tokens is a sequence of candidate tokens,
    reference_tokens_list is a list of sequences of reference tokens, and
    and n stands for the lenght of the n-gram
    """
    # this is rouge-n on tokens
    candidate_ngrams = n_gram_slices(candidate_tokens, n)
    reference_ngrams = []
    
    for rt in reference_tokens_list:
        reference_ngrams += n_gram_slices(rt, n)
        
    return rouge_ngram(candidate_ngrams, reference_ngrams)


def rouge_ngram(candidate_ngrams, reference_ngrams):
    """
    return the ROUGE-N score (aka N-gram co-occurrence statistic), where
    candidate_ngrams is a list of all ngrams from the candidate,
    and reference_ngrams is a list of ngrams from the referernces
    """
    # this is rouge-n on ngrams
    try:
        return ( count_match(candidate_ngrams, reference_ngrams) / 
                 float(len(reference_ngrams)) )
    except ZeroDivisionError:
        return 0.0
    

def count_match(candidate_ngrams, reference_ngrams):
    """
    count the number of ngrams from candidate_ngrams 
    co-occurring in reference_ngrams
    """
    # this implements Count_match(gram_n) from Lin04, section 2
    # implementation might be slow for long lists
    return len([cng for cng in candidate_ngrams if cng in reference_ngrams])   
    

# ==============================================================================
# ROUGE-L
# ==============================================================================


def rouge_l(candidate_tokens, reference_tokens, beta=1):
    """
    Return the ROUGE-L score (longest common subsequence), where
    candidate_tokens is a sequence of candidate tokens,
    reference_tokens is a sequence of reference tokens, and
    beta determines the relative importance of recall in the F-measure
    """
    lcs = len(longest_common_subsequence(candidate_tokens, reference_tokens))
    recall = lcs / float(len(reference_tokens))
    precision = lcs / float(len(candidate_tokens))

    try:
        return ( ((1 + beta ** 2) * precision * recall )  /
                 (beta ** 2 * precision + recall) )
    except ZeroDivisionError:
        return 0


# ==============================================================================
# ROUGE-S
# ==============================================================================

def rouge_s(tokens1, tokens2, distance_limit=sys.maxint, beta=1):
    """
    Return the ROUGE-S score for token sequences tokens1 and tokens2, where
    distance_limit defines the maximal skip distance, and
    beta determines the relative importance of recall in the F-measure, 
    """
    # implementation based on section 5 from Lin04
    skip_bigrams1 = skip_bigram_slices(tokens1, distance_limit) 
    skip_bigrams2 = skip_bigram_slices(tokens2, distance_limit)
    
    return rouge_skip_bigram(skip_bigrams1, skip_bigrams2, beta)


def rouge_skip_bigram(skip_bigrams1, skip_bigrams2, beta=1):
    """
    Return the ROUGE-S score for two lists of skip bigrams, where
    beta determines the relative importance of recall in the F-measure
    """
    matches = set(skip_bigrams1).intersection(set(skip_bigrams2))
    # matches_count corresponds to SKIP2(X,Y) in Lin04
    # It is defined as "the number of skip bigram matches between X and Y"-
    # However, it is not clear what to do with multiple occurrences of the same bigram.
    # For instance, does SKIP([a,a], [a]) equal 1 or 2? Does it equal SKIP([a], [a, a])? 
    # In the current implementation, X and Y are effectively considered sets (i.e. no duplicates). 
    matches_count = float(len(matches))
    
    recall = matches_count / len(skip_bigrams1)
    precision = matches_count / len(skip_bigrams2)
    
    try:
        return ( ((1 + beta ** 2) * precision * recall )  /
                 (beta ** 2 * precision + recall) )
    except ZeroDivisionError:
        return 0
    
    
# ==============================================================================
# ROUGE-SU
# ==============================================================================

def rouge_su(tokens1, tokens2, distance_limit=sys.maxint, 
             beta=1, marker="_"):
    """
    Return the ROUGE-SU score for token sequences tokens1 and tokens2, where
    distance_limit defines the maximal skip distance,
    beta determines the relative importance of recall in the F-measure, and
    marker is the begin-of-sentence marker (which must be different from any other token)
    """
    # Implementation based on section 5 from Lin04, in particular
    # "We can also obtain ROUGE-SU from ROUGE-S by adding a begin-of-sentence marker
    # at the beginning of candidate and reference sentences."
    # Note however that distance_limit may interfere with this trick!
    return rouge_s((marker,) + tokens1, (marker,) + tokens2,
                   distance_limit, beta)
