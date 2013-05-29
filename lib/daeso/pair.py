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
generic Pair class for a pair of source and target items (strings, nodes,
graphs, ...)
"""

__authors__ = "Erwin Marsi <e.marsi@gmail.com>"



# used namedtuple before, but immutable attributes turned out to be
# inconvenient on a number of occassions

class Pair(object):
    """
    Pair of source and target objects
    """

    def __init__(self, source=None, target=None):
        self.set(source, target)
        
        
    def __eq__(self, other):
        if isinstance(other, Pair):
            return ( self.source == other.source and
                     self.target == other.target )
        
        
    def __repr__(self):
        return 'Pair(source={pair.source!r}, target={pair.target!r})'.format(
            pair=self) 
    
    
    def __str__(self):
        return 'Pair(source={pair.source}, target={pair.target})'.format(
            pair=self)
    
    
    def __iter__(self):
        return (role for role in (self.source, self.target))
    
    
    def set(self, source=None, target=None):
        self. source = source
        self.target = target
        
