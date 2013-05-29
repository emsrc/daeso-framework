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
n-grams
"""

__authors__ = "Erwin Marsi <e.marsi@gmail.com>"




def n_gram_slices(tokens, n, pad_size=0, pad_string="_"):
    """
    Return a list of all n-grams occuring in the sequence tokens
    in the form of slices of tokens, where 
    pad_size is the size of padding before and after the tokens, and 
    pad_string is the string used for padding
    """
    padded_tokens = pad(tokens, pad_size, pad_string)
    return [padded_tokens[i:i+n] for i in range(len(padded_tokens) - n + 1)]


def n_gram_strings(tokens, n, pad_size=0, pad_string="_", separator=" "):
    """
    Return a list of all n-grams occuring in the sequence tokens
    in the form of substrings, where 
    pad_size is the size of padding before and after the tokens, 
    pad_string is the string used for padding, and
    separator is the string by which tokens are joined.
    """
    # this should be faster because it avoids a second iteration over ngram slices 
    # to join them into a string
    padded_tokens = pad(tokens, pad_size, pad_string)
    return [separator.join(padded_tokens[i:i+n]) for i in range(len(padded_tokens) - n + 1)]


def n_gram_slices_range(tokens, n_range, pad=False, pad_sizes=None,
                        pad_string="_"):
    """
    Return dictionary of n-gram slices for every n in nrange (see n_gram_slices).
    If pad is True, padding will occur acording to pad_sizes, which defaults to n-1.
    """
    if pad:
        if pad_sizes:
            assert len(n_range) == len(pad_sizes)
        else:
            pad_sizes = [n-1 for n in n_range]
    else:
        pad_sizes = len(n_range) * [0]
        
    n_gram_dict = {}
    
    for n, pad_size in zip(n_range, pad_sizes):
        n_gram_dict[n] = n_gram_slices(tokens, n, pad_size=pad_size,
                                       pad_string=pad_string)
        
    return n_gram_dict


def pad(tokens, pad_size, pad_string="_"):
    """ 
    Returns a padded version of the sequence tokens, where
    pad_size is the size of padding before and after the tokens, 
    pad_string is the string used for padding
    """
    if type(tokens) == type(tuple()):
        return pad_size * (pad_string,) + tokens + pad_size * (pad_string,)
    elif type(tokens) == type(""):
        return pad_size * pad_string + tokens + pad_size * pad_string
    else:
        return pad_size * [pad_string] + tokens + pad_size * [pad_string]
