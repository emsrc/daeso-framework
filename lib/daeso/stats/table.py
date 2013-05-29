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
table for storing statistics 
"""

__authors__ = "Erwin Marsi <e.marsi@gmail.com>"



from sys import stdout

from daeso.thirdparty.odict import OrderedDict


class Column(list):
    
    def __init__(self, label="", type="count", descr="", size=0, 
                 overall=None, width=8, prec=2):
        list.__init__(self)
        self.label = label
        self.type = type
        self.descr = descr
        self.overall = overall
        self.width = 8
        self.prec = 2
        
        if size:
            self.grow(size)
            
            
    def grow(self, incr):
        if self.type == "count":
            self.extend(incr * [0])
        elif self.type == "string":
            self.extend(incr * [""])
        else:
            self.extend(incr * [0.0])
            
        
    def get_width(self, margin=2):
        assert self.type == "string"
        
        try:
            widest = max([len(e) for e in self])
        except ValueError:
            # columns is empty
            widest = 0
            
        return max(len(self.label), widest) + margin
    
    
    
        
class StatsTable(OrderedDict):
    
    def __init__(self, size=0):
        OrderedDict.__init__(self)
        
        for l in self.columns_def.split("\n"):
            l = l.strip().split()
            if l:
                self[l[0]] = Column(l[0], 
                                    l[1], 
                                    " ".join(l[2:]),
                                    size)
                
                
    def is_empty(self):
        """
        test if contains no data
        """
        for c in self.values():
            if len(c):
                return False
        else:
            return True
                
                
    def grow(self, incr):
        for c in self.values():
            c.grow(incr)
                
                
    def write(self, legenda=True, out=stdout):
        tot_width = lmargin = 0 # 12
        format = lmargin * " "
        overalls = "" # "OVERALL".ljust(lmargin)
        out.write(lmargin * " ")
        
        for c in self.values():
            if c.type == "string":
                w = c.get_width()
                out.write(c.label.ljust(w))
                format += "%-" + str(w) + "s"
            elif c.type == "count":
                w = c.width
                out.write(c.label.rjust(w))
                format += "%" + str(w) + "d"
            else:
                w = c.width
                out.write(c.label.rjust(w))
                format += "%" + str(w) + "." + str(c.prec) + "f"
                
            if c.overall is None:
                overalls += w * " "
            elif c.type == "count":
                overalls += ("%" + str(w) + "d") % c.overall
            else:
                overalls += ("%" + str(w) + "." + str(c.prec) + "f") % c.overall
                
            tot_width += w
                
        format += "\n"
        
        out.write("\n" + tot_width * "-" + "\n")
                
        for row in zip(*self.values()):
            out.write(format % row)
            
        out.write(tot_width * "-" + "\n" +
                  overalls + 3 * "\n" )
        
        if legenda:
            out.write("\n\n")
            self.write_legenda(out=out)
        
        
    def write_legenda(self, out=stdout):
        for i, col in enumerate(self.values()):
            out.write("%-4d%-8s%s\n" % (
            i + 1,
            col.label,
            col.descr))
                   
        
    def read(self, file):
        # doesn't read the summary
                
        if not hasattr(file, "read"):
            file = open(file, "r")
        
        sep_count = 0
        rows = []
            
        for l in file:
            if not l.strip():
                continue
            elif self.is_separator(l):
                sep_count += 1
                
                if sep_count == 2:
                    break
                else:
                    continue            
            elif sep_count == 1:
                # read body
                value_row = l.strip().split()
                
                for col, val in zip(self.values(), value_row):
                    if col.type == "string":
                        col.append(val)
                    elif col.type == "count":
                        col.append(int(val))
                    else:
                        col.append(float(val))
        else:
            raise EOFError("stats table truncated in file " + file.name)
                        
                        
    def is_separator(self, l):
        return l.startswith("----")
        

    def summarize(self):
        self.calc_count_overalls()
        self.calc_percent_overalls()
        self.calc_average_overalls()
        
                
    def calc_count_overalls(self):
        for c in self.values():
            if c.type == "count":
                c.overall = sum(c)
                
                
    def calc_percent_overalls(self):
        pass
    
    
    def calc_average_overalls(self):
        pass
    
    


def percent(a, b):
    return (a / float(b)) * 100

