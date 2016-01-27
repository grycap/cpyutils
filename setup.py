#!/usr/bin/env python
#
# CLUES Python utils - Utils and General classes that spin off from CLUES
# Copyright (C) 2015 - GRyCAP - Universitat Politecnica de Valencia
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
# 

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup
import version

setup(name='cpyutils',
      version=version.get(),
      description='CLUES Python utils - Utils and General classes that spin off from CLUES',
      author='Carlos de Alfonso',
      author_email='caralla@upv.es',
      url='https://github.com/grycap/cpyutils',
      packages = [ 'cpyutils' ],
      package_dir = { 'cpyutils' : '.'},
      # download_url = "https://github.com/grycap/cpyutils/tarball/%s" % version.get(),
      py_modules = []
)
