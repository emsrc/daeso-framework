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
skip bigrams
"""

__authors__ = "Erwin Marsi <e.marsi@gmail.com>"


import sys
from daeso.string.ngram import pad


def skip_bigram_slices(tokens, distance_limit=sys.maxint):
    """
    Return a list of all skip bigrams in the token sequence
    in the form of slices of tokens, where 
    distance_limit is an optional limit to the maximal skip distance
    """
    # distance_limit corresponds to d_skip in Lin04
    # distance_limit=0 gives ordinary bigrams
    if tokens:
        return ( [(tokens[0], next_token) 
                  for next_token in tokens[1:2 + distance_limit]] +
                 skip_bigram_slices(tokens[1:], distance_limit) )
    else:
        return []


def padded_skip_bigram_slices(tokens, distance_limit=sys.maxint,
                              pad_string="_"):
    """
    Return a list of all skip bigrams in the token sequence
    in the form of slices of tokens, where 
    distance_limit is an optional limit to the maximal skip distance,
    pad_string is the string used for padding
    """
    return skip_bigram_slices(pad(tokens, 1, pad_string), 
                              distance_limit)
