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

		def __init__(self, productsControlMQTT, userID, fridgeID, sensorID, catalogIP, catalogPort):
			threading.Thread.__init__(self)

		def run(self):

			# subscribe to the topic related to camera0
			topicSubscribe = "MyGreenFridge/" + userID + "/" + fridgeID + "/camera0"
			productsControlMQTT.mySubscribe(topicSubscribe)

			url = "http://"+ catalogIP + ":"+ catalogPort + "/update_sensor?Fridge_ID=" + fridgeID

			while True:
				
				# imageString is received on topicSubscribe and stored in productsControlMQTT.productsController
				imageString = productsControlMQTT.productsController.getImage()

				
				# publish EANcode corresponding to imageString on the relative topic
				topicPublish = "MyGreenFridge/" + userID + "/" + fridgeID + "/EAN0"

				try:

					# get EANcode from imageString	
					EANcode = productsControlMQTT.productsController.imageToEan(imageString)

					messageDict = {"EAN0": EANcode}
					messageJson = json.dumps(messageDict)
					
					# publish on topicPublish
					productsControlMQTT.myPublish(topicPublish, messageJson)

				except: # catch all exceptions
					
					# if the EAN code cannot be retrieved, print an error
					e = sys.exc_info()[0]
					print("ERROR: cannot publish EAN0.")
					print(e)

				# update the value of the camera0 image on the Catalog,
				# only if it is different from the value that is currently stored on the Catalog

				dictC0 = {"sensor_ID": sensorID,
							"Value": imageString}
				jsonC0 = json.dumps(dictC0)
				r = requests.put(url, data=jsonC0)


				time.sleep(15)


class RegistrationThread(threading.Thread):
		
		def __init__(self, catalogIP, catalogPort, devIP, devPort):
			threading.Thread.__init__(self)
		
		def run(self):
			url = "http://"+ catalogIP + ":"+ catalogPort + "/add_WS"
			while True:

				### register ProductsControlWS as a web service
				dictWS = {"name": ("ProductsControlWS"),
									"IP": devIP,
									"port": devPort}
				jsonWS = json.dumps(dictWS)
				r = requests.post(url, data=jsonWS)
				
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

	sensorID = "camera0"

	# iterate over all the fridges
	for fridge in fridges["fridges"]:
		
		userID =  fridge["user"]
		fridgeID = fridge["ID"]
		clientID = "ProductsControlWS_" + userID + "_" + fridgeID

		# get the current value of the image from camera0 which is stored in the Catalog
		for sensor in fridge["sensors"]:
			if (sensor["sensor_ID"] == sensorID):
				initialImageString = sensor["Value"]

		productsController = ProductsControl(initialImageString)
		productsControlMQTT = ProductsControlMQTT(clientID, brokerIP, brokerPort, productsController)
		productsControlMQTT.start()

		prodThread = ProductsThread(productsControlMQTT, userID, fridgeID, sensorID, catalogIP, catalogPort)
		prodThread.start()



