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
import logging

_logsetup = False

class Log:
    '''
    This is a class that try to provide a simple utility to the common logging functions.
      * it tries to automate starting logging and setting the logging level to default (by default)
      * it returns the logging messages to enable more one-liners
    '''
    @staticmethod
    def setup(_filename = None, _loglevel = logging.DEBUG):
        logging.basicConfig(filename=_filename,level=_loglevel)
    
    def __init__(self, name = None, loglevel = logging.DEBUG):
        if name is None:
            self._logger = logging.getLogger()
        else:
            self._logger = logging.getLogger("[%s]" % name)
        self._filename = None
        
        global _logsetup
        if not _logsetup:
            Log.setup()
            _logsetup = True
    
    def setup_log(self, loglevel = logging.DEBUG):
        self._logger.setLevel(loglevel)
        
    def log(self, txt, loglevel = logging.DEBUG):
        if loglevel == logging.DEBUG:
            self._logger.debug(txt)
        elif loglevel == logging.INFO:
            self._logger.info(txt)
        elif loglevel == logging.WARNING:
            self._logger.info(txt)
        elif loglevel == logging.ERROR:
            self._logger.error(txt)
        else:
            self._logger.debug(txt)
        return txt
    
    def debug(self, msg):
        return self.log(msg, logging.DEBUG)
        
    def error(self, msg):
        return self.log(msg, logging.ERROR)

    def warning(self, msg):
        return self.log(msg, logging.WARNING)

    def info(self, msg):
        return self.log(msg, logging.INFO)