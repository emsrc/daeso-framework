## -*- coding: utf-8 -*-
################################################################
## Author : Gaël Le Mignot
## Email : gael@pilotsystems.net
################################################################

__author__ = "gael@pilotsystems.net"
__format__ = "plaintext"
__version__ = "$Id: LRUStock.py 1269 2010-03-10 05:03:59Z emarsi $"

class LRUNode(object):
    """
    Node objects for LRUs
    """
    def __init__(self, item):
        """
        Constructor
        """
        self.prev = None
        self.next = None
        self.item = item

class LRUStock(object):
    """
    Hashed linked list object for LRUs
    Warning: this class is *not* synchronised, unlike the GenericCache class
    """
    def __init__(self):
        """
        Constructor
        """
        self.prev = self
        self.next = self
        self.keys = {}

    def update(self, item):
        """
        Get given value
        """
        self.discard(item)
        self.add(item)

    def discard(self, item):
        """
        Discard given object
        """
        if not item in self.keys:
            return
        node = self.keys[item]
        node.prev.next = node.next
        node.next.prev = node.prev        
        del self.keys[item]

    def add(self, item):
        """
        Add given object
        """
        node = LRUNode(item)
        self.keys[item] = node
        node.next = self
        node.prev = self.prev
        node.prev.next = node
        self.prev = node

    def pop(self):
        """
        Get the head of the list
        """
        if self.next is self:
            return None
        return self.next.item

    def __iter__(self):
        """
        Return an iterator to the ordered stock
        """
        item = self
        while item.next != self:
            item = item.next
            yield item.item

    def tolist(self):
        """
        Convert to list
        """
        return [ item for item in self ]

    def __str__(self):
        """
        Return as a string
        """
        s = []
        node = self.prev
        while node is not self:
            s.append(str(node.item))
            node = node.prev
        res = " <- ".join(s)
        s = []
        node = self.next
        while node is not self:
            s.append(str(node.item))
            node = node.next
        res += " / " + " -> ".join(s)
        return res

    def clear(self):
        """
        Clear the whole stock
        """
        self.keys.clear()
        self.next = self
        self.prev = self
        
    def size(self):
        """
        Get the size of the stock
        """
        return len(self.keys)
    
    __len__ = size
