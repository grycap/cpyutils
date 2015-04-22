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
# The MIT License (MIT)
#
# Copyright (c) 2014 Carlos de Alfonso (caralla@upv.es)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
#
# This version of ServerProxy created with the advise of contributors from
#
# http://stackoverflow.com/questions/372365/set-timeout-for-xmlrpclib-serverproxy
# http://stackoverflow.com/questions/2425799/timeout-for-xmlrpclib-client-requests
# http://stackoverflow.com/questions/5663946/problem-with-xmlrpc-server
#
# And using parts of code of the XML-RPC client interface distributed in python
# 2.7 and 2.4. This software is not substituting or modifying the XML-RPC client
# interface at all, but it uses some pieces of its code. So it is acknowledged
# the copyright of its authors:
#
# --------------------------------------------------------------------
# The XML-RPC client interface is
#
# Copyright (c) 1999-2002 by Secret Labs AB
# Copyright (c) 1999-2002 by Fredrik Lundh
#
# By obtaining, using, and/or copying this software and/or its
# associated documentation, you agree that you have read, understood,
# and will comply with the following terms and conditions:
#
# Permission to use, copy, modify, and distribute this software and
# its associated documentation for any purpose and without fee is
# hereby granted, provided that the above copyright notice appears in
# all copies, and that both that copyright notice and this permission
# notice appear in supporting documentation, and that the name of
# Secret Labs AB or the author not be used in advertising or publicity
# pertaining to distribution of the software without specific, written
# prior permission.
#
# SECRET LABS AB AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH REGARD
# TO THIS SOFTWARE, INCLUDING ALL IMPLIED WARRANTIES OF MERCHANT-
# ABILITY AND FITNESS.  IN NO EVENT SHALL SECRET LABS AB OR THE AUTHOR
# BE LIABLE FOR ANY SPECIAL, INDIRECT OR CONSEQUENTIAL DAMAGES OR ANY
# DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS,
# WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS
# ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR PERFORMANCE
# OF THIS SOFTWARE.
# --------------------------------------------------------------------

import xmlrpclib
import httplib
import socket

try:
    _GLOBAL_DEFAULT_TIMEOUT=socket.__GLOBAL_DEFAULT_TIMEOUT
except:
    _GLOBAL_DEFAULT_TIMEOUT=10

class TimeoutHTTPConnection(httplib.HTTPConnection):
   def connect(self):
       httplib.HTTPConnection.connect(self)
       self.sock.settimeout(self.timeout)

class TimeoutHTTP(httplib.HTTP):
   _connection_class = TimeoutHTTPConnection
   def set_timeout(self, timeout):
       self._conn.timeout = timeout

class TimeoutTransport(xmlrpclib.Transport):
    """
    Custom XML-RPC transport class for HTTP connections, allowing a timeout in
    the base connection.
    """

    def __init__(self, timeout=_GLOBAL_DEFAULT_TIMEOUT, use_datetime=0):
        if hasattr(xmlrpclib.Transport,"__init__"):
            xmlrpclib.Transport.__init__(self, use_datetime)
        self._timeout = timeout

    def make_connection(self, host):
        if hasattr(self,"_connection"):
            #return an existing connection if possible.  This allows
            #HTTP/1.1 keep-alive.
            if self._connection and host == self._connection[0]:
                return self._connection[1]
    
            # create a HTTP connection object from a host descriptor
            chost, self._extra_headers, x509 = self.get_host_info(host)
            #store the host argument along with the connection object
            self._connection = host, httplib.HTTPConnection(chost, timeout = self._timeout)
            return self._connection[1]
        else:
            host, extra_headers, x509 = self.get_host_info(host)
            conn = TimeoutHTTP(host)
            conn.set_timeout(self._timeout)
            return conn
            
class ServerProxy(xmlrpclib.ServerProxy):
    def __init__(self, uri, timeout = _GLOBAL_DEFAULT_TIMEOUT, encoding=None, verbose=0, allow_none=0, use_datetime=0):
        transport = TimeoutTransport(timeout = timeout, use_datetime = use_datetime)
        xmlrpclib.ServerProxy.__init__(self, uri, transport = transport, encoding = encoding, verbose = verbose, allow_none = allow_none)
        
def create_xmlrpc_server_in_thread(host, port, functions):
    from SimpleXMLRPCServer import SimpleXMLRPCServer
    server = SimpleXMLRPCServer((host, port))
    
    for f in functions:
        server.register_function(f)

    import threading
    thread = threading.Thread(target=server.serve_forever)
    thread.daemon = True
    thread.start()
    if thread.isAlive():
        return True
    return False