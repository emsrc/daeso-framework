## -*- coding: utf-8 -*-
################################################################
## Author : Gaël Le Mignot
## Email : gael@pilotsystems.net
################################################################

__author__ = "gael@pilotsystems.net"
__format__ = "plaintext"
__version__ = "$Id: decorators.py 1269 2010-03-10 05:03:59Z emarsi $"

def default_marshaller(func, *args, **kwargs):
    """
    Default marshaller
    """
    return repr((func.__name__, args, kwargs))

def cached(cache, marshaller = default_marshaller):
    """
    This is a decorator that cache results according to parameters

    The marshaller computes a key from function arguments
    """
    def decorator(func):
        def inner(*args, **kwargs):
            key = marshaller(func, *args, **kwargs)

            return cache.fetch_with_generator(key, func, *args, **kwargs)
            
        return inner
    return decorator

def verbose(func):
    """
    Decorator to print debug stuff - use it only on python >= 2.4
    """
    def verbose_func(self, *args, **kwargs):
        print "  " * self.level, "==> Entering: %s(*%r, **%r)" % (func.__name__, args, kwargs)
        self.level += 1
        print "  " * self.level, self.lru
        res = func(self, *args, **kwargs)
        print "  " * self.level, self.lru
        self.level -= 1
        print "  " * self.level, "==> Leaving %s: %r" % (func.__name__, res)
        return res
    return verbose_func

def synchronized(func):
    """
    Synchronize a method using internal lock object, a decorator
    """
    def inner(self, *args, **kwargs):
        """
        The inner function
        """
        self.lock.acquire()
        try:        
            return func(self, *args, **kwargs)
        finally:
            self.lock.release()
    return inner

