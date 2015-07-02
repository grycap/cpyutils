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
import xml.dom.minidom
import logging

class XMLObject:
	tuples = {}
	tuples_lists = {}
	values = []
	values_lists = []
	numeric = []
	noneval = None
	numeric_accept_none = []

	@staticmethod
	def getText(nodelist):
		rc = []
		for node in nodelist:
			if node.nodeType == node.TEXT_NODE or node.nodeType == node.CDATA_SECTION_NODE:
				rc.append(node.data)
		return ''.join(rc)

	@staticmethod
	def handleField(fieldName, VM):
		try:
			fieldElements = VM.getElementsByTagName(fieldName)[0]
			return XMLObject.getText(fieldElements.childNodes)
		except:
			return None

	@staticmethod
	def handleFieldAsList(fieldName, VM):
		try:
			fieldElements = VM.getElementsByTagName(fieldName)
			local_list = []
			for fieldElement in fieldElements:
				local_list.append(XMLObject.getText(fieldElement.childNodes))
			return local_list
		except:
			return []

	def __setattr__(self, name, value):
		self.__dict__[name] = value

	def _parse(self, xml_str, parameters):
		dom = xml.dom.minidom.parseString(xml_str)

		for tag, className in self.__class__.tuples.items():
			objs = dom.getElementsByTagName(tag)
			if (len(objs) > 0):
				if parameters is None:
					newObj = className(objs[0].toxml())
				else:
					newObj = className(objs[0].toxml(), *parameters)
				dom.childNodes[0].removeChild(objs[0])
			else:
				newObj = None
			self.__setattr__(tag, newObj)

		for tag, className in self.__class__.tuples_lists.items():
			objs = dom.getElementsByTagName(tag)
			obj_list = []
			for obj in objs:
				if parameters is None:
					newObj = className(obj.toxml())
				else:
					newObj = className(obj.toxml(), *parameters)
				dom.childNodes[0].removeChild(obj)
				obj_list.append(newObj)
			self.__setattr__(tag, obj_list)

		for tag in self.__class__.values_lists:
			self.__setattr__(tag, XMLObject.handleFieldAsList(tag, dom))

		for tag in self.__class__.values:
			value = XMLObject.handleField(tag, dom)
			if (value is None):
				value = self.noneval
			if (tag in self.__class__.numeric):
				accepted = False
				if value is None:
					if tag in self.numeric_accept_none:
						value = None
						accepted = True
				if not accepted:
					try:
						value = float(value)
						if (value == int(value)):
							value = int(value)	
					except:
						logging.warning("numeric value expected for %s - found %s" % (tag, value))
			self.__setattr__(tag, value)

	def __init__(self, xml_str, parameters = None):
		self._parse(xml_str, parameters)

def _to_numeric(value):
	try:
	    v = float(value)
	except:
	    return None
	f = v
	try:
	    e = int(v)
	except ValueError:
	    e = f
	if (e == f):
	    v = e
	else:
	    v = f
	return v

class XMLObject_KW(XMLObject):
    def get_kws_string(self):
        retval = ""
        for kw in self.values:
            if kw in self.numeric:
                retval = "%s%s=%s;" % (retval, kw, self.__dict__[kw])
            else:
                retval = "%s%s=\"%s\";" % (retval, kw, self.__dict__[kw])
        return retval
    def get_kws_dict(self):
        kw_dict = {}
        for kw in self.values:
            if kw in self.numeric:
                kw_dict[kw] = _to_numeric(self.__dict__[kw])
            else:
                kw_dict[kw] = self.__dict__[kw]
        return kw_dict