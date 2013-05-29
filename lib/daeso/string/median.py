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
set median string and generalized median string
"""

__authors__ = "Erwin Marsi <e.marsi@gmail.com>"


def set_median_string(strings, dist_func):
    """"
    select the set median string from a sequence of strings
    """
    # sum of distances
    sod = len(strings) * [0]
    
    for i in range(len(strings)):
        for j in range(i):
            d = dist_func(strings[i], strings[j])
            sod[i] += d
            sod[j] += d

            
    # alternatively:
    # return strings[sod.index(min(sod))]
    # which in theory requires two interations through the sod list
    
    i = 0
    min_sum = sod[i]
    
    for j in range(1, len(sod)):
        if sod[j] < min_sum:
            min_sum = sod[j]
            i = j
            
    return strings[i]



    
    
    
def generalized_median_string(strings):
    """
    calculate the generalized median string from a sequence of strings
    
    """
    pass