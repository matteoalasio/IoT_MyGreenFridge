import time
import json
import requests
import cherrypy
import paho.mqtt.client as PahoMQTT
from HumidityControl import *
import threading
import sys

#- MQTT_subscriber:		- /MyGreenFridge/ + user_ID + fridge_ID + /humidity
#- MQTT_publisher:		- /GreenFridge/ + user_ID + fridge_ID + /Hcontrol 
					#publish 0 when the humidity is in the correct range
					#publish +1 when the humidity is higher than the permitted value
					#publish -1 when the humidity is lower than the permitted value

class Hum_MQTT():

	def __init__(self, client_ID, user_ID, fridge_ID, broker_ip, broker_port, control):

		self.user_ID = user_ID
		self.fridge_ID = fridge_ID
		self.client_ID = client_ID
		self.broker = broker_ip
		self.port = broker_port
		self.control = control

		# create an instance of paho.mqtt.client
		self._paho_mqtt = PahoMQTT.Client(self.client_ID, False)

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
					

	def start(self, topic):

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



class HumidityThread(threading.Thread):
        
        def __init__(self, MQTT_Humidity, userID, fridgeID, sensor, catalog_URL, control):
            threading.Thread.__init__(self)
            self.MQTT_Humidity = MQTT_Humidity
            self.user_ID = userID
            self.fridge_ID = fridgeID
            self.sensor_ID = sensor
            self.catalog_url = catalog_URL
            self.control = control
        
        def run(self):
            while True:
                
                topic = "MyGreenFridge/"+str(self.user_ID) + '/' + str(self.fridge_ID) + "/humidity"
                MQTT_Humidity.mySubscribe(topic)
               	#File di prova per fare da publisher
               	#with open('prova.txt', 'r') as myfile:
                #	data = myfile.read()
                #MQTT_temperature.myPublish(topic, data)

                hum_curr = self.control.get_humidity()
                #Control the temperature
                control_status = self.control.hum_check(hum_curr)

                topic_pub = "MyGreenFridge/" + str(self.user_ID) + '/' + str(self.fridge_ID) + "/Hcontrol"

                if control_status != None:

					#the humidity at this point can be higher or lower wrt the limits
                	pub_mess = json.dumps({"v":control_status})

					#{"v":1} if higher, {"v":-1} if lower
                	MQTT_Humidity.myPublish(topic_pub, pub_mess)
                else:
                	print ("Humidity is ok for fridge ",  str(self.fridge_ID))
                	pub_mess = json.dumps({"v":0})
                	MQTT_Humidity.myPublish(topic_pub, pub_mess)
							

                #Only when the humidity value is different from the previous one, we change it in the json file
                if (hum_curr != self.control.get_init_humidity()):
                	print("Changing the humidity!")
                	hum_init = self.control.update_init_humidity(hum_curr)
               		url = self.catalog_url + "update_sensor?Fridge_ID=" + self.fridge_ID

                	
                	sensor_to_add = {"sensor_ID": self.sensor_ID, "Value": hum_curr}

                #Posting on CATALOG the current value of the sensor
                	try:
                		r = requests.post(url, data = json.dumps(sensor_to_add))
                		r.raise_for_status()

               		except requests.HTTPError as err:
                		print ("Error in posting, aborting")
                		return

                time.sleep(15)


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

	i=0
	#It iterates on all the available fridges in the system
	for fridge in fridges["fridges"]:
		user_ID =  fridge["user"]
		fridge_ID = fridge["ID"]
		client_ID = "humidityclient_" + str(i)

		i=i+1

		for sensor in fridge["sensors"]:
			if (sensor["sensor_ID"] == "humidity"):
				hum_init = sensor["Value"]

		hum_curr = hum_init

		HumidityController = HumidityControl(hum_init, hum_curr)
		
		MQTT_Humidity = Hum_MQTT(client_ID, user_ID, fridge_ID, broker_IP, broker_port, HumidityController)
	
		MQTT_Humidity.start("/MyGreenFridge/" + str(user_ID) + '/' + str(fridge_ID) + "/humidity")

		Humidity_Thread = HumidityThread(MQTT_Humidity, user_ID, fridge_ID, "Humidity", catalog_URL, HumidityController)
		#REST_temperature = Temp_REST(fridge_ID, "Temperature", catalog_URL, TemperatureController_init)
		#REST_temperature.run()

		Humidity_Thread.start()
