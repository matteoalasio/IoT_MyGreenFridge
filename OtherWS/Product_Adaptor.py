#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr 20 16:32:39 2020

@author: macste
"""

import paho.mqtt.client as PahoMQTT
import threading
import time
import json
import requests
import socket
import sys
import cherrypy


class ProductsAdaptorREST(object):

	# expose the Web Services
	exposed = True

	def __init__(self,catalog_URL):
		self.catalog_URL = catalog_URL


	def GET (self, *uri, **params):
		pass
		return

	def POST (self, *uri, **params):
		# riceve dal telegram bot un body contenente (prod_id, fridge_id, exp date)

		# POST AL CATALOG dell'exp_Date
		# - /add_expiration?Fridge_ID=<IDFridge>&Product_ID=<IDProduct> : Add the expiration date of a specified product
		# The body required is {"day":"", "month":"", "year":""}
		if len(uri) == 0:
			raise cherrypy.HTTPError(400)

		json_body = cherrypy.request.body.read()
		body = json.loads(json_body) #(exp date)
		print (body)
		if uri[0] == 'add_expiration':
			product_ID = params['Product_ID']
			fridge_ID = params['Fridge_ID']
			print("okokok")
			r3 = requests.post(catalog_URL + "add_expiration?Fridge_ID=" + fridge_ID + "&Product_ID=" + product_ID, data=json.dumps(body))
			print("data di scadenza aggiunta al frigo")

		if uri[0] == 'add_wasted':
			product_ID = params['Product_ID']
			fridge_ID = params['Fridge_ID']
			if body["status"] == "wasted":
				corpo = { "product_ID": product_ID}
				print("okokok")
				r3 = requests.post(catalog_URL + "add_wasted?Fridge_ID=" + fridge_ID, data=json.dumps(corpo))
				print("prodotto rimosso")

	def PUT (self, *uri, **params):
		pass
		return

	def DELETE(self):
		pass
		return

class ProductsAdaptorMQTT:

	def __init__(self, clientID , userID , fridgeID ,  broker , port , catalog_Port , url_barcode_WS , url_product_input_WS , url_product_output_WS):

		self.broker = broker
		self.port = port  #porta broker
		self.clientID = clientID
		self.userID = userID
		self.fridgeID = fridgeID
		self.catalog_Port = catalog_Port
		self.url_barcode_WS = url_barcode_WS
		self.url_product_input_WS = url_product_input_WS
		self.url_product_output_WS = url_product_output_WS

		#self.topic = topic
		self._isSubscriber = True

		# create an instance of paho.mqtt.client
		self._paho_mqtt = PahoMQTT.Client(clientID)

		# register the callback
		self._paho_mqtt.on_connect = self.myOnConnect
		self._paho_mqtt.on_message = self.myOnMessageReceived


	def myOnConnect (self, paho_mqtt, userdata, flags, rc):
		print ("Connected to broker: " + str(self.broker) + ", with result code: " + str(rc))

	def mySubscribe (self, topic):
	# if needed, you can do some computation or error-check before subscribing
		print ("Subscribing to topic: " + str(topic))
	# subscribe for a topic
		self._paho_mqtt.subscribe(topic, 2)
	# just to remember that it works also as a subscriber
		self._isSubscriber = True

	def myOnMessageReceived (self, paho_mqtt , userdata, msg):
		#print("Message received: " + str(msg.payload))
		#print("On topic: ", str(msg.topic))
		print("Message received on topic: ", str(msg.topic))
		# barcode_port = "8689"
		# catalog_port = "8080"
		# prod_in_port = "8690"
		# prod_out_port = "8691"

		if (msg.topic == "MyGreenFridge/" + userID + "/" + fridgeID + "/EAN0"):

			print("prodotto da inserire ricevuto")

				   # BARCODE CONVERSION WS ---- ottieni lista Prod_ID Brand
				   # 8076809531191 EAN EXAMPLE
			message = json.loads(msg.payload.decode("utf-8"))
# 			EAN_IN = (msg.payload)
			print(message)

			# GET al barcode conversion url: - /product?EAN=<ean>

			r0 = requests.get(url_barcode_WS + "product?EAN=" + str(message))
			prod_in = r0.json() #contiene il nome e la marca del prodotto inserito
			print(prod_in)        #prod_in = {"product": product_name, "brand": brand}

			# POST AL CATALOG per aggiungere prodotto individuato
			# - /add_product?Fridge_ID=<IDFridge> : Add a product to the correspondant Fridge
			# The body required is {"product_ID":"", "brand":""}

			body = {"product_ID": prod_in["product"] , "brand": prod_in["brand"]}

			catalog_url = "http://localhost" + catalog_Port
			r1 = requests.post(catalog_url + "add_product?Fridge_ID=" + fridgeID, data = json.dumps(body))
			print("prodotto aggiunto al catalog")

			# GET AL PROD_INPUT_WS per ricavare expiratio_date
			# /insert_product?product_name=<name>&brands=<brand>

			r2 = requests.get(url_product_input_WS  + "insert_product?FridgeID=" + fridgeID + "&userID=" + userID + "&product_name=" + prod_in["product"] + "&brands=" + prod_in["brand"])

			print("get al ws fatta")

			#####

		if (msg.topic == "MyGreenFridge/" + userID + "/" + fridgeID + "/EAN1"):

			print("prodotto da eliminare ricevuto")

				   # BARCODE CONVERSION
			message = json.loads(msg.payload.decode("utf-8"))
# 			EAN_IN = (msg.payload)
			print(message)

			# GET al barcode conversion url: - /product?EAN=<ean>

			r0 = requests.get(url_barcode_WS + "product?EAN=" + str(message))
			prod_out = r0.json() #contiene il nome e la marca del prodotto inserito
			print(prod_out)         #dictOutput = {"product": product_name, "brand": brand}

			# POST AL CATALOG per rimuovere prodotto individuato
			# - /product/Fridge_ID?Prod_ID=<IDProd> : Delete a product for a specified fridge.

			catalog_url_delete = "http://localhost" + catalog_Port + fridgeID + "?Prod_ID=" + prod_out["product"]
			r1 = requests.delete(catalog_url_delete)
			print("prodotto rimosso dal frigo")

			# GET AL PROD_OUtPUT_WS per ottenere status

			r2 = requests.get(url_product_output_WS  + "delete_product?FridgeID=" + fridgeID + "&userID=" + userID + "&product_name=" + prod_out["product"] + "&brands=" + prod_out["brand"])

			print("get al ws fatta")

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

class RegistrationThread(threading.Thread):

		def __init__(self, catalogIP, catalogPort, WS_IP, WS_Port):
			threading.Thread.__init__(self)
			self.catalogIP = catalogIP
			self.catalogPort = catalogPort
			self.WS_IP = WS_IP
			self.WS_Port = WS_Port

		def run(self):
			url = "http://"+ self.catalogIP + self.catalogPort
			while True:

				### register ProductsControlWS as a web service
				web_service = json.dumps({"name": "ProductAdaptorWS", "IP": self.WS_IP, "port": self.WS_Port})
				r1 = requests.post(url + "add_WS", web_service)

				print("ProductAdaptorWS registered.")

				time.sleep(60*60)


class ProductsAdaptorThread(threading.Thread):

		def __init__(self, MQTT_ProductsAdaptor):
			threading.Thread.__init__(self)
			self.userID = MQTT_ProductsAdaptor.userID
			self.fridgeID = MQTT_ProductsAdaptor.fridgeID

		def run(self):
			while True:

				topic1 = "MyGreenFridge/" + self.userID + "/" + self.fridgeID + "/EAN0"
				MQTT_ProductsAdaptor.mySubscribe(topic1)
				topic2 = "MyGreenFridge/" + self.userID + "/" + self.fridgeID + "/EAN1"
				MQTT_ProductsAdaptor.mySubscribe(topic2)

				time.sleep(15)

if __name__ == '__main__':

	conf = {
		'/': {
			'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
			'tools.sessions.on': True
		}
	}
	# # get IP address of the RPI
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	s.connect(("8.8.8.8", 80))
	ip = s.getsockname()[0]
	devPort = 8586

	#Open file of configuration, including the data of the catalog
	file = open("Configuration.txt","r")
	info = json.loads(file.read())
	file.close()

	catalog_IP = info["catalog_IP"]
	catalog_Port = info["catalog_port"]
	catalog_URL =  "http://" + catalog_IP + catalog_Port

	regThread = RegistrationThread(catalog_IP, catalog_Port, ip, devPort)
	regThread.start()

#  richiedere poorte dinamicamente
	try:
		r = requests.get(catalog_URL + "broker")
		broker = r.json()
		broker_IP = broker["broker_IP"]
		broker_port = broker["broker_port"]
	except requests.HTTPError:
		print ("Error retrieving the broker")
		sys.exit()

	r2 = requests.get(catalog_URL + "fridges")
	fridges = r2.json()

	r3 = requests.get( catalog_URL + "web_service?Name=" + "BarcodeConversionWS" )
	barcode = r3.json()
	IP = barcode['URL']['IP']
	barcode_port = barcode['URL']['port']
	url_barcode_WS = "http://" + str(IP) + ":" + str(barcode_port) + "/"


	r4 = requests.get(catalog_URL + "web_service?Name=" + "ProductInputWS")
	product_input = r4.json()
	product_input_port = product_input['URL']['port']
	url_product_input_WS = "http://" + str(IP) + ":" + str(product_input_port) + "/"


	r5 = requests.get(catalog_URL + "web_service?Name=" + "ProductOutputWS")
	product_output = r5.json()
	product_output_port = product_output['URL']['port']
	url_product_output_WS = "http://" + str(IP) + ":" + str(product_output_port) + "/"


	for fridge in fridges["fridges"]:

		userID =  fridge["user"]
		fridgeID = fridge["ID"]
		clientID = "ProductsAdaptorlWS_" + userID + "_" + fridgeID


		MQTT_ProductsAdaptor = ProductsAdaptorMQTT(clientID , userID , fridgeID , broker_IP , broker_port, catalog_Port , url_barcode_WS , url_product_input_WS , url_product_output_WS)
		MQTT_ProductsAdaptor.start()


		ProductsAdaptor_Thread = ProductsAdaptorThread(MQTT_ProductsAdaptor)
		ProductsAdaptor_Thread.start()


	cherrypy.tree.mount(ProductsAdaptorREST(catalog_URL), '/', conf)
	cherrypy.config.update({'server.socket_host': '0.0.0.0'})
	cherrypy.config.update({'server.socket_port': devPort})
	cherrypy.engine.start()
	cherrypy.engine.block()


