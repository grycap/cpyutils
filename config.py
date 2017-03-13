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

import glob
import logging
import os

_ETC_PATHS = [ '/etc/' ]
_MAIN_CONFIG_FILE = "app.cfg"
_CONFIG_VAR_INCLUDE = ""
_CONFIG_FILTER = "*.cfg"

def set_paths(etc_paths = [ "/etc/" ]):
    """
        Sets the paths where the configuration files will be searched
        
        * You can have multiple configuration files (e.g. in the /etc/default folder
        and in /etc/appfolder/)
    """
    global _ETC_PATHS
    _ETC_PATHS = []
    for p in etc_paths:
        _ETC_PATHS.append(os.path.expanduser(p))
    
def set_main_config_file(c_file):
    """
        Sets the name of the main configuration file. This file will be searched
        in the configuration folders (see function "set_paths")
    """
    global _MAIN_CONFIG_FILE
    _MAIN_CONFIG_FILE = c_file
    
def set_config_filter(config_var_include = "CONFIG_DIR", filter_ = "*.cfg"):
    """
        Sets the filter of other configuration files to include as configuration files.
        You can set also the subfolder that should contain these files (it should be
        a subfolder of one of the folders set with "set_paths")
    """
    global _CONFIG_VAR_INCLUDE, _CONFIG_FILTER
    _CONFIG_VAR_INCLUDE = config_var_include
    _CONFIG_FILTER = filter_

_LOGGER = logging.getLogger("[CONFIG]")

def config_filename(filename):
    """
        Obtains the first filename found that is included in one of the configuration folders.
        This function returs the full path for the file.
        
        * It is useful for files that are not config-formatted (e.g. hosts files, json, etc.)
          that will be read using other mechanisms
    """
    global _ETC_PATHS
    if filename.startswith('/'):
        _LOGGER.info("using absolute path for filename \"%s\"" % filename)
        return filename

    import os.path
    for fpath in _ETC_PATHS:
        current_path = "%s/%s" % (fpath, filename)
        if os.path.isfile(current_path):
            current_path = os.path.realpath(current_path)
            _LOGGER.info("using path \"%s\" for filename \"%s\"" % (current_path, filename))
            return current_path

    _LOGGER.info("using path \"%s\" for filename \"%s\"" % (filename, filename))
    return filename

def read_config(section, variables, sink, filename = None, logvars = False):
    """
        This functions creates a dictionary whose keys are the variables indicated in
        'variables' with the values obtained from the config filenames set for this module.
        
        'variables' is a dictionary of variable names and default values { 'VAR1': defaultval1, ...}
        
        The value for the variables is searched under the 'section' section from the configuration
        files (all the configuration files: the main one and those included by the config_filter
        mechanism)
        
        Sink is a dictionary (or object) that admits each of the variables to be created and set
        the value.
    """
    global _ETC_PATHS
    import ConfigParser
    config = ConfigParser.ConfigParser()
    
    if filename is None:
        config_files = existing_config_files()
    else:
        config_files = []
        for fpath in _ETC_PATHS:
            config_files.append("%s/%s" % (fpath, filename))
    
    config.read(config_files)

    options = {}
    if section in config.sections():
        options = config.options(section)

    for varname, value in variables.items():
        orig_varname = varname
        varname = varname.lower()
        if varname in options:
            try:
                if isinstance(value, bool):
                    value = config.getboolean(section, varname)
                elif isinstance(value, int):
                    value = config.getint(section, varname)
                elif isinstance(value, float):
                    value = config.getfloat(section, varname)
                else:
                    value = config.get(section, varname)
                    if len(value) > 0:
                        value = value.split("#")[0].strip()
            except:
                raise Exception("Invalid value for variable %s in config file" % orig_varname)
                
        varname = varname.upper()
        sink.__dict__[varname] = value
        if (logvars):
            _LOGGER.debug("%s=%s" % (varname, str(value)))

class Configuration():
    """
        Class that reads the configuration for a set of variables, from one configuration file
        (or all the configuration files established using the other methods in this module).
        
        e.g.
        
        my_config = Configuration( 'GENERAL',
                {   'VAR1': 0,
                    'VAR2': 'default2' } )   
    """
    def __init__(self, section, variables, filename = None, callback = None):
        read_config(section, variables, self, filename)
        if callback is not None:
            callback(self)

    """
    This function is used to map the standard log level values from the string to the logging variable value
    """
    def maploglevel(self, varname):
        import logging
        self.mapvalues(varname,
            {
                "debug": logging.DEBUG,
                "info": logging.INFO,
                "warning": logging.WARNING, 
                "error": logging.ERROR
            },
            logging.DEBUG,
            True
        )
            
    """
    This function is used to map the values of a var to other values (e.g. strings to integer values)
    """
    def mapvalues(self, varname, maps, default, lowercase = True):
        value = self.__dict__[varname]
        result = None
        found = False
        if lowercase:
            value = value.lower()
            for k, v in maps.items():
                if value == k.lower():
                    result = v
                    found = True
                    break
        else:
            for k, v in maps.items():
                if value == k:
                    result = v
                    found = True
                    break
        
        if found:
            self.__dict__[varname] = result
        else:
            self.__dict__[varname] = default
            
    """
    These functions act as helpers to translate a 'character separated' list stored in a string, to a typed list
      * these methods are included because they are very common in configuration files
    """
    @staticmethod
    def str2intlist(str_list, separator = ","):
        ar_list = [ x.strip() for x in str_list.split(separator) ]
        result = []
        for v in ar_list:
            try:
                v = int(v)
            except:
                v = None
            if v is not None:
                result.append(v)
        return result

    @staticmethod
    def str2list(str_list, separator = ","):
        ar_list = [ x.strip() for x in str_list.split(separator) ]
        return ar_list
    
    @staticmethod
    def str2floatlist(str_list, separator = ","):
        ar_list = [ x.strip() for x in str_list.split(separator) ]
        result = []
        for v in ar_list:
            try:
                v = float(v)
            except:
                v = None
            if v is not None:
                result.append(v)
        return result



def existing_config_files():
    """
        Method that calculates all the configuration files that are valid, according to the
        'set_paths' and other methods for this module.
    """
    global _ETC_PATHS
    global _MAIN_CONFIG_FILE
    global _CONFIG_VAR_INCLUDE
    global _CONFIG_FILTER

    config_files = []
    for possible in _ETC_PATHS:
        config_files = config_files + glob.glob("%s%s" % (possible, _MAIN_CONFIG_FILE))
    
    if _CONFIG_VAR_INCLUDE != "":
        main_config = Configuration("general", {
            _CONFIG_VAR_INCLUDE:""
        }, _MAIN_CONFIG_FILE)

        if main_config.CONFIG_DIR != "":
            for possible in _ETC_PATHS:
                config_files = config_files + glob.glob("%s%s/%s" % (possible, main_config.CONFIG_DIR, _CONFIG_FILTER))
            
    return config_files