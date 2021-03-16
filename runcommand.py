# coding: utf-8
#
# CLUES Python utils - Utils and General classes that spin off from CLUES
# Copyright (C) 2017 - GRyCAP - Universitat Politecnica de Valencia
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

import subprocess
import logging
import time
import threading
import os
import signal

class CommandError(Exception):pass

# TODO: in case that we try to implement the simulator, we should reimplement the run_command apps to use timemachine and events
#       * it probably will not be needed, because the commands are supposed to not to fail in case that we are simmulating; this
#         this polling method is for production purposes
def _runcommand(command, shell=False, timeout = None, strin = None, cwd = None):
    try:
        p = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, cwd = cwd, stderr=subprocess.PIPE, shell=shell, preexec_fn = os.setsid)
    except Exception as e:
        if type(command)==list: command = " ".join(command)
        logging.error('Could not execute command "%s"' %command)
        raise

    timer = threading.Timer(timeout, os.killpg, [p.pid, signal.SIGKILL])
    timer.start()
    (out, err) = p.communicate(input=strin)
    timer.cancel()
    return (p.returncode, out, err)

def runcommand(command, shell = True, timeout = None, strin = None, cwd = None):
    cout = ""
    try:
        retcode, cout, cerr = _runcommand(command, shell, timeout, strin, cwd)
        if retcode != 0:
            if type(command)==list: command = " ".join(command)
            logging.error(' Error in command "%s"' % command)
            logging.error(' Return code was: %s' % retcode)
            logging.error(' Error output was:\n%s' % cerr)
            return False, cout
        else:
            return True, cout
    except OSError:
        logging.error("error executing command %s" % command)
        return False, cout
    return True, cout

def runcommand_e(command, shell = True, timeout = None, strin = None, cwd = None):
    cout = ""
    cerr = ""
    try:
        retcode, cout, cerr = _runcommand(command, shell, timeout, strin, cwd)
    except OSError:
        logging.error("error executing command %s" % command)
        return -1, cout, cerr
    return retcode, cout, cerr
