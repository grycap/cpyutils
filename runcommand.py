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
# This version of ServerProxy created with the advise of contributors from
#   - http://stackoverflow.com/a/10012262
#   - http://stackoverflow.com/a/4791612

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
def _runcommand(command, shell=False, timeout = None):
    try:
        p = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=shell, preexec_fn = os.setsid)
    except:
        if type(command)==list: command = " ".join(command)
        logging.error('Could not execute command "%s"' %command)
        raise

    timer = threading.Timer(timeout, os.killpg, [p.pid, signal.SIGKILL])
    timer.start()
    (out, err) = p.communicate()
    timer.cancel()

    if p.returncode != 0:
        if type(command)==list: command = " ".join(command)
        logging.error(' Error in command "%s"' % command)
        logging.error(' Return code was: %s' % p.returncode)
        logging.error(' Error output was:\n%s' % err)
        raise CommandError()
    else:
        return out

def runcommand(command, shell = True, timeout = None):
    cout = ""
    try:
        cout = _runcommand(command, shell, timeout)
    except (CommandError, OSError):
        logging.error("error executing command %s" % command)
        return False, cout
    return True, cout
