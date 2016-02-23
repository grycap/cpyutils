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

import sys
import threading
from SimpleXMLRPCServer import SimpleXMLRPCDispatcher
import SimpleXMLRPCServer
import sys, logging
import xmlrpclib

class SimpleXMLRPCRequestHandler_withGET(SimpleXMLRPCServer.SimpleXMLRPCRequestHandler):
    def _return_html(self, response):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        if self.encode_threshold is not None:
            if len(response) > self.encode_threshold:
                q = self.accept_encodings().get("gzip", 0)
                if q:
                    try:
                        response = xmlrpclib.gzip_encode(response)
                        self.send_header("Content-Encoding", "gzip")
                    except NotImplementedError:
                        pass
        self.send_header("Content-length", str(len(response)))
        self.end_headers()
        self.wfile.write(response)
    
    def do_GET(self):
        if self.server._web_class is None:
            self.send_response(500)
        else:
            self._return_html(self.server._web_class.GET(self.path))

class XMLRPCServer(SimpleXMLRPCServer.SimpleXMLRPCServer):
    def __init__(self, host, port, web_class = None):
        SimpleXMLRPCServer.SimpleXMLRPCServer.__init__(self, (host, port), requestHandler = SimpleXMLRPCRequestHandler_withGET)
        self._web_class = None
        if web_class is not None:
            self._web_class = web_class()
        self._host = host
        self._port = port
    
    def start_in_thread(self):
        self.logRequests = False
        thread = threading.Thread(target=self.serve_forever)
        thread.daemon = True
        thread.start()
        return thread

class web_class:
    def GET(self, url):
        return "please use root url for web browsing"