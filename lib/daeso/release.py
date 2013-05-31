#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2007-2013 by 
# Erwin Marsi and TST-Centrale
#
#
# This file is part of the Algraeph program.
#
# The Algraeph program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# The Algraeph program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
Release data for DAESO Framework
"""

__author__ = "Erwin Marsi <e.marsi@gmail.com>"



name = "daeso"

version = "1.1"

description = """DAESO Framework is a Python framework for working 
with parallel treebanks"""

long_description = """DAESO Framework is a Python library developed in the
DAESO (Detecting And Exploiting Semantic Overlap) research project. It
supports working with collections (corpora/treebanks/graphbanks) of aligned
similar (parallel/comparable) text. It provides the foundation for the Hitaext
and Algraeph corpus annotation tools, and for the language-specific DAESO
Dutch library."""

author = "Erwin Marsi"

author_email = "e.marsi@gmail.com"

url = "https://github.com/emsrc/daeso-framework"

copyright = " TST-Centrale and Erwin Marsi"

license = "GNU Public License"

download_url = "https://github.com/emsrc/daeso-framework"

platforms = ["Linux", "Mac OS X", "MS Windows"]

keywords = [
    "graph alignment", 
    "tree alignment", 
    "parallel treebank",
    "parallel graphbank", 
    "parallel text", 
    "comparable text" ]

classifiers = [
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: GNU Public License (GPL)",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Text Processing :: Linguistic",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Topic :: Text Processing :: Linguistic",
        "Topic :: Text Processing :: Markup",
        "Natural Language :: English"
    ]

# Get date dynamically
import time
date = time.asctime()
del time
