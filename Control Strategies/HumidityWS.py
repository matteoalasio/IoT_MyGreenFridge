import time
import json
import requests
import cherrypy
import paho.mqtt.client as PahoMQTT
from HumidityControl import *
import threading

#- MQTT_subscriber:		- /MyGreenFridge/ + user_ID + /humidity
#- MQTT_publisher:		- /GreenFridge/ + user_ID + /Hcontrol 
					#pubblica 0 in caso di valore della temperatura nella norma
					#pubblica error in caso di valore della temperatura o troppo alto o troppo basso


class Hum_MQTT():

	def __init__(self, user_ID, broker_ip, broker_port, control):

		self.user_ID = user_ID
		self.broker = broker_ip
		self.port = broker_port
		self.control = control

		# create an instance of paho.mqtt.client
		self._paho_mqtt = PahoMQTT.Client(self.user_ID, False)

		# register the callback
		self._paho_mqtt.on_connect = self.myOnConnect
		self._paho_mqtt.on_message = self.myOnMessage

	def myOnConnect(self, paho_mqtt, userdata, flags, rc):
		print ("Connected to %s with result code: %d" % (self.broker, rc))

	#Receive the message from the topic 
	def myOnMessage(self, paho_mqtt, userdata, msg):
		# A new message is received
		#message = json.loads(msg.payload.decode('string-escape').strip('"'))
		humidity_read = msg.payload.decode("utf-8")
		#temperature_read = ((message["e"])[0])["v"] #restituisce il valore --> JSON?

		#Control the humidity
		control_status = self.control.hum_check(humidity_read)
		
		if control_status != None:
			#the humidity at this point can be higher or lower wrt the limits
			pub_mess = json.dumps({"v":control_status})
			#{"v":1} if higher, {"v":-1} if lower
			self.myPublish('/MyGreenFridge/' + self.user_ID + '/Hcontrol', pub_mess)
		else:
			#The humidity is in the correct range
			print ("Humidity is ok")
			pub_mess = json.dumps({"v":0})
			self.myPublish('/MyGreenFridge/' + self.user_ID + '/Hcontrol', pub_mess)
				

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
                
                topic = "MyGreenFridge/"+str(self.user_ID)+"/humidity"
                MQTT_humidity.mySubscribe(topic)

                #MQTT_humidity.myPublish(topic, "13")
                humidity_curr = self.control.get_humidity()

                if (humidity_curr != self.control.get_init_humidity()):

               		url = self.catalog_url + "add_sensor?Fridge_ID=" + self.fridge_ID

                	print ("Current Humidity:", humidity_curr)
                	sensor_to_add = {"sensor_ID": self.sensor_ID, "Value": humidity_curr}

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
	hum_init = info["hum_init"]
	hum_curr = hum_init

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
	for fridge in fridges["fridges"]:
		user_ID =  fridge["user"]
		fridge_ID = fridge["ID"]

		HumidityController_init = HumidityControl(hum_init, hum_curr)
		
		MQTT_humidity = Hum_MQTT(user_ID, broker_IP, broker_port, HumidityController_init)
	
		MQTT_humidity.start("/MyGreenFridge/" + user_ID + "/humidity")
		#MQTT_humidity.mySubscribe("/MyGreenFridge/110995/humidity")

		Humidity_Thread = HumidityThread(MQTT_humidity, user_ID, fridge_ID, "Humidity", catalog_URL, HumidityController_init)
		#REST_temperature = Temp_REST(fridge_ID, "Temperature", catalog_URL, TemperatureController_init)
		#REST_temperature.run()
		Humidity_Thread.run()
