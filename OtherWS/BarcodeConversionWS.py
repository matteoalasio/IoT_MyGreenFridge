import cherrypy
import json
import threading
import requests
import sys

class BarcodeConversionREST(object):
    
    # expose the Web Services
    exposed = True

    def __init__(self):
        pass

    def GET (self, *uri):
        pass
        return

    def POST (self, *uri, **params):
        pass
        return

    def PUT (self, *uri, **params):
        pass
        return

    def DELETE(self):
        pass
        return



if __name__ == '__main__':
    
    
    # standard configuration to serve the url "localhost:8080"
    conf = {
        '/': {
            'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
            'tools.sessions.on': True
        }
    }

    devPort = 8080

    
    # deploy the DeviceConnectorREST class and start the web server
    cherrypy.tree.mount(BarcodeConversionREST(), '/', conf)
    cherrypy.config.update({'server.socket_host': '0.0.0.0'})
    cherrypy.config.update({'server.socket_port': devPort})
    cherrypy.engine.start()
    cherrypy.engine.block()