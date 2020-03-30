from DeviceConnector import *
import cherrypy
import json
import socket
import paho.mqtt.client as PahoMQTT       
import threading
import requests

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


class DeviceConnectorMQTT:
	
	def __init__(self, clientID, broker, port, deviceConnector):
		
		self.broker = broker
		self.port = port
		self.clientID = clientID

		self._topic = ""
		self._isSubscriber = False

		# create an instance of paho.mqtt.client
		self._paho_mqtt = PahoMQTT.Client(clientID, False) 

		# register the callback
		self._paho_mqtt.on_connect = self.myOnConnect
		self._paho_mqtt.on_message = self.myOnMessageReceived


	def myOnConnect (self, paho_mqtt, userdata, flags, rc):
		print ("Connected to broker: " + str(self.broker) + ", with result code: " + str(rc))

	def myOnMessageReceived (self, paho_mqtt , userdata, msg):
		# A new message is received
		#self.notifier.notify (msg.topic, msg.payload)
		print("Message received: " + str(msg.payload))
		print("On topic: ", str(msg.topic))


	def myPublish (self, topic, msg):
		# if needed, you can do some computation or error-check before publishing
		print ("Publishing message: " + str(msg))
		print("with topic: " + str(topic))
		# publish a message with a certain topic
		self._paho_mqtt.publish(topic, msg, 2)

	def mySubscribe (self, topic):
		# if needed, you can do some computation or error-check before subscribing
		print ("Subscribing to topic: " +str(topic))
		# subscribe for a topic
		self._paho_mqtt.subscribe(topic, 2)

		# just to remember that it works also as a subscriber
		self._isSubscriber = True
		self._topic = topic

	def start(self):
		#manage connection to broker
		self._paho_mqtt.connect(self.broker , self.port)
		self._paho_mqtt.loop_start()

	def stop (self):
		if (self._isSubscriber):
			# remember to unsuscribe if it is working also as subscriber 
			self._paho_mqtt.unsubscribe(self._topic)

		self._paho_mqtt.loop_stop()
		self._paho_mqtt.disconnect()
		
class TemperatureThread(threading.Thread):
        
        def __init__(self, deviceConnector, deviceConnectorMQTT):
            threading.Thread.__init__(self)
        
        def run(self):
            while True:
                Tsenml = deviceConnector.get_temperature()
                msg = json.dumps(Tsenml)
                topic = "MyGreenFridge/"+str(deviceConnector.userID)+"/"+str(deviceConnector.fridgeID)+"/temperature"
                deviceConnectorMQTT.myPublish(topic, msg)
                time.sleep(15)

class HumidityThread(threading.Thread):
        
        def __init__(self, deviceConnector, deviceConnectorMQTT):
            threading.Thread.__init__(self)
        
        def run(self):
            while True:
                Hsenml = deviceConnector.get_humidity()
                msg = json.dumps(Hsenml)
                topic = "MyGreenFridge/"+str(deviceConnector.userID)+"/"+str(deviceConnector.fridgeID)+"/humidity"
                deviceConnectorMQTT.myPublish(topic, msg)
                time.sleep(15)
                
class Camera0Thread(threading.Thread):
        
        def __init__(self, deviceConnector, deviceConnectorMQTT):
            threading.Thread.__init__(self)
        
        def run(self):
            while True:
                C0senml = deviceConnector.get_camera0()
                msg = json.dumps(C0senml)
                topic = "MyGreenFridge/"+str(deviceConnector.userID)+"/"+str(deviceConnector.fridgeID)+"/camera0"
                deviceConnectorMQTT.myPublish(topic, msg)
                time.sleep(15)
                
class Camera1Thread(threading.Thread):
        
        def __init__(self, deviceConnector, deviceConnectorMQTT):
            threading.Thread.__init__(self)
        
        def run(self):
            while True:
                C1senml = deviceConnector.get_camera1()
                msg = json.dumps(C1senml)
                topic = "MyGreenFridge/"+str(deviceConnector.userID)+"/"+str(deviceConnector.fridgeID)+"/camera1"
                deviceConnectorMQTT.myPublish(topic, msg)
                time.sleep(15)
                
class RegistrationThread(threading.Thread):
        
        def __init__(self, deviceConnector, catalogIP, catalogPort):
            threading.Thread.__init__(self)
        
        def run(self):
            url = "http://"+ catalogIP + ":"+ catalogPort + "/"
            while True:
                # register user
                dictUser = {"ID": deviceConnector.userID,
                            "nickname": None}
                jsonUser = json.dumps(dictUser)
                #r1 = requests.post(url+"add_user", data=jsonUser)
                dictFridge = {"ID": deviceConnector.fridgeID,
                              "user": None,
                              "sensors":[],
                              "products": [],
                              "IP": deviceConnector.ip,
                              "port": deviceConnector.port}
                jsonFridge = json.dumps(dictFridge)
                #r2 = requests.post(url+"add_fridge", data=jsonFridge)
                print(url)
                print(dictUser)
                print(dictFridge)
                time.sleep(5)



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
    
    # PROVA --> poi sistemiamo da dove vengono questi parametri
    userID = "pippo"
    clientID = "ciccio"
    broker = ip
    port = 1883
    
    # read configuration file
    with open("configDeviceConnector.txt", "r") as configFile:
        configJson = configFile.read()
        configDict = json.loads(configJson)
        configFile.close()
        
    userID = configDict["userID"]
    catalogIP = configDict["catalogIP"]
    catalogPort = configDict["catalogPort"]
    fridgeID = configDict["fridgeID"]
    
    print("Catalog IP is: " + catalogIP)
    print("Catalog port is " + catalogPort)
    
    
    # instantiate a DeviceConnector object
    deviceConnector = DeviceConnector(ip, userID, fridgeID)
    
    deviceConnectorMQTT = DeviceConnectorMQTT(clientID, broker, port, deviceConnector)
    deviceConnectorMQTT.start()
    
    tempThread = TemperatureThread(deviceConnector, deviceConnectorMQTT)
    humThread = HumidityThread(deviceConnector, deviceConnectorMQTT)
    cam0Thread = Camera0Thread(deviceConnector, deviceConnectorMQTT)
    cam1Thread = Camera1Thread(deviceConnector, deviceConnectorMQTT)
    regThread = RegistrationThread(deviceConnector, catalogIP, catalogPort)
    
    tempThread.start()
    humThread.start()
    #cam0Thread.start()
    #cam1Thread.start()
    regThread.start()
    
    # deploy the DeviceConnectorREST class and start the web server
    cherrypy.tree.mount(DeviceConnectorREST(deviceConnector), '/', conf)
    cherrypy.config.update({'server.socket_host': '0.0.0.0'})
    cherrypy.config.update({'server.socket_port': 8080})
    cherrypy.engine.start()
    cherrypy.engine.block()
