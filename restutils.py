# coding: utf-8
#
# IM - Infrastructure Manager
# Copyright (C) 2011 - GRyCAP - Universitat Politecnica de Valencia
#
# CLUES Python utils - Utils and General classes that spin off from CLUES
# Copyright (C) 2015 - GRyCAP - Universitat Politecnica de Valencia
#   * extract classes to be used in future developments
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

# $ sudo pip install cherrypy bottle
import threading
import bottle
import json

_app = bottle.Bottle()  
_bottle_server = None

def get_app():
    global _app
    return _app

# Declaration of new class that inherits from ServerAdapter  
# It's almost equal to the supported cherrypy class CherryPyServer  
class MySSLCherryPy(bottle.ServerAdapter):
    def __init__(self, ssl_certfile = None, ssl_keyfile = None, ssl_ca_certs = None, host='127.0.0.1', port=8080, **options):
        self._ssl_certfile = ssl_certfile
        self._ssl_keyfile = ssl_keyfile
        self._ssl_ca_certs = ssl_ca_certs
        bottle.ServerAdapter.__init__(self, host, port, options)
        
    
    def run(self, handler):
        from cherrypy.wsgiserver.ssl_builtin import BuiltinSSLAdapter
        from cherrypy import wsgiserver
        server = wsgiserver.CherryPyWSGIServer((self.host, self.port), handler)  
        self.srv = server
        
        # If cert variable is has a valid path, SSL will be used  
        # You can set it to None to disable SSL
        server.ssl_adapter = BuiltinSSLAdapter(self._ssl_certfile, self._ssl_keyfile, self._ssl_ca_certs)
        try:  
            server.start()  
        finally:  
            server.stop()  
                
    def shutdown(self):
        self.srv.stop()

class StoppableWSGIRefServer(bottle.ServerAdapter):
    def run(self, app): # pragma: no cover
        from wsgiref.simple_server import WSGIRequestHandler, WSGIServer
        from wsgiref.simple_server import make_server
        import socket

        class FixedHandler(WSGIRequestHandler):
            def address_string(self): # Prevent reverse DNS lookups please.
                return self.client_address[0]
            def log_request(*args, **kw):
                if not self.quiet:
                    return WSGIRequestHandler.log_request(*args, **kw)

        handler_cls = self.options.get('handler_class', FixedHandler)
        server_cls  = self.options.get('server_class', WSGIServer)

        if ':' in self.host: # Fix wsgiref for IPv6 addresses.
            if getattr(server_cls, 'address_family') == socket.AF_INET:
                class server_cls(server_cls):
                    address_family = socket.AF_INET6

        srv = make_server(self.host, self.port, app, server_cls, handler_cls)
        self.srv = srv ### THIS IS THE ONLY CHANGE TO THE ORIGINAL CLASS METHOD!
        srv.serve_forever()

    def shutdown(self): ### ADD SHUTDOWN METHOD.
        self.srv.shutdown()
        # self.server.server_close()

def run_in_thread(host, port, use_ssl = False, ssl_certfile = None, ssl_keyfile = None, ssl_ca_certs = None):
    _bottle_thr = threading.Thread(target=run, args=(host, port, use_ssl, ssl_certfile, ssl_keyfile, ssl_ca_certs))
    _bottle_thr.daemon = True
    _bottle_thr.start()
    return _bottle_thr

def run(host, port, use_ssl = False, ssl_certfile = None, ssl_keyfile = None, ssl_ca_certs = None):
    global _bottle_server, _app
    if use_ssl:
        # Add our new MySSLCherryPy class to the supported servers  
        # under the key 'mysslcherrypy'
        if use_ssl and (ssl_certfile is None or ssl_keyfile is None or ssl_ca_certs is None):
            raise Exception("You must provide certificate, key file and the CA path to enable the SSL server")
        
        _bottle_server = MySSLCherryPy(ssl_certfile, ssl_keyfile, ssl_ca_certs, host=host, port=port)
        bottle.run(_app, host=host, port=port, server=_bottle_server, quiet=True)
    else:
        _bottle_server = StoppableWSGIRefServer(host=host, port=port)
        bottle.run(_app, server=_bottle_server, quiet=True)

def stop():
    _bottle_server.shutdown()

def response_json(content):
    bottle.response.content_type = "application/json"
    content_str = json.dumps(content)
    return content_str

def response_txt(content):
    bottle.response.content_type = "text/plain"
    content_str = str(content)
    return content_str
    
def add_header(name, content):
    bottle.response.set_header(name, content)
    
def set_status(_id):
    bottle.response.status = _id
    
def error(num, txt):
    '''
    Typical error:
        401: Unauthorized
        403: Forbidden
        404: Not found
        500: Internal server error
    '''
    bottle.abort(num, "Error: " + str(txt))

'''
    EXAMPLE:

    app = restutils.get_app()
    @app.route('/:_id', method='GET')
    def get_info(_id):
        return json_response({'field1':'2'})
    
    if __name__ == '__main__':
        run("0.0.0.0",7000)
'''