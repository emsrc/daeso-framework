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
register of graphbank parsers

For each known graphbank format, defines a tuple with 
1. the name of the module containing the parser, and 
2. the name of the parser class.

Formats are assumed to be lower cased.
"""

__authors__ = "Erwin Marsi <e.marsi@gmail.com>"



graphml = ("daeso.gb.graphml", "GraphmlParser")
alpino  = ("daeso_nl.gb.alpinoparser", "AlpinoParser")