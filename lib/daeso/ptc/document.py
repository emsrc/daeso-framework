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
Hitaext document
"""

__authors__ = "Erwin Marsi <e.marsi@gmail.com>"



from xml.etree.cElementTree import Element, ElementTree, XML

from daeso.ptc.ielemtree import IndexElemTree
from daeso.pair import Pair

from os.path import basename, dirname, exists, join
    

    
class HitaextDoc(ElementTree):
    '''
    Hitaext XML document as an ElementTree
    '''
    
    _hitaext_template = '''
    <hitaext>
        <from>
            <filename />
            <render>
                <font />
                <elements />
            </render>
        </from>
        <to>
            <filename />
            <render>
                <font />    
                <elements />
            </render>
        </to>
        <alignment />
    </hitaext>
    '''
    
    
    def __init__(self, element=None, file=None):
        ElementTree.__init__(self, element=element, file=file)
        
        if element or file:
            self.validate()
        else:
            xml = "".join(self._hitaext_template.split())
            self._setroot(XML(xml))
        
        if file:
            self.filename = file
        else:
            self.filename = ""
            
        self.alignment = self.find('/alignment')
            
        
    def validate(self):
        '''
        test XML for minimal requirements
        '''
        assert self.get_filename('from'), AssertionError('invalid source filename')
        assert self.get_filename('to'), AssertionError('invalid target filename')
        
        
    def get_filename(self, side, search=False):
        fn = self.find('/%s/filename' % side).text.strip()
        
        # this still won't work with a windows path
        if search:
            for p in (
                fn,
                # relative path
                join(dirname(self.filename), fn),
                # ignore path, just search in same dir as hitaext document
                join(dirname(self.filename), basename(self.filename)) 
            ):
                if exists(p):
                    return p
            
        return fn
    
    
    def set_filename(self, side, filename):
        self.find('/%s/filename' % side).text = filename

        
    def get_pseudo_root(self, side):
        return self.find('/%s/render/elements' % side).get("pseudo_root")

    
    def set_pseudo_root(self, side, tag):
        self.find('/%s/render/elements' % side).set("pseudo_root", tag)

        
    def get_pseudo_root_tags(self, side):
        return [c.tag for c in self.find('/%s/render/elements' % side).getchildren() 
                if c.get('uniq') == 'True']

    
    def get_elem_tags(self, side):
        return [c.tag for c in self.find('/%s/render/elements' % side).getchildren()]

    
    def get_elem(self, side, tag):
        return self.find('/%s/render/elements/%s' % (side, tag))

    def get_elem_dict(self, side, tag): 
        """
        return a dict mapping tags to elements in the <render> section
        """
        return dict([(c.tag, c) for c in self.find('/%s/render/elements' % side).getchildren()])
    
    def add_elem(self, side, tag):
        e = self.default_elem(tag)
        self.find('/%s/render/elements' % side).append(e)
        return e

    
    def default_elem(self, tag):
        return Element(tag,
                       ignore = 'False',
                       skip = 'False',
                       newline = 'False',
                       blankline = 'False')

    
    def init_elems(self, side, tree):
        seen_tags = {}
        
        for elem in tree.getiterator():
            if not elem.tag in seen_tags:
                new_elem = self.add_elem(side, elem.tag)
                new_elem.set('uniq','True')
                seen_tags[elem.tag] = new_elem
            else:
                seen_tags[elem.tag].set('uniq', 'False')
        
        pseudo_root = tree.getroot().tag
        self.set_pseudo_root(side, pseudo_root)
        
        
    def get_tags(self, side, attrib):
        """
        return a list tags where value for attribute is True
        """
        return [c.tag for c in self.find("/%s/render/elements" % side).getchildren() if c.get(attrib) == "True"]
    
    def write(self, file, encoding="utf-8"):
        """
        write to file
        """
        # ElementTree.write does not write the XML header
        # if the encoding is utf-8
        if not hasattr(file, "write"):
            file = open(file, "w")
        print >>file, '<?xml version="1.0" encoding="utf-8"?>'
        ElementTree.write(self, file, "utf-8")
    
    #===============================================================================
    # document tree methods
    #===============================================================================
        
    def get_doc_tree(self, side, search=False):
        """
        Get the document tree where side is either 'from' or 'to'.
        Returns an instance of IndexElemTree. 
        """
        fn = self.get_filename(side, search)
        return IndexElemTree(fn)   
    
    
    def get_doc_trees(self, search=False, update=True):
        """
        Get pair of document trees
        """
        from_tree = self.get_doc_tree("from", search=search)
        to_tree = self.get_doc_tree("to", search=search)
        
        if update:
            from_tree.update()
            to_tree.update()
            
        return Pair(from_tree, to_tree)
        
        
    #===============================================================================
    # alignment methods
    #===============================================================================

    alignments_methods = ("n", "id")
    
    def set_alignment_method(self, method="n"):
        if method in self.alignments_methods:
            method = self.alignment.set("method", method)
        else:
            raise AssertionError("Unknown alignment method: %s" % method)
        
        
    def get_alignment_method(self):
        return self.alignment.get("method") 
        
        
    def clear_alignments(self):
        self.alignment[:] = []

        
    def add_n_alignment(self, from_tag, from_n, to_tag, to_n):
        self.alignment.append(Element('link', 
                                      from_tag=from_tag, from_n=str(from_n),
                                      to_tag=to_tag, to_n=str(to_n)))
        
        
    def add_id_alignment(self, from_tag, from_id, to_tag, to_id):
        self.alignment.append(Element('link', 
                                      from_tag=from_tag, from_id=from_id,
                                      to_tag=to_tag, to_id=to_id))

        
    def get_alignments(self):
        return self.alignment
    
    
    def inject_alignments(self, from_tree, to_tree):
        '''
        Update the _alignments attributes in both document trees
        according to the links in the <alignments> section
        of the Hitaext XML document
        '''
        method = self.get_alignment_method()
        
        if method in  ("n", None):
            self.inject_alignments_n(from_tree, to_tree)
        elif method == "id":
            self.inject_alignments_id(from_tree, to_tree)
        else:
            raise AssertionError("Unknown alignment method: %s" % method)
        
        
    def inject_alignments_n(self, from_tree, to_tree):
        '''
        Update the _alignments attributes in both document trees
        according to the links in the <alignments> section
        of the Hitaext XML document,
        based on the "from_n" and "to_n" attributes.
        '''
        # Assume "_alignments" attribute is initialized with empty list
        for elem in self.alignment:
            fromTag = elem.get('from_tag')
            fromN = int(elem.get('from_n'))
            # fromN/toN counts from 1 -- tagCountTable counts from zero!!! 
            fromElem = from_tree.tagCountTable[fromTag][fromN - 1]
            
            toTag = elem.get('to_tag')
            toN = int(elem.get('to_n'))
            # fromN/toN counts from 1 -- tagCountTable counts from zero!!! 
            toElem = to_tree.tagCountTable[toTag][toN - 1]
            
            fromElem.get("_alignments").append(toElem)
            toElem.get("_alignments").append(fromElem)    

    
    def inject_alignments_id(self, from_tree, to_tree):
        '''
        Update the _alignments attributes in both document trees
        according to the links in the <alignments> section
        of the Hitaext XML document,
        based on the "from_id" and "to_id" attributes.
        '''
        # Assume "_alignments" attribute is initialized with empty list
        for elem in self.alignment:
            fromTag = elem.get('from_tag')
            fromId = elem.get('from_id')
            fromElem = from_tree.tagIdTable[fromTag][fromId]
            
            toTag = elem.get('to_tag')
            toId = elem.get('to_id')
            toElem = to_tree.tagIdTable[toTag][toId]
            
            fromElem.get("_alignments").append(toElem)
            toElem.get("_alignments").append(fromElem)    
            
            
    def extract_alignments(self, from_tree, to_tree):
        '''
        Replace the links in the <alignments> section
        of the Hitaext XML document according to 
        the _alignments attributes in both document trees
        '''
        method = self.alignment.get("method") 
        
        if method in  ("n", None):
            self.extract_alignments_n(from_tree, to_tree)
        elif method == "id":
            self.extract_alignments_id(from_tree, to_tree)
        else:
            raise AssertionError("Unknown alignment method: %s" % method)
        
        
    def extract_alignments_n(self, from_tree, to_tree):
        '''
        Replace the links in the <alignments> section
        of the Hitaext XML document according to 
        the _alignments attributes in both document trees
        using "from_n" and "to_n" attributes.
        '''
        self.clear_alignments()
        
        for fromElem in from_tree.getiterator():
            for toElem in fromElem.get("_alignments", []):
                self.add_n_alignment(fromElem.tag, fromElem.get("_n"), 
                                     toElem.tag, toElem.get("_n"))
                
                
    def extract_alignments_id(self, from_tree, to_tree):
        '''
        Replace the links in the <alignments> section
        of the Hitaext XML document according to 
        the _alignments attributes in both document trees
        using "from_id" and "to_id" attributes.
        '''
        self.clear_alignments()
        
        for fromElem in from_tree.getiterator():
            for toElem in fromElem.get("_alignments", []):
                self.add_id_alignment(fromElem.tag, fromElem.get("id"), 
                                      toElem.tag, toElem.get("id"))
        
        
    

if __name__ == '__main__':
    import sys
    doc = HitaextDoc()
    from_tree = ElementTree(file=sys.argv[1])
    doc.set_filename('from', sys.argv[1])
    doc.init_elems('from', from_tree)
    to_tree = ElementTree(file=sys.argv[2])
    doc.set_filename('to', sys.argv[2])
    doc.init_elems('to', to_tree)
    doc.validate()
    doc.add_n_alignment("p", "1", "p", "2")
    doc.get_elem('from', 'p').set('blankline', 'True')
    doc.write(sys.stdout)
