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
some utility function for performing operating system tasks
"""

__authors__ = "Erwin Marsi <e.marsi@gmail.com>"



import os
import glob as _glob

def makedirs(path, mode=0777):
    """
    a version of os.makedirs which raises no exception when the dir already
    exists
    """
    try:
        os.makedirs(path, mode)
    except OSError, inst:
        if inst.errno == 17:
            # dir already exists
            pass
        
        
def glob(pattern):
    """
    a version of glob which returns a sorted list of filenames
    """
    filenames = _glob.glob(pattern)
    filenames.sort()
    return filenames


def multiglob(patterns):
    """
    glob for multiple patterns and return a sorted list of filenames
    """
    filenames =  [ fn 
                   for pat in patterns 
                   for fn in _glob.glob(pat) ]
    filenames.sort()
    return filenames
