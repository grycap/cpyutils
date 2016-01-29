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

def read_csv_from_lines(lines, separator = " ", clean_callback = None, min_expected_fields = None, max_expected_fields = None):
    accepted = []
    ignored = []
    for line in lines:
        # Remove comments
        line = line.split('#',1)[0]
        line = line.strip()
        if line != "":
            if clean_callback is not None:
                line = clean_callback(line)
                
            line_split = [ line ]
            
            # Allow multiple separators
            for s in separator:
                result = []
                for l in line_split:
                    splitted = l.split(s)
                    if len(splitted) > 1:
                        result = result + splitted
                    else:
                        result.append(l)
                line_split = result
                
            # The problem of this is that it does not allow blank fields
            lineparts = [ x.strip() for x in line_split ]
            if min_expected_fields is not None:
                if len(lineparts) < min_expected_fields:
                    _LOGGER.warning("malformed CSV entry: few values")
                    ignored.append(lineparts)
                    continue
                
            if max_expected_fields is not None:
                if len(lineparts) > max_expected_fields:
                    _LOGGER.warning("malformed CSV entry: too values")
                    ignored.append(lineparts)
                    continue

            accepted.append(lineparts)

    return accepted, ignored

def read_csv(filename, separator = " ", clean_callback = None, min_expected_fields = None, max_expected_fields = None):
    accepted = []
    ignored = []
    try:
        accepted, ignored = read_csv_from_lines(open(filename), separator, clean_callback, min_expected_fields, max_expected_fields)
    except IOError, e:
        _LOGGER.error("cannot read entries for file %s" % filename)
        raise e
        
    return accepted, ignored