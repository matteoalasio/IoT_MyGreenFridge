# ----------------------------------------------------------------------
# Author: Letizia Bergamasco
# 
# Description: Products Control is a control strategy that manages the
# 	images of the products inserted in the fridge. It works both as an
# 	MQTT subscriber, to receive the images from the first webcam, and as
# 	an MQTT publisher, to return the corresponding EAN codes to the
# 	Products Adaptor.
#   - MQTT subscriber on topics:
#       > MyGreenFridge/<userID>/<fridgeID>/camera0
#   - MQTT publisher on topics:
#       > MyGreenFridge/<userID>/<fridgeID>/EAN0
# ----------------------------------------------------------------------

from ProductsLib import *
import socket
import json
import requests
import sys


if __name__ == '__main__':
	
	# get IP address of the ProductsControlWS
	s = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
	s.connect(("8.8.8.8", 80))
	devIP = s.getsockname()[0]
	devPort = 8690

	# read configuration file
	try:
		configFile = open("../configSystem.json", "r")
		configJson = configFile.read()
		configDict = json.loads(configJson)
		configFile.close()
	except OSError:
		sys.exit("ERROR: cannot open the configuration file.")

	catalogIP = configDict["catalogIP"]
	catalogPort = configDict["catalogPort"]

	print("Catalog IP is: " + catalogIP)
	print("Catalog port is " + catalogPort)

	nameWS = "ProductsControlWS"
	sensorID = "camera0"
	topicEnd = "EAN0"

	mainFunct(catalogIP, catalogPort, devIP, devPort, nameWS, sensorID, topicEnd)







