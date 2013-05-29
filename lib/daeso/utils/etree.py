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
utility functions related to element tree
"""

__authors__ = "Erwin Marsi <e.marsi@gmail.com>"


import sys


def write(etree, file=sys.stdout, encoding="utf-8", pprint=False):
    """
    write element tree with xml header
    even when encoding is the default utf-8
    """
    if not hasattr(file, "write"):
        file = open(file, "wb")
        
    if pprint:
        indent(etree.getroot())
        
    file.write('<?xml version="1.0" encoding="utf-8"?>\n')
    etree.write(file, "utf-8")
    
 
def equals(elem1, elem2):
    """
    Test if two elements are equal in terms of tag, text, tail, attributes and
    recursively all their children. Heading/trailing whitespace is stripped
    before the comparison of texts and tails.
    """
    # as far as I can see, _ElementInterface lacks a __eq__ method
    return ( elem1.tag == elem2.tag and
             str(elem1.text).strip() == str(elem2.text).strip() and
             str(elem1.tail).strip() == str(elem2.tail).strip() and
             elem1.attrib == elem2.attrib and
             len(elem1) == len(elem2) and
             all([ equals(child1, child2)
                   for (child1, child2) in zip(elem1, elem2)]) )   


def indent(elem, level=0):
    """
    indent element and all subelements for pretty printing of XML 
    """
    # copied from Fredrik Lund 
    # http://effbot.python-hosting.com/file/effbotlib/ElementTree.py
    i = "\n" + level*"  "
    
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "  "
        for e in elem:
            indent(e, level+1)
        if not e.tail or not e.tail.strip():
            e.tail = i

    if level and (not elem.tail or not elem.tail.strip()):
        elem.tail = i
    