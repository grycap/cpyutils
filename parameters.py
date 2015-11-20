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
import sys
_LOGGER = logging.getLogger("[PARAMS]")
_LOGGER.disabled = True

# The structure that will be returned as a result of the parsing.
# * The operation value is prepared to give support to the operations that have its own parameters
# * The values structure will contain an entry for each of the parameters or arguments, with the values recognised (or the default value).
#   The index for the entry will be the name for the parameter (the alt name will not appear).
#   In case that the parameter is an operation, it will contain its own "result" structure. Depends on the behaviour of the Operation class.
class Result:
    def __init__(self):
        self.operation = None
        self.values = {}
        self.detected = []

# This is a class to validate "int" arguments
class _Cast_int:
    def _cast(self, v, error):
        try:
            value = int(v)
            return True, value
        except:
            error.append("parameter '%s' for '%s' expected to be integer" % (v, self._name))
            return False, None

# This is a class to validate "float" arguments
class _Cast_float:
    def _cast(self, v, error):
        try:
            value = float(v)
            return True, value
        except:
            error.append("parameter '%s' for '%s' expected to be float" % (v, self._name))
            return False, None

# The base class for the parameters. This should not be used by itself. Instead, the user should instantiate classes such as Parameter, Arguments, Flag, etc.
class _Parameter_base:
    def __init__(self, name, alt = None, desc = None, count = 1, mandatory = False, default = None):
        # The name of the parameter. It will be used in the results structure to indicate the values captured from the commandline
        self._name = name
        # An alternate name for the parameter (e.g. the long name in unix)
        self._alt = alt
        # A description for the parameter (for the help string)
        self._desc = desc
        # The number of fields (that are not the name of the parameter) that will be captured from the commandline (e.g. a flag needs 0 extra commands, a parameter at least, 1)
        self._count = count
        # If True, the parameter MUST be parsed
        self._mandatory = mandatory
        # If True, the name of the parameter MUST appear in the commandline (e.g. the name of a flag --xml or the name of a parameter --host <host>). If False
        # the name of the parameter is only for internal usage (e.g. an argument)
        self._index = False
        # The default value in the results structure, in case that this parameter does not appear in the commandline
        self._default = default
        
        # TODO: make a priority system for the arguments. This will enable to make a parsing algorithm that extracts the arguments from the middle of the commandline.
        # the current system only processes the commandline from the first argument to the last one.
        # A prioritized system could first try to extract the flags, then try to extract the parameters, then the operations and lastly, the arguments. Such system
        # will not allow to duplicate the flags between the main commandline and the inner operations, while the current method allows it.
        self._priority = 0
        
    def __str__(self):
        return self._tostr(0)

    def _brief_cmdline(self):
        # Returns a brief commandline
        return self._cmdline()

    def _cmdline(self):
        # Returns the whole commandline for this parameter, with its flags (if needed), arguments, etc.
        if self._mandatory:
            name = "<%s>" % self._name
        else:
            name = "[%s]" % self._name
        return name

    def help_str(self):
        # Return a string that contains the help
        return self._tostr(0)
            
    def _tostr(self, depth):
        # Obtains a string that describes the help about the parameter, but it indents the paragraphs according to the depth level
        # * This is used to enable pretty output of subcommands and flags
        tstr = "\t" * depth
        if self._alt is None:
            name = self._name
        else:
            name = "%s|%s" % (self._name, self._alt)
        if self._mandatory:
            name = "<%s>" % name
        else:
            name = "[%s]" % name
            
        if self._desc is None:
            desc = ""
        else:
            desc = " - %s" % self._desc
        return "%s%s%s" % (tstr, name, desc)
    
    def _cast(self, v, error):
        # When a parameter is received, it is casted to the proper type. E.g. translates from string to integer, etc.
        # * This enables a generic parsing algorithm for typed parameters
        return True, v
    
    def _initialize_result(self, result):
        # Initializes the result structure that will be deliveder to the user as a result of the parsing
        result.values[self._name] = self._default
    
    def parse(self, args, result, error):
        # This is the parsing algorithm. It receives the current arg list, the result structure and a list of error lines
        # * The algorithm extracts the args from the list (those arguments parsed MUST be removed) and fills in the "result" structure.
        #   In case that some error happens, this function should add strings to the "error" list to explain the error.
        # The function returns "True" in case that it has successfully parsed the structure (False in other case), along with the "result" structure and the "error" string list.
        count = self._count
        values = []
        values_raw = []
        failed = False
        
        while (count != 0) and (len(args) > 0):
            arg = args.pop(0)
            values_raw.insert(0, arg)
            casted, value = self._cast(arg, error)
            if casted:
                values.append(value)
            else:
                failed = True
            count -= 1

        accepted = True            
        if count > 0:
            if self._mandatory:
                error.append("Not enough values for parameter '%s'" % self._name)
                failed = True
            else:
                # We restore the parameters in order to be used by other
                for a in values_raw:
                    args.insert(0, a)
                accepted = False
            
        if (not failed) and (accepted):
            result.values[self._name] = values
            result.detected.append(self._name)

        return (not failed) and accepted, result, error

