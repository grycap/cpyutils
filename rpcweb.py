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

import web
import sys
import threading
from SimpleXMLRPCServer import SimpleXMLRPCDispatcher
import sys, logging

class SilentLogMiddleware:
    def __init__(self, app):
        self.app = app
    def __call__(self, environ, start_response):
        return self.app(environ, start_response)

# This line enables to silent the calls from web.py
web.httpserver.LogMiddleware=SilentLogMiddleware

def get_dispatcher():
    global dispatcher
    try:
        dispatcher
    except:
        dispatcher = SimpleXMLRPCDispatcher(allow_none = False, encoding = "UTF-8")
    return dispatcher

class rpc_server:
    def GET(self, url):
        return "please use root url for web browsing"
    def POST(self):
        dispatcher = get_dispatcher()
        response = dispatcher._marshaled_dispatch(web.webapi.data())
        web.header('Content-length', str(len(response)))
        return response

class web_server(rpc_server):
    pass

def start_server(web_class = 'web_server', port = 8080):
    urls = ('/RPC2', 'rpc_server', '(/.*)', web_class)
    sys.argv = [ sys.argv[0], str(port) ] + sys.argv[1:]
    app = web.application(urls, globals())
    app.internalerror = web.debugerror
    app.run()

def start_server_in_thread(web_class = 'web_server', port = 80):
    thread = threading.Thread(args = (web_class, port), target=start_server)
    thread.daemon = True
    thread.start()
    return thread
