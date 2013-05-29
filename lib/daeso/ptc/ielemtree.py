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
provides the class IndexedElementTree, a subclass of ElementTree
as used in Hitaext
"""

__authors__ = "Erwin Marsi <e.marsi@gmail.com>"


from xml.etree.cElementTree import ElementTree


class IndexElemTree(ElementTree):
    '''
    An indexed ElementTree, where each element has attributes
    
    "_start" : start position of the corresponding text span 
    "_end" : end position of the corresponding text span 
    "_alignments" : list of aligned elements from another IndexElemTree instance
    "_n" : integer indicating this is the n-th occurrence of an element with this tag
    
    self.tagCountTable maps each tag T to a ordered list of elements tagged T,
    so we can easily access the n-th element with tag T
    
    self.tagIdTable  maps each tag T to a dict, which in turn maps id's to the elements tagged T,
    so we can easily access the element with tag T and a certain id
    '''

    def __init__(self, filename=None):
        ElementTree.__init__(self, file=filename)
        self.filename = filename
        
    def update(self, ignoreTags=[], newlineTags=[], blanklineTags=[]):
        '''
        set _start, _end, _alignments, and _n attributes,
        construct tagCountTable, tagIdTable
        and extract text
        '''
        # must be called each time the render settings change
        self.ignoreTags = ignoreTags
        self.newlineTags = newlineTags
        self.blanklineTags = blanklineTags
        # actually, tagCountTable stays the same,
        # but otherwise we have to make two passes on initialization
        self.tagCountTable = {}
        self.tagIdTable = {}
        self.text = self.index_elem(self.getroot())
        
    def index_elem(self, elem, start=0, ignore=False):
        '''
        assign absolute text positions to _start and _end attributes,
        initialize _alignment attribute to empty list,
        add element to tagCountTable,
        recursively index all daugter nodes,
        and return text corresponding to subtree rooted in elem
        '''
        try:
            self.tagCountTable[elem.tag].append(elem)
        except KeyError:
            self.tagCountTable[elem.tag] = [elem]
            
        try:
            self.tagIdTable[elem.tag][elem.get("id")] = elem
        except KeyError:
            self.tagIdTable[elem.tag] = {elem.get("id"): elem}
        
        # Add "_n" attribute to enable reverse lookup
        # Required when reading/writing the alignment
        # Counting starts at 1 (not zero)!    
        # NB Even if an element gets ignored,
        # we still need to traverse its children 
        # to get the tagCountTable and _n attributes right!
        elem.set("_n", len(self.tagCountTable[elem.tag]))
        
        # NB Even if an element gets ignored (invisible and thus not editable),
        # it may still have (old) alignments, 
        # so _alignment attribute is still needed!
        # In case of many element and few alignments
        # it may be better to create this attribute on the fly
        elem.set("_alignments", [])
        
        if ignore or elem.tag in self.ignoreTags: 
            for child in elem.getchildren():
                elem.set("_ignore", "true")
                self.index_elem(child, ignore=True)
                
            text = ""
        else:       
            # TODO: strips white space, which should be an option
            text = (elem.text or "").strip()
            
            for child in elem.getchildren():
                text += self.index_elem(child, start + len(text))
                
            elem.set("_start", start)
            elem.set("_end", start + len(text))
            
            if elem.tag in self.blanklineTags:
                text += '\n\n'    
            elif elem.tag in self.newlineTags:
                text += '\n'
        
        # don't forget possible tail text
        # even if elem is ignored
        text += (elem.tail or "").strip()
        
        return text
    
    def get_elem_text(self, elem):
        '''
        return all text contained in element
        '''
        # this is different from elem.text!
        return self.text[elem.get("_start", 0):elem.get("_end", 0)]
    
    

if __name__ == '__main__':    
    from sys import argv, stdout
    tree = IndexElemTree(file=argv[1])
    tree.update()
    # TODO: cannot write tree because _alignment attribute has non-string value
    # tree.write(stdout)
    