# This class represents a simple flag. E.g. -l in ls command.
class Flag(_Parameter_base):
    def __init__(self, name, alt = None, desc = None, value = True, default = False):
        # The value parameter is the value that the user wants to appear in the values structure in case that the flag appears in the commandline.
        # * The most common values are: default = False, value = True to represent whether it appears or not in the commandline
        _Parameter_base.__init__(self, name, alt, desc, count = 0, mandatory = False, default = default)
        self._value = value
        self._index = True
    
    def parse(self, args, result, error):
        # If the flag appears in firt place (in its _name form or its alternative name) it will be removed from the args array
        if len(args) > 0:
            if (args[0] == self._name) or ((self._alt is not None) and (args[0] == self._alt)):
                args.pop(0)
                result.values[self._name] = self._value
                result.detected.append(self._name)
        return True, result, error

# This class represents a plain argument. e.g. the names of the folders to be created using the mkdir command
# * It is possible to capture more than one argument using the "count" parameter in the constructor, and -1 will mean to capture all the possible arguments
class Argument(_Parameter_base):
    def __init__(self, name, desc, count = 1, mandatory = False, default = None):
        _Parameter_base.__init__(self, name, None, desc, count, mandatory, default)
        self._index = False

# This class represents a parameter provided using a flag. e.g. --host <hostname>
# * It is possible to capture more than one argument using the "count" parameter in the constructor, and -1 will mean to capture all the possible arguments
class Parameter(_Parameter_base):
    def __init__(self, name, alt = None, desc = None, count = 1, mandatory = False, default = None):
        _Parameter_base.__init__(self, name, alt, desc, count, mandatory, default)
        self._index = True

    def parse(self, args, result, error):
        parsed = True
        if len(args) > 0:
            if (args[0] == self._name) or ((self._alt is not None) and (args[0] == self._alt)):
                args.pop(0)
                # Now that we know that it is the specific parameter, the values are mandatory; we will restore the mandatory value later
                mandatory = self._mandatory
                self._mandatory = True
                parsed, _, _ = _Parameter_base.parse(self, args, result, error)
                self._mandatory = mandatory
        return parsed, result, error
    
    def _cmdline(self):
        name = self._name

        if self._count == 1:
            name = "%s <value>" % name
        elif self._count < 0:
            name = "%s <value> ..." % name
        if self._count > 1:
            name = "%s <value>...<value>" % name

        if not self._mandatory:
            name = "[%s]" % name

        return name
    
    def _tostr(self, depth):
        tstr = "\t" * depth
        if self._alt is None:
            name = self._name
        else:
            name = "%s|%s" % (self._name, self._alt)
            
        if not self._mandatory:
            name = "[%s]" % name
            
        if self._count == 1:
            name = "%s <value>" % name
        elif self._count < 0:
            name = "%s <value> ..." % name
        if self._count > 1:
            name = "%s <value>...<value>" % name
            
        if self._desc is None:
            desc = ""
        else:
            desc = " - %s" % self._desc
        return "%s%s%s" % (tstr, name, desc)
    
