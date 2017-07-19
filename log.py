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

# This avoids the error of recursive import
try: import eventloop
except: pass

_include_timestamp = False

def include_timestamp(include = True):
    global _include_timestamp
    _include_timestamp = include

class Log:
    '''
    This is a class that try to provide a simple utility to the common logging functions.
      * it tries to automate starting logging and setting the logging level to default (by default)
      * it returns the logging messages to enable more one-liners
    '''
    @staticmethod
    def setup(_filename = None, _loglevel = logging.DEBUG):
        logging.basicConfig(filename=_filename,level=_loglevel, format = "%(name)10s;%(levelname)5s;%(asctime)s;%(message)s")
    
    def __init__(self, name = None, loglevel = logging.DEBUG):
        if name is None:
            self._logger = logging.getLogger()
        else:
            self._logger = logging.getLogger("[%s]" % name)
        self._filename = None
        self._logger.setLevel(loglevel)
        
    def setup_log(self, loglevel = logging.DEBUG):
        self._logger.setLevel(loglevel)
        
    def log(self, txt, loglevel = logging.DEBUG, exc_info = None):
        global _include_timestamp
        if _include_timestamp:
            txt = "%.3f;%s" % (eventloop.now(), txt)
        if loglevel == logging.DEBUG:
            self._logger.debug(txt)
        elif loglevel == logging.INFO:
            self._logger.info(txt)
        elif loglevel == logging.WARNING:
            self._logger.info(txt)
        elif loglevel == logging.ERROR:
            self._logger.error(txt, exc_info=exc_info)
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

    def exception(self, msg):
        # Pass the exception information using the keyword argument exc_info=true
        return self.log(msg, logging.ERROR, exc_info=True)
