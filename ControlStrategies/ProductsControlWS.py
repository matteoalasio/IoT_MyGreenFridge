import paho.mqtt.client as PahoMQTT
import threading
import time

class ProductsControlMQTT:

	def __init__(self, clientID, broker, port):

		self.broker = broker
		self.port = port
		self.clientID = clientID

		self._topic = ""
		self._isSubscriber = True

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

class ProductsThread(threading.Thread):

        def __init__(self, productsControlMQTT):
            threading.Thread.__init__(self)

        def run(self):
            while True:
                topic = "MyGreenFridge/#"
                productsControlMQTT.mySubscribe(topic)
                
                time.sleep(15)

if __name__ == '__main__':

    brokerIP = "localhost"
    brokerPort = 1883
    clientID = "ProductsControlWS"
    productsControlMQTT = ProductsControlMQTT(clientID, brokerIP, brokerPort)
    productsControlMQTT.start()

    prodThread = ProductsThread(productsControlMQTT)
    prodThread.start()