# These are classes that correspond to the parameters and arguments with type validations    
class Parameter_int(_Cast_int, Parameter): pass
class Parameter_float(_Cast_float, Parameter): pass
class Argument_int(_Cast_int, Argument, ): pass
class Argument_float(_Cast_float, Argument): pass

# The generic argument parser. This class is the one that validates the set of arguments in the commandline.
class ArgumentParser(_Parameter_base):
    def __init__(self, name, alt = None, desc = None, arguments = []):
        _Parameter_base.__init__(self, name, alt, desc)
        self._parameters = {}
        self._arguments = {}
        self._keyword_to_parameter = {}
        self._argument_order = []
        self._parameter_order = []
        if arguments is not None:
            for argument in arguments:
                self.add(argument)
        
    def add(self, param):
        duplicate = False
        if param._index:
            # it is a parameter
            if param._name in self._keyword_to_parameter:
                raise Exception("Parameter name '%s' already taken" % param._name)
                duplicate = True
            if (param._alt is not None) and (param._alt in self._keyword_to_parameter):
                raise Exception("Parameter name '%s' already taken" % param._alt)
                duplicate = True
            if not duplicate:
                self._keyword_to_parameter[param._name] = param._name
                if param._alt is not None:
                    self._keyword_to_parameter[param._alt] = param._name
                self._parameters[param._name] = param
                self._parameter_order.append(param._name)
        else:
            # it is an argument
            if param._name in self._arguments:
                raise Exception("Argument name '%s' already taken" % param._name)
                duplicate = True
            if not duplicate:
                self._arguments[param._name] = param
                self._argument_order.append(param._name)

    def parse(self, args, result, error):
        # The arguments are processed in the fifo order. We are not processing them using any priority system (although it is commited for the future)
        for _, arg in self._arguments.items():
            arg._initialize_result(result)
        for _, arg in self._parameters.items():
            arg._initialize_result(result)
        
        # Initialize the other_arguments array to later check the arguments
        other_arguments = []
        failed = False
        
        # First we are checking the indexed ones
        while (len(args) > 0) and (not failed):
            arg = args[0]
            _LOGGER.debug("recognising %s" % arg)
            
            recognised = False
            if arg in self._keyword_to_parameter:
                _LOGGER.debug("recognising %s as a parameter" % arg)
                arg_key = self._keyword_to_parameter[arg]
                parameter = self._parameters[arg_key]
                parsed, _, _ = parameter.parse(args, result, error)
                if not parsed:
                    failed = True
                    
                recognised = True
            else:
                _LOGGER.debug("%s is not a parameter" % arg)
                for argname in self._argument_order:
                    myarg = self._arguments[ argname ]

                    # If it is already set, we are not getting the values again; we supose that it is other argument
                    if myarg._name not in result.detected:
                        parsed, _, _ = myarg.parse(args, result, error)
                        if parsed:
                            recognised = True
                            break
            if not recognised:
                failed = True
                error.append("could not recognise parameters '%s'" % (" ".join(args)))

        for _, myarg in self._arguments.items():
            if (myarg._name not in result.detected) and (myarg._mandatory):
                failed = True
                error.append("missing mandatory argument '%s' for '%s'" % (myarg._name, self._name))

        for _, myarg in self._parameters.items():
            if (myarg._name not in result.detected) and (myarg._mandatory):
                failed = True
                error.append("missing mandatory argument '%s' for '%s'" % (myarg._name, self._name))
        
        if len(args) > 0:
            failed = True
                
        return (not failed), result, error
    
    def _cmdline(self):
        cmdlines = []
        index = []

        for parname in self._parameter_order:
            arg = self._parameters[parname]
            if issubclass(arg.__class__, Operation):
                index.append(arg._brief_cmdline())
            else:
                cmdlines.append(arg._brief_cmdline())

        for argname in self._argument_order:
            arg = self._arguments[argname]
            cmdlines.append(arg._brief_cmdline())

        if len(index)>0:
            return "%s [%s]" % (" ".join(cmdlines), "|".join(index))
        else:
            return "%s" % (" ".join(cmdlines))

    def _tostr(self, depth):
        tstr = "\t" * depth
        if self._alt is None:
            name = self._name
        else:
            name = "%s|%s" % (self._name, self._alt)
        if self._mandatory:
            name = "[%s]" % name
        if self._desc is None:
            desc = ""
        else:
            desc = "%s" % self._desc
            
        arglines = []
        for parname in self._parameter_order:
            arg = self._parameters[parname]
            arglines.append(arg._tostr(depth + 1))

        for argname in self._argument_order:
            arg = self._arguments[argname]
            arglines.append(arg._tostr(depth + 1))

        if len(arglines) > 0:
            return "%s%s\n\n%sUsage: %s %s\n\n%s\n" % (tstr, desc, tstr, name, self._brief_cmdline(), "\n".join(arglines))
        else:
            return "%s%s%s\n%sUsage: %s\n" % (tstr, desc, tstr, name, self._brief_cmdline())
    
