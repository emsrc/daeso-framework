## -*- coding: utf-8 -*-
################################################################
## Author : Gaël Le Mignot
## Email : gael@pilotsystems.net
################################################################

__author__ = "gael@pilotsystems.net"
__format__ = "plaintext"
__version__ = "$Id: GenericCache.py 1269 2010-03-10 05:03:59Z emarsi $"

import time
from threading import RLock

from LRUStock import *
from decorators import *

_marker = []

class CacheNode(object):
    """
    A simple cache node

    A cache node must:
    - support hash and cmp, comparing and hashing the key
    - return a string key with the __str__ method
    """
    def __init__(self, key, value):
        self.key = key
        self.value = value

    def __str__(self):
        return str(self.key)

    def __hash__(self):
        return hash(str(self))

    def __cmp__(self, other):
        return cmp(str(self), str(other))

class GenericCache(dict):
    """
    This is a cache.
    """
    def __init__(self, maxsize = None, expiry = None, default_fail = False):
        """
        Constructor
         - Maxsize specify the maximal size of the cache
         - Expiry specify a maximal living time of an item inside the cache
         - If default_fail is True, the default behavior will be to raise
           an exception if not present in the cache
        """
        self.maxsize = maxsize
        self.expiry = expiry
        self.values = {}
        self.level = 0
        self.default_fail = default_fail

        # Least Recently Used objects
        self.lru = LRUStock()

        # Lock for synchronization
        self.lock = RLock()

    def _has_expired(self, value):
        """
        Internal method checking if a value expired
        """
        if self.expiry and value.__cache_timestamp + self.expiry < time.time():
            return True
        else:
            return False

    def _shrink(self, nb = 0):
        """
        Internal method: shrink cache until at least nb objects are free
        """
        if self.maxsize:
            while len(self) + nb > self.maxsize:
                self.remove(self.lru.pop())

    @synchronized
    def fetch(self, key, fail = None, onmissing = None):
        """
        Fetch a value
        """
        if fail is None:
            fail = self.default_fail
        
        key = str(key)
        if not self.values.has_key(key):
            if fail:
                raise KeyError, key
            return onmissing

        value = self.values[key]
        # Test for expiry
        if self._has_expired(value):
            self.remove(key)
            if fail:
                raise KeyError, key
            return onmissing
        self.lru.update(key)
        return value.value

    @synchronized
    def fetch_with_generator(self, key, generator, *args, **kwargs):
        """
        Fetch key, calling generator to build if it doesn't exist
        """
        res = self.fetch(key, onmissing = _marker)
        if res is _marker:
            res = generator(*args, **kwargs)
            self[key] = res
            
        return res
    
    @synchronized
    def remove(self, key):
        """
        Expire a value
        """
        key = str(key)
        if key in self.values:
            value = self.values[key]
            self.lru.discard(value)
            del self.values[key]    

    @synchronized
    def reconfigure(self, maxsize = None, expiry = None):
        """
        Reconfigure the cache settings
        """
        self.maxsize = maxsize
        self.expiry = expiry
        self._shrink()        

    @synchronized
    def insert(self, key, value = _marker):
        """
        Insert an object into the cache

        You can provide a CacheNode class, or directly a key and a value
        """
        if value is _marker:
            value = key
            
        if not isinstance(key, CacheNode):
            node = CacheNode(key, value)
        else:
            node = key

        if not key in self:
            self._shrink(1)
        
        node.__cache_timestamp = time.time()
        self.values[node] = node
        self.lru.add(node)

    @synchronized
    def clear(self):
        """
        Clear the whole cache
        """
        self.values.clear()
        self.lru.clear()

    @synchronized
    def collect(self):
        """
        Collect (remove) all obsoleted items, by default, the removal
        is done lazyly at first access
        """
        for key in self.values.keys():
            value = self.values[key]
            # Test for expiry
            if self._has_expired(value):
                self.remove(key)

    @synchronized
    def size(self):
        """
        Get the size of the cache (number of objects stored)
        """
        return len(self.values)
    
    # Hooks for dictionnary methods
    __getitem__ = fetch
    __setitem__ = insert
    __delitem__ = remove
    __len__ = size

    def keys(self):
        """
        Get stored keys
        """
        return [ key.key for key in self.values.keys() ]

    def has_key(self, key):
        """
        Do we have such key ?
        """
        return self.values.has_key(key)
    __contains__ = has_key

