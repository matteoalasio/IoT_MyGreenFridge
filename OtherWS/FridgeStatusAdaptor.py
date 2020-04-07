"""
The Fridge Status Adaptor is an MQTT subscriber that receives data about the status of the fridge
from the control strategies. It communicates with the Temperature Alarm Web Service using REST
Web Services, indicating whether the temperature value is above the threshold. With the same kind
of communication, it also allows the user to visualize the current status of the fridge on the available
interfaces, in this case a Telegram Bot.
"""
import socket
import time
import json
import requests
import cherrypy
import paho.mqtt.client as PahoMQTT
from FridgeStatusControl import *
import threading

class Fridge_GET():																	

	exposed = True

	def __init__(self, controller):
		self.controller = controller

	def GET(self, *uri, **params):

		#/status?User_ID=<IDUser>&Fridge_ID=<IDFridge>
		if (uri[0] == "status"):
			user_ID = params['User_ID']
			fridge_ID = params['Fridge_ID']
			info = json.dumps({"Current status":self.controller.get_status_fridge(user_ID,fridge_ID)})
			return info

		else:
			raise cherrypy.HTTPError(400, "Your GET request has URI not correct")


class Fridge_MQTT():

	def __init__(self, user_ID, fridge_ID, broker_ip, broker_port, control):

		self.user_ID = user_ID
		self.fridge_ID = fridge_ID
		self.broker = broker_ip
		self.port = broker_port
		self.control = control

		# create an instance of paho.mqtt.client
		self._paho_mqtt = PahoMQTT.Client(self.user_ID)

		# register the callback
		self._paho_mqtt.on_connect = self.myOnConnect
		self._paho_mqtt.on_message = self.myOnMessage

	def myOnConnect(self, paho_mqtt, userdata, flags, rc):
		print ("Connected to %s with result code: %d" % (self.broker, rc))

	#Receive the message from the topic 
	def myOnMessage(self, paho_mqtt, userdata, msg):
		# A new message is received
		message = msg.payload.decode("utf-8")
		msg = json.loads(message)
		#print ("Message received:", msg['v'])

		#when a message is received, the control status is updated
		control_status = self.control.update_status(self.user_ID, self.fridge_ID, msg['v'])	
		print (control_status)			

	def start(self):

		self._paho_mqtt.connect(self.broker, self.port)
		self._paho_mqtt.loop_start()
	

	def stop(self):

		self._paho_mqtt.loop_stop()
		self._paho_mqtt.disconnect()

	def mySubscribe(self, topic):
		print ("subscribing to %s" % (topic)) # subscribe for a topic
		self._paho_mqtt.subscribe(topic, 2)

	def myPublish(self, topic, message):
		print ("Publishing on ", topic, "with message ", message)
		self._paho_mqtt.publish(topic, message, 2)


class FridgeThread(threading.Thread):
        
        def __init__(self, MQTT_Fridge, userID, fridgeID, catalog_URL, control):
            threading.Thread.__init__(self)
            self.MQTT_Fridge = MQTT_Fridge
            self.user_ID = userID
            self.fridge_ID = fridgeID
            self.catalog_url = catalog_URL
            self.control = control
        
        def run(self):
            while True:
                
                topic = "/MyGreenFridge/"+ str(self.user_ID) + '/' + self.fridge_ID + "/Tcontrol"
                MQTT_Fridge.mySubscribe(topic)

                with open('prova_2.txt', 'r') as myfile:
                	data = myfile.read()
                MQTT_Fridge.myPublish(topic, data)

                time.sleep(5)


if __name__ == '__main__':														

	#Open file of configuration, including the data of the catalog
	file = open("Configuration.txt","r")
	info = json.loads(file.read())

	catalog_IP = info["catalog_IP"]
	catalog_Port = info["catalog_port"]

	file.close()
	catalog_URL = "http://" + catalog_IP + catalog_Port
	try:
		r = requests.get(catalog_URL + "broker")
		broker = r.json()
		broker_IP = broker["broker_IP"]
		broker_port = broker["broker_port"]
	except requests.HTTPError as err:
		print ("Error retrieving the broker")
		sys.exit()

	r2 = requests.get(catalog_URL + "fridges")
	fridges = r2.json()

	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	s.connect(("8.8.8.8", 80))
	ip = s.getsockname()[0]
	port = "8787"

	web_service = json.dumps({"name":"FridgeStatusWS", "IP":ip, "port":port})
	r3 = requests.post(catalog_URL + "add_WS", web_service)


	#It iterates on all the available fridges in the system
	for fridge in fridges["fridges"]:
		user_ID =  fridge["user"]
		fridge_ID = fridge["ID"]
		status_init = 3
		status_curr = status_init #both are inizialized with a default value equal to 3

		FridgeController = FridgeStatusControl(status_init, status_curr)

		MQTT_Fridge = Fridge_MQTT(user_ID, fridge_ID, broker_IP, broker_port, FridgeController)
		MQTT_Fridge.start()

		Fridge_Thread = FridgeThread(MQTT_Fridge, user_ID, fridge_ID, catalog_URL, FridgeController)
		Fridge_Thread.start()


		conf = {'/':{'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
			'tools.sessions.on': True}}

		cherrypy.tree.mount(Fridge_GET(FridgeController), '/', conf)
		cherrypy.config.update({'server.socket_host': '0.0.0.0'})
		cherrypy.config.update({'server.socket_port': 8787})
		cherrypy.engine.start()
		cherrypy.engine.block()