# A Operation is like a commandline inside a commandline. It states a operation that has its own options with its own parameters. So it has its own results structure.
class Operation(ArgumentParser):
    def __init__(self, name, alt = None, desc = None, arguments = []):
        ArgumentParser.__init__(self, name, alt, desc, arguments)
        self._index = True

    def _brief_cmdline(self):
        return self._name
        
    def _tostr(self, depth):
        tstr = "\t" * depth
        if self._alt is None:
            name = self._name
        else:
            name = "%s|%s" % (self._name, self._alt)
        if self._mandatory:
            name = "[%s]" % name
        if self._desc is None:
            desc = ""
        else:
            desc = "* %s" % self._desc
            
        arglines = []
        for parname in self._parameter_order:
            arg = self._parameters[parname]
            arglines.append(arg._tostr(depth + 1))

        for argname in self._argument_order:
            arg = self._arguments[argname]
            arglines.append(arg._tostr(depth + 1))

        if len(arglines) > 0:
            return "%s%s\n%s  Usage: %s %s\n%s\n" % (tstr, desc, tstr, name, self._cmdline(), "\n".join(arglines))
        else:
            return "%s%s\n%s  Usage: %s %s\n" % (tstr, desc, tstr, name, self._cmdline())
        
    def parse(self, args, result, error):
        success = True
        if len(args) > 0:
            arg = args[0]
            if (arg == self._name) or ((self._alt is not None) and (self._alt == arg)):
                arg = args.pop(0)
                result.operation = self._name
                opresult = Result()
                parsed, _, _ = ArgumentParser.parse(self, args, opresult, error)
                if parsed:
                    result.values[self._name] = opresult
                    result.detected.append(self._name)
                else:
                    success = False
                    
                # After one operation tag, everything is suposed to be part of the operation commandline, so
                # we are removing it to prevent further processing from the upper structure
                if len(args) > 0:
                    while (len(args)>0): args.pop(0)
                
        return success, result, error

