import paho.mqtt.client as PahoMQTT
import threading
import time
import json
import requests
import socket
import sys
from ProductsControl import *

class ProductsControlMQTT:

	def __init__(self, clientID, broker, port, productsController):

		self.broker = broker
		self.port = port
		self.clientID = clientID

		self.productsController = productsController

		#self.topic = topic
		self._isSubscriber = True

		# create an instance of paho.mqtt.client
		self._paho_mqtt = PahoMQTT.Client(clientID) 

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

		message = json.loads(msg.payload.decode("utf-8"))

		imageString = ((message["e"])[0])["v"]
		# STRING TO CONVERT
		print("STRING TO CONVERT")
		self.productsController.updateImage(imageString)




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
		#self._topic = topic

	def start(self):
		# manage connection to broker
		self._paho_mqtt.connect(self.broker , self.port)
		self._paho_mqtt.loop_start()

	def stop (self):
		if (self._isSubscriber):
			# remember to unsuscribe if it is working also as subscriber
			self._paho_mqtt.unsubscribe(self._topic)

		self._paho_mqtt.loop_stop()
		self._paho_mqtt.disconnect()




class ProductsThread(threading.Thread):

		def __init__(self, productsControlMQTT):
			threading.Thread.__init__(self)

		def run(self):
			while True:
				
				topicSubscribe = "MyGreenFridge/1234/5678/camera0"
				productsControlMQTT.mySubscribe(topicSubscribe)

				imageString = productsControlMQTT.productsController.getImage()

				topicPublish = "MyGreenFridge/1234/5678/EAN0"

				if imageString != "":

					EANcode = productsControlMQTT.productsController.imageToEan(imageString)

					messageDict = {"EAN0": EANcode}
					messageJson = json.dumps(messageDict)
					
					productsControlMQTT.myPublish(topicPublish, messageJson)

				time.sleep(15)


class RegistrationThread(threading.Thread):
		
		def __init__(self, catalogIP, catalogPort, devIP, devPort):
			threading.Thread.__init__(self)
		
		def run(self):
			url = "http://"+ catalogIP + ":"+ catalogPort + "/"
			while True:

				### register ProductsControlWS as a web service
				dictWS = {"name": ("ProductsControlWS"),
									"IP": devIP,
									"port": devPort}
				jsonWS = json.dumps(dictWS)
				r = requests.post(url+"add_WS", data=jsonWS)
				
				print("ProductsControlWS registered.")

				time.sleep(60)



if __name__ == '__main__':

	# get IP address of the ProductsControlWS
	s = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
	s.connect(("8.8.8.8", 80))
	devIP = s.getsockname()[0]
	devPort = 8690

	# read configuration file
	try:
		configFile = open("configProductsControl.txt", "r")
		configJson = configFile.read()
		configDict = json.loads(configJson)
		configFile.close()
	except OSError:
		sys.exit("ERROR: cannot open the configuration file.")

	catalogIP = configDict["catalogIP"]
	catalogPort = configDict["catalogPort"]

	print("Catalog IP is: " + catalogIP)
	print("Catalog port is " + catalogPort)

	# retrieve the broker IP and the broker port from the Catalog
	catalogURL = "http://" + catalogIP + ":" + catalogPort
	try:
		r = requests.get(catalogURL + "/broker")
		broker = r.json()
		brokerIP = broker["broker_IP"]
		brokerPort = broker["broker_port"]
	except requests.RequestException as err:
		sys.exit("ERROR: cannot retrieve the Broker IP from the Catalog.")

	# register ProductsControlWS as a web service
	regThread = RegistrationThread(catalogIP, catalogPort, devIP, devPort)
	regThread.start()

	# retrieve all the fridges from the Catalog
	r2 = requests.get(catalogURL + "/fridges")
	fridges = r2.json() # fridges is a Python dictionary

	# iterate over all the fridges
	for fridge in fridges["fridges"]:
		userID =  fridge["user"]
		fridgeID = fridge["ID"]
		clientID = "ProductsControlWS_" + userID + "_" + fridgeID

		# get the current value of the image from camera0 which is stored in the Catalog
		for sensor in fridge["sensors"]:
			if (sensor["sensor_ID"] == "camera0"):
				image0Init = sensor["Value"]
				#print(image0Init)

	clientID = "ProductsControlWS_1234_5678"
	
	initialImageString = ""
	productsController = ProductsControl(initialImageString)
	productsControlMQTT = ProductsControlMQTT(clientID, brokerIP, brokerPort, productsController)
	productsControlMQTT.start()

	prodThread = ProductsThread(productsControlMQTT)
	prodThread.start()

