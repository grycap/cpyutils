# coding: utf-8
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
VERSION="0.20"

def get():
    global VERSION
    return VERSION

'''
CHANGELOG:

0.20    -   2016-01-28
    1. CONFIGURATION ENHANCEMENT
    The config accepts float values (they should be set as float in the default value in order to accept float values from
    the config file).

    2. ENHANCEMENT OF THE EVENTLOOP
    
    An enhanced eventloop is created. Now it is possible to create an eventloop that executes events on its time instead of
    steps of time. Moreover the code has been greatly enhanced.
    
    The previous version of eventloop is kept for compatibility with older apps. It is renamed eventloop0.
    
    3. LOGS
    
    Added the feature of including a timestamp in the logs, for ALL the logs using the Log class.

0.14    -   2015-12-15
    Including the iputils.py file

0.13
    Correcting one bug in runcommand
'''