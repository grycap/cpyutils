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
VERSION="0.28"

def get():
    global VERSION
    return VERSION

'''
CHANGELOG:
0.28	-   2017-07-19
    Removing autosetup for logs as it was buggy
    Enhancing runcommand

0.27	-   2017-05-18
    Include the option of passing a stdin to the runcommand

0.26    -   2017-03-22
    Include new states in oneconnect to avoid failing in ONE 5.2 due to KeyError (issue #10)
    Enable to dump or not configuration vars when reading.

0.25	-   2016-10-06
    Correct one bug in iputils

0.24    -   2016-02-19
    Removing web.py from rpc_web, because its usage had performance issues: lots of simultaneous calls would make the server
    to hang.
    
    Using the current approach enables a simple web frontend, but it should not be used as a production web server. It should
    be used for testing purposes or simple local deployments.

	Logging also includes a well-known timestamp.

0.23    -   2016-02-02
    Setting the time of real time eventloop to absolute values, instead of local time (which were start time elapsed).
    
    Includes _Eventloop_RT0 and _Eventloop_RTT0 that create a local time basis (the time is refered to the time in which
    the eventloop is created).
    
    Logs are default to DEBUG
    
0.22    -   2016-02-01
    Corrected bug in Logs, now it sets the loglevel on creation time (as expected in previous __init__ parameters)
    
    Eventloop has asynchronous events that run on threads. Eventloop also has a new end-of-loop condition: the time in which
    no new events happen can be limited.

0.21    -   2016-01-29
    Creating fileutils.py that now includes utilities to interpret a csv formatted file.

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
