import time
import json
import requests
import cherrypy
import paho.mqtt.client as PahoMQTT
from HumidityControl import *
import threading
import socket
import sys


class Hum_MQTT():

	def __init__(self, client_ID, user_ID, fridge_ID, broker_ip, broker_port, control):

		self.user_ID = user_ID
		self.client_ID = client_ID
		self.fridge_ID = fridge_ID
		self.broker = broker_ip
		self.port = broker_port
		self.control = control

		# create an instance of paho.mqtt.client
		self._paho_mqtt = PahoMQTT.Client(self.client_ID)

		# register the callback
		self._paho_mqtt.on_connect = self.myOnConnect
		self._paho_mqtt.on_message = self.myOnMessage

	def myOnConnect(self, paho_mqtt, userdata, flags, rc):
		print ("Connected to %s with result code: %d" % (self.broker, rc))

	#Receive the message from the topic
	def myOnMessage(self, paho_mqtt, userdata, msg):
		# A new message is received
		message = json.loads(msg.payload.decode("utf-8"))

		humidity_read = int(((message["e"])[0])["v"])
		print ("Current humidity:", humidity_read)

		update_humidity = self.control.update_humidity(humidity_read)



	def start(self):

		self._paho_mqtt.connect(self.broker, self.port)
		self._paho_mqtt.loop_start()


	def stop(self):

		self._paho_mqtt.loop_stop()
		self._paho_mqtt.disconnect()

	def mySubscribe(self, topic):
		print ("subscribing to %s" % (topic))
		self._paho_mqtt.subscribe(topic, 2)

	def myPublish(self, topic, message):
		print ("Publishing on ", topic, "with message ", message)
		self._paho_mqtt.publish(topic, message, 2)



class HumidityThread(threading.Thread):

		def __init__(self, MQTT_humidity, userID, fridgeID, sensor, catalog_URL, control):
			threading.Thread.__init__(self)
			self.MQTT_humidity = MQTT_humidity
			self.user_ID = userID
			self.fridge_ID = fridgeID
			self.sensor_ID = sensor
			self.catalog_url = catalog_URL
			self.control = control

		def run(self):
			while True:

				topic = "MyGreenFridge/"+str(self.user_ID) + '/' + self.fridge_ID + "/humidity"
				self.MQTT_humidity.mySubscribe(topic)

				hum_curr = self.control.get_humidity()

				#Control the temperature
				control_status = self.control.hum_check(hum_curr)
				topic_pub = "MyGreenFridge/" + str(self.user_ID) + '/' + str(self.fridge_ID) + "/Hcontrol"

				if control_status != None:
					#the humidity at this point can be higher or lower wrt the limits
					pub_mess = json.dumps({"v":control_status})
					#{"v":1} if higher, {"v":-1} if lower
					self.MQTT_humidity.myPublish(topic_pub, pub_mess)

				else:
					pub_mess = json.dumps({"v":0})
					self.MQTT_humidity.myPublish(topic_pub, pub_mess)


				#Only when the humidity value is different from the previous one, we change it in the CATALOG file
				if (hum_curr != self.control.get_init_humidity()):

					hum_init = self.control.update_init_humidity(hum_curr)

					url = self.catalog_url + "update_sensor?Fridge_ID=" + self.fridge_ID
					sensor_to_add = {"sensor_ID": self.sensor_ID, "Value": hum_curr}

				#Posting on CATALOG the current value of the sensor
					try:
						r = requests.put(url, data = json.dumps(sensor_to_add))
						r.raise_for_status()

					except requests.HTTPError as err:
						print ("Error in posting, aborting")
						return

				time.sleep(15)

class RegistrationThread(threading.Thread):

		def __init__(self, catalogIP, catalogPort, WS_IP, WS_Port):
			threading.Thread.__init__(self)
			self.catalogIP = catalogIP
			self.catalogPort = catalogPort
			self.WS_IP = WS_IP
			self.WS_Port = WS_Port

		def run(self):
			url = "http://"+ self.catalogIP + ":"+ self.catalogPort + "/"
			while True:

				### register ProductsControlWS as a web service
				web_service = json.dumps({"name": "HumidityWS", "IP": self.WS_IP, "port": self.WS_Port})
				r1 = requests.post(catalog_URL + "add_WS", web_service)

				print("HumidityWS registered.")

				time.sleep(60)



class ControlThread(threading.Thread):

		def __init__(self, catalogIP, catalogPort, initFridges, brokerIP, brokerPort):

			threading.Thread.__init__(self)

			self.catalogIP = catalogIP
			self.catalogPort = catalogPort
			self.initFridges = initFridges
			self.broker_IP = brokerIP
			self.broker_port = brokerPort


		def run(self):


			catalog_URL = "http://" + self.catalogIP + ":" + self.catalogPort
			oldFridges = self.initFridges

			while True:

				# retrieve all the fridges from the Catalog
				r = requests.get(catalog_URL + "/fridges")
				i=0

				dictCurrFridges = r.json() # fridges is a Python dictionary
				currFridges = []
				for fridge in dictCurrFridges["fridges"]:
					currFridges.append(fridge["ID"])


				# get new fridges that have been added
				diffFridges = list(set(currFridges) - set(oldFridges))

				#listThreads = threading.enumerate()
				#print(listThreads)

				for fridge_ID in diffFridges:

					for fridge in dictCurrFridges["fridges"]:

						if fridge_ID == fridge["ID"]:

							user_ID =  fridge["user"]
							client_ID = "humidityclient_" + str(i)

							i=i+1

							hum_init = 0

							for sensor in fridge["sensors"]:
								if (sensor["sensor_ID"] == "humidity"):
									hum_init = sensor["Value"]


							hum_curr = hum_init

							HumidityController = HumidityControl(hum_init, hum_curr)

							MQTT_humidity = Hum_MQTT(client_ID, user_ID, fridge_ID, self.broker_IP, self.broker_port, HumidityController)
							MQTT_humidity.start()

							Humidity_Thread = HumidityThread(MQTT_humidity, user_ID, fridge_ID, "humidity", catalog_URL, HumidityController)
							Humidity_Thread.start()


				time.sleep(60*60)
				oldFridges = currFridges.copy()

if __name__ == '__main__':

		#Open file of configuration, including the data of the catalog
	file = open("../configSystem.json","r")
	info = json.loads(file.read())

	catalog_IP = info["catalogIP"]
	catalog_Port = info["catalogPort"]

	file.close()
	catalog_URL = "http://" + catalog_IP + ":" + catalog_Port + "/"

	# Register the WS in the CATALOG
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	s.connect(("8.8.8.8", 80))
	ip = s.getsockname()[0]
	port = "8487"

	regThread = RegistrationThread(catalog_IP, catalog_Port, ip, port)
	regThread.start()


	try:
		r = requests.get(catalog_URL + "broker")
		broker = r.json()
		broker_IP = broker["broker_IP"]
		broker_port = broker["broker_port"]
	except requests.HTTPError as err:
		print ("Error retrieving the broker")
		sys.exit()


	initFridges = []

	controlThread = ControlThread(catalog_IP, catalog_Port, initFridges, broker_IP, broker_port)
	controlThread.start()
