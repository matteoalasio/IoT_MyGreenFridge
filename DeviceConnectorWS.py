from DeviceConnector import *
import cherrypy
import json
import socket
        

class DeviceConnectorREST(object):
    
    # expose the Web Services
    exposed = True

    def __init__(self, deviceconnector):
        self.deviceConnector = deviceConnector

    def GET (self, *uri):
        
        if (len(uri)!=1):
            raise cherrypy.HTTPError(404, "Error: wrong number of uri")
        elif (uri[0] == 'temperature'):
            senml = self.deviceConnector.get_temperature()
            if senml is None:
                raise cherrypy.HTTPError(500, "Error: invalid senml")
            
            temperature = ((senml['e'])[0])['v']
            
            # check if temperature is a string
            # since in that case there must have been a reading error
            if isinstance(temperature, basestring):
                raise cherrypy.HTTPError(500, "Error in reading data from temperature sensor")
            else:
                # if the temperature has been read correctly, convert senml into json
                outputJson = json.dumps(senml)


        elif (uri [0] == 'humidity'):
            senml = self.deviceConnector.get_humidity()
            if senml is None:
                raise cherrypy.HTTPError(500, "Error: invalid senml")
            
            # check if humidity is a string
            # since in that case there must have been a reading error
            humidity = ((senml['e'])[0])['v']

            if isinstance(humidity, basestring):
                raise cherrypy.HTTPError(500, "Error in reading data from humidity sensor")
            else:
                # if the humidity has been read correctly, convert senml into json
                outputJson = json.dumps(senml)

        elif (uri [0] == 'camera0'):            
            senml = self.deviceConnector.get_camera0()
            
            if senml is None:
                raise cherrypy.HTTPError(500, "Error: invalid senml")
            
            camera0 = ((senml['e'])[0])['v']

            if camera0 == "Reading error":
                raise cherrypy.HTTPError(500, "Error in reading data from camera0")
            else:
                # if the image from camera0 has been read correctly, convert senml into json
                outputJson = json.dumps(senml)
        
        elif (uri [0] == 'camera1'):            
            senml = self.deviceConnector.get_camera1()
            
            if senml is None:
                raise cherrypy.HTTPError(500, "Error: invalid senml")
            
            camera1 = ((senml['e'])[0])['v']

            if camera1 == "Reading error":
                raise cherrypy.HTTPError(500, "Error in reading data from camera1")
            else:
                # if the image from camera0 has been read correctly, convert senml into json
                outputJson = json.dumps(senml)
        else:
            raise cherrypy.HTTPError(404, "Error: uri[0] must be 'temperature', 'humidity', 'camera0' or 'camera1'")
        
        return outputJson


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

    # get IP address of the RPI
    s = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    ip = s.getsockname()[0]
    
    # instantiate a DeviceConnector object
    deviceConnector = DeviceConnector(ip)
    
    # deploy the DeviceConnectorREST class and start the web server
    cherrypy.tree.mount(DeviceConnectorREST(deviceConnector), '/', conf)
    cherrypy.config.update({'server.socket_host': '0.0.0.0'})
    cherrypy.config.update({'server.socket_port': 8080})
    cherrypy.engine.start()
    cherrypy.engine.block()
