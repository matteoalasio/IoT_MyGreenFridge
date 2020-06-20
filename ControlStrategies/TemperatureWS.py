import time
import json
import requests
import cherrypy
import paho.mqtt.client as PahoMQTT
from TemperatureControl import *
import threading
import socket
import sys

#- MQTT_subscriber:		- /MyGreenFridge/ + user_ID + fridge_ID + /temperature
#- MQTT_publisher:		- /GreenFridge/ + user_ID + fridge_ID + /Tcontrol
					#publish 0 when the temperature is in the correct range
					#publish +1 when the temperature is higher than the permitted value
					#publish -1 when the temperature is lower than the permitted value

class Temp_MQTT():

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

		temperature_read = int(((message["e"])[0])["v"])
		print ("Current temperature:", temperature_read)

		update_temperature = self.control.update_temperature(temperature_read)



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



class TemperatureThread(threading.Thread):

        def __init__(self, MQTT_temperature, userID, fridgeID, sensor, catalog_URL, control):
            threading.Thread.__init__(self)
            self.MQTT_temperature = MQTT_temperature
            self.user_ID = userID
            self.fridge_ID = fridgeID
            self.sensor_ID = sensor
            self.catalog_url = catalog_URL
            self.control = control

        def run(self):
            while True:

                topic = "MyGreenFridge/"+str(self.user_ID) + '/' + self.fridge_ID + "/temperature"
                MQTT_temperature.mySubscribe(topic)

                temp_curr = self.control.get_temperature()

                #Control the temperature
                control_status = self.control.temp_check(temp_curr)
                topic_pub = "/MyGreenFridge/" + str(self.user_ID) + '/' + str(self.fridge_ID) + "/Tcontrol"

                if control_status != None:
					#the temperature at this point can be higher or lower wrt the limits
                	pub_mess = json.dumps({"v":control_status})
					#{"v":1} if higher, {"v":-1} if lower
                	MQTT_temperature.myPublish(topic_pub, pub_mess)

                else:
                	print ("Temperature is ok")
                	pub_mess = json.dumps({"v":0})
                	MQTT_temperature.myPublish(topic_pub, pub_mess)


                #Only when the temperature value is different from the previous one, we change it in the CATALOG file
                if (temp_curr != self.control.get_init_temperature()):
                	print("Changing the temperature!")

                	temp_init = self.control.update_init_temperature(temp_curr)

               		url = self.catalog_url + "update_sensor?Fridge_ID=" + self.fridge_ID
                	sensor_to_add = {"sensor_ID": self.sensor_ID, "Value": temp_curr}

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
                web_service = json.dumps({"name": "TemperatureWS", "IP": self.WS_IP, "port": self.WS_Port})
                r1 = requests.post(catalog_URL + "add_WS", web_service)

                print("TemperatureWS registered.")

                time.sleep(60*60)


if __name__ == '__main__':

	#Open file of configuration, including the data of the catalog
	file = open("../configSystem.json","r")
	info = json.loads(file.read())

	catalog_IP = info["catalogIP"]
	catalog_Port = ":" + info["catalogPort"] + "/"

	file.close()
	catalog_URL = "http://" + catalog_IP + catalog_Port

    # Register the WS in the CATALOG
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	s.connect(("8.8.8.8", 80))
	ip = s.getsockname()[0]
	port = "8587"

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


	r2 = requests.get(catalog_URL + "fridges")
	fridges = r2.json()
	i=0

	#Iterating on all the available fridges in the system
	for fridge in fridges["fridges"]:
		user_ID =  fridge["user"]
		fridge_ID = fridge["ID"]
		client_ID = "temperatureclient_" + str(i)

		i=i+1

		temp_init = 0

		for sensor in fridge["sensors"]:
			if (sensor["sensor_ID"] == "temperature"):
				temp_init = sensor["Value"]


		temp_curr = temp_init

		TemperatureController = TemperatureControl(temp_init, temp_curr)

		MQTT_temperature = Temp_MQTT(client_ID, user_ID, fridge_ID, broker_IP, broker_port, TemperatureController)
		MQTT_temperature.start()

		Temperature_Thread = TemperatureThread(MQTT_temperature, user_ID, fridge_ID, "temperature", catalog_URL, TemperatureController)
		Temperature_Thread.start()

