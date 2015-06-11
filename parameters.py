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

_LOGGER = logging.getLogger("[PAR]")

class Result:
    def __init__(self):
        self.operation = None
        self.flags = {}
        self.parameters = {}
        self.op_flags = {}
        self.op_parameters = {}
        self.other_args = []
        self.op_other_args = []
        self.errors = []
    def __str__(self):
        return "%s\n%s\nOP: %s\nFlags: %s\nParameters: %s\nErrors: %s" % (self.flags, self.parameters, self.operation, self.op_flags, self.op_parameters, self.errors)

def break_parameter_into_list(value):
    if value is None:
        return None
    return value.split(",")
    
class ParameterHandler:
    def __init__(self, operations = []):
        self._operations = []
        self._parameters = {}
        self._long_to_parameter = {}
        self._flags = []
        self._long_to_flag = {}
        self._op_flags = {}
        self._op_parameters = {}
        self._op_long_to_flag = {}
        self._op_long_to_parameter = {}
        for o in operations:
            self._create_op(o)

    def help(self, execname):
        
        retval = execname
        
        f_str = ""
        for f in self._flags:
            f_str = "%s[%s] " % (f_str, f)

        p_str = ""
        for p in self._parameters:
            p_str = "%s[%s <value>]" % (p_str, p)
            
        if len(f_str)>0:
            retval = "%s%s " % (retval, f_str)
        if len(p_str)>0:
            retval = "%s%s " % (retval, p_str)

        op_str = ""
        for o in self._operations:
            
            op_str = "%s" % o
            f_str = ""
            for f in self._op_flags[o]:
                f_str = "%s[%s] " % (f_str, f)
                
            if len(f_str)>0:
                op_str = "%s %s" % (op_str, f_str)
                
            p_str = ""
            for p in self._op_parameters[o]:
                p_str = "%s [%s <value>]" % (p_str, p)
                
            if len(p_str)>0:
                op_str = "%s%s " % (op_str, p_str)

            retval = "%s [ %s ]" % (retval, op_str)
                
        return retval

    def _occupied(self, operation = None):
        if operation is None:
            p = self._parameters.keys()
            f = self._flags
            l2p = self._long_to_parameter.keys()
            l2f = self._long_to_flag.keys()
            o = self._operations
        else:
            f = []
            p = []
            if operation in self._op_flags:
                f = self._op_flags[operation]
            if operation in self._op_parameters:
                p = self._op_parameters[operation].keys()
            l2p = []
            l2f = []
            o = []
        return o + l2f + l2p + p + f
    
    def is_occupied(self, name, operation = None):
        # Just to offer to the external world
        return self._are_occupied([name], operation)
    
    def _are_occupied(self, id_list, operation = None):
        occupied = self._occupied(operation)
        for i in id_list:
            if i in occupied:
                return True
        return False
    
    def add_flag(self, flagname, long_flagname = None):
        if self._are_occupied([flagname, long_flagname]):
            _LOGGER.warning("flag %s is already occupied" % flagname)
            return False
        
        self._flags.append(flagname)
        if long_flagname is not None:
            self._long_to_flag[long_flagname]=flagname
        return True
    
    def add_parameter(self, parametername, long_parametername = None, default = None):
        if self._are_occupied([parametername, long_parametername]):
            _LOGGER.warning("parameter %s is already occupied" % parameter)
            return False
        
        self._parameters[parametername] = default
        if long_parametername is not None:
            self._long_to_parameter[long_parametername]=parametername
        return True

    def _create_op(self, operation):
        if operation not in self._operations:
            self._operations.append(operation)
            self._op_flags[operation] = []
            self._op_parameters[operation] = {}
            self._op_long_to_flag[operation] = {}
            self._op_long_to_parameter[operation] = {}

    def add_op_flag(self, operation, flagname, long_flagname = None):
        if self._are_occupied([flagname, long_flagname], operation):
            _LOGGER.warning("flag %s is already occupied for operation %s" % (flagname, operation))
            return False
        
        self._create_op(operation)        
        self._op_flags[operation].append(flagname)
        if long_flagname is not None:
            self._op_long_to_flag[operation][long_flagname] = flagname
        return True
    
    def add_op_parameter(self, operation, parametername, long_parametername = None, default = None):
        if self._are_occupied([parametername, long_parametername], operation):
            _LOGGER.warning("parameter %s is already occupied for operation %s" % (parametername, operation))
            return False
        
        self._create_op(operation)        
        self._op_parameters[operation][parametername] = default
        if long_parametername is not None:
            self._op_long_to_parameter[operation][long_parametername] = parametername
        return True

    def parse(self, argv, accept_other_args = False, accept_other_op_args = False):
        result = Result()

        while len(argv) > 0:
            symbol = argv.pop(0)
            _LOGGER.debug("symbol: %s" % symbol)
            
            if symbol in self._operations:
                result.operation = symbol
                for f in self._op_flags[symbol]:
                    result.op_flags[f] = False
                for p, v in self._op_parameters[symbol].items():
                    result.op_parameters[p] = v
                continue
            
            if result.operation is None:
                if symbol in self._long_to_flag:
                    symbol = self._long_to_flag[symbol]
                if symbol in self._long_to_parameter:
                    symbol = self._long_to_parameter[symbol]
                if symbol in self._flags:
                    result.flags[symbol] = True
                elif symbol in self._parameters:
                    if len(argv) <= 0:
                        result.errors.append("missing value for parameter %s" % symbol)
                        continue
                    value = argv.pop(0)
                    result.parameters[symbol] = value
                else:
                    if accept_other_args:
                        result.other_args.append(symbol)
                        continue
                    else:
                        result.errors.append("unrecognized symbol %s" % symbol)
                        continue
            else:
                if symbol in self._op_flags[result.operation]:
                    result.op_flags[symbol] = True
                elif symbol in self._op_parameters[result.operation]:
                    if len(argv) <= 0:
                        result.errors.append("missing value for parameter %s in operation %s" % (symbol, result.operation))
                        continue
                    value = argv.pop(0)
                    result.op_parameters[symbol] = value
                else:
                    if accept_other_op_args:
                        result.op_other_args.append(symbol)
                        continue
                    else:
                        result.errors.append("unrecognized symbol %s for operation %s" % (symbol, result.operation))
                        continue
                    
        return len(result.errors)==0, result