# This is the class that is designed to be used to create a commandline parser.
# * It allows to declare the commandline in a compact manner, adds the de-facto standard -h parameter for the help and processes it to show the help
# * It also enables to auto call operations handlers in case that an operation is stated and some Operations objects are created as possible arguments
#   In such case, the user MUST create functions with the same name of the operations, and the (self, result, error) interface. Using the "autocall_ops"
#   method, such function will be called in case that the operation appears in the commandline.
class CmdLineParser(ArgumentParser):
    def __init__(self, name, desc, arguments = []):
        ArgumentParser.__init__(self, name, desc = desc, arguments = [ Flag("-h", "--help", desc = "Shows this help") ] + arguments)

    def add_operations(self, operations):
        for (op, desc, arguments) in operations:
            o = Operation(op, desc = desc)
            if arguments is not None:
                for arg in arguments:
                    o.add(arg)
            self.add(o)
    
    def autocall_ops(self, args):
        parsed, result, error = ArgumentParser.parse(self, args, Result(), [])
        if parsed:
            if result.operation is None:
                return False, result, "No operation was stated"
            try:
                method = getattr(self, result.operation)
            except:
                raise Exception("No handler for command %s" % result.operation)
            
            self.preops(result, error)
            retval = method(result.values[result.operation], error)
            return True, result, retval
        else:
            return False, None, ", ".join(error)
        
    def parse(self, args):
        parsed, result, error = ArgumentParser.parse(self, args, Result(), [])
        if parsed:
            if result.values['-h']:
                return False, result, self._tostr(0)
            return True, result, ""
        else:
            if (result is not None) and result.values['-h']:
                return False, result, self._tostr(0)
            return False, None, ", ".join(error)
        
    # This function enables the common workflow for the command line parsing
    # * In case that it is operation based, it should be called the self_service with the ops parameter set to True. Then the function that has the same name than the operation will be called
    # * In case that it is command line based, it should be called the self_service function with the ops parameter set to True. Then the function "process" will be called. The developer should
    #   overwrite the process(self, result) operation to carry out the proper actions
    def self_service(self, ops = False):
        if ops:
            parsed, result, info = self.autocall_ops(sys.argv[1:])
            if not parsed:
                if (result is None):
                    print "Error:", info
                    sys.exit(-1)
                    
            if (result.values['-h']):
                print self
                sys.exit(0)
        
            if (result.operation is None):
                print info
                sys.exit(-1)
                
            (opexecuted, explain) = info
            print explain
            if opexecuted:
                sys.exit(0)
            else:
                sys.exit(-1)
        else:
            parsed, result, info = self.parse(sys.argv[1:])
            print result.values
            if not parsed:
                if (result is None):
                    print "Error:", info
                    sys.exit(-1)
                else:
                    print info
                    sys.exit(0)
            else:
                if self.process(result, info):
                    sys.exit(0)
                else:
                    print "Exit with errors"
                    sys.exit(-1)

    # This function is exectued in the autocall_ops procedure. It is called prior to the call to the function that implements the operation
    def preops(self, result, info):
        pass
                   
    # This function is executed if the self_service function is called with the ops parameter set to False and the commandline is properly parsed.
    # * It should return True in case that the function is properly executed. Otherwise it should return False.
    def process(self, result, info):
        print "Not implemented"
        return True
        
if __name__ == '__main__':
    import sys
    
    ########################
    #
    # Example 1: common arguments
    #
    ########################
    ap = CmdLineParser("ls", "List directory contents", [
        Flag("-a", "--all", desc = "do not ignore entries starting with ."),
        Flag("-A", "--almost-all", desc = "do not list implied . and .."),
        Flag("--author", desc = "with -l, print the author of each file"),
        Flag("-b", "--escape", desc = "print C-style escapes for nongraphic characters"),
        Parameter("--block-size", desc = "scale sizes by SIZE before printing them.  E.g., '--block-size=M' prints sizes in units of 1,048,576 bytes.  See SIZE format."),
        Argument("FILE", "the files that want to be listed", count = -1)
    ])
    
    parsed, result, info = ap.parse(sys.argv[1:])
    print result.values
    if not parsed:
        if (result is None):
            print "Error:", info
            sys.exit(-1)
        else:
            print info
            sys.exit(0)
    else:
        print info
        sys.exit(0)

    ########################
    #
    # Example 2: common arguments and operations
    #
    ########################

    class CluesCmdLine(CmdLineParser):
        def status(self, result, error):
            print "at status"
            return "success"
        def recover(self, result, error):
            print "recover nodes", result.values['nodes']
            return "success"
        def enable(self, result, error):
            print "enable nodes", result.values['nodes']
            return "success"
        def disable(self, result, error):
            print "disable nodes", result.values['nodes']
            return "success"

    ap = CluesCmdLine("clues", desc = "The CLUES command line utility", arguments = [
            Operation("status", desc = "Show the status of the platform"),
            Operation("recover", desc = "Recover one or more nodes from an error state", arguments = [
                Argument("nodes", "names of the nodes that want to be recovered", mandatory = True, count = -1)
            ]),
            Operation("enable", "Enable one or more nodes to be considered by the platform", arguments = [
                Argument("nodes", "names of the nodes that want to be enabled", mandatory = True, count = -1)
            ]),
            Operation("disable", "Disable one or more nodes to be considered by CLUES", arguments = [
                Argument("nodes", "names of the nodes that want to be disabled", mandatory = True, count = -1)
            ]),
        ])

    ap.self_service(True)