#!/usr/bin/env python
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
distutils setup script for distributing the DAESO Framework
"""

# TODO:
# - docs, data and test are not installed when using bdist_wininst...

__authors__ = "Erwin Marsi <e.marsi@gmail.com>"


from distutils.core import setup
from imp import load_source
from glob import glob
from os import walk, path, remove
from os.path import basename, isdir, join, exists
from shutil import rmtree


# "from daeso import release" won't work 
release = load_source("release", "lib/daeso/release.py")


if exists('MANIFEST'): remove('MANIFEST')
if exists("build"): rmtree("build")

packages = [ root[4:] 
             for (root, dirs, files) in walk("lib") 
             if not ".svn" in root ]


def get_data_files(data_dir_prefix, dir):
    # data_files specifies a sequence of (directory, files) pairs 
    # Each (directory, files) pair in the sequence specifies the installation directory 
    # and the files to install there.
    data_files = []

    for base, subdirs, files in walk(dir):
        install_dir = join(data_dir_prefix, base)
        files = [ join(base, f) for f in files
                  if not f.endswith(".pyc") and not f.endswith("~") ]
        
        data_files.append((install_dir, files))

        if '.svn' in subdirs:
            subdirs.remove('.svn')  # ignore svn directories
                
    return data_files


# data files are installed under sys.prefix/share/pycornetto-%(version)
data_dir = join("share", "%s-%s" % (release.name, release.version))
data_files = [(data_dir, ['CHANGES', 'COPYING', 'INSTALL', 'README'])]
data_files += get_data_files(data_dir, "doc")
#data_files += get_data_files(data_dir, "data")

sdist_options = dict( 
    formats=["zip","gztar","bztar"])

setup(
    name = release.name,
    version = release.version,
    description = release.description,
    long_description = release.long_description, 
    license = release.license,
    author = release.author,
    author_email = release.author_email,
    url = release.url,
    requires = ["networkx"],
    provides = ["daeso (%s)" % release.version],
    package_dir = {"": "lib"},
    packages = packages,
    scripts = glob(join("bin","*.py")),
    data_files =  data_files,
    platforms = "POSIX, Mac OS X, MS Windows",
    keywords = release.keywords,
    classifiers = release.classifiers,
    options = dict(sdist=sdist_options)
)
