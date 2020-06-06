import cherrypy
import socket
import threading
import json
import requests
import time
import sys

class ProductInputREST(object):

	# expose the Web Services
	exposed = True

	def __init__(self , bot_Token , catalog_URL):
		self.bot_Token = bot_Token
		self.catalog_URL = catalog_URL


	def GET (self, *uri, **params):
		if (len(uri) != 1):
			raise cherrypy.HTTPError(404, "Error: wrong number of uri")
		# /insert_product?userID=<IDuser>&Fridge_ID=<FridgeID>&product_name=<name>&brands=<brand>
		elif (uri[0] == "insert_product"):
			Fridge_ID = params["FridgeID"]
			userID = params["userID"]
			product_ID = params["product_name"]
			brand = params["brands"]

		
			r = requests.get(self.catalog_URL + 'user?ID=' + str(userID))


			r.raise_for_status()
			detail_user = r.json()
			user = json.loads(detail_user['user'])
			ID_bot = user['ID_bot']
			print(ID_bot)
			print(userID)

			print ("prodotto da inserire ricevuto")
			# richiesta BOT

			r2 = requests.get('https://api.telegram.org/bot' + self.bot_Token + '/sendMessage?chat_id=' + str(ID_bot) +
										  '&text=' + 'The product ' + str(product_ID) + ' has been added in the fridge ' + str(Fridge_ID) + 
										  ' Please write /add_product and insert its expiration date.')



		# richiedere exp_date mediante BOT
		# mystring = "nome prodotto = " + product_ID + "	brand = " + brand


	def POST (self, *uri, **params):

		pass
		return

	def PUT (self, *uri, **params):
		pass
		return

	def DELETE(self):
		pass
		return

class RegistrationThread(threading.Thread):

		def __init__(self, catalogIP, catalogPort, devIP, devPort):
			threading.Thread.__init__(self)

		def run(self):
			url = "http://"+ catalogIP + ":"+ catalogPort + "/"
			while True:

				### register BarcodeConversionREST as a web service
				dictWS = {"name": ("ProductInputWS"),
									"IP": devIP,
									"port": devPort}
				jsonWS = json.dumps(dictWS)
				r = requests.post(url+"add_WS", data=jsonWS)

				print("ProductInputWS registered.")

				time.sleep(60*60)



if __name__ == '__main__':


	# standard configuration
	conf = {
		'/': {
			'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
			'tools.sessions.on': True
		}
	}

	# get IP address of ProductInputWS
	s = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
	s.connect(("8.8.8.8", 80))
	devIP = s.getsockname()[0]
	devPort = 8690 #inserire numero porta per prod input ws

	try:
		configFile = open("../configSystem.json", "r")
		configJson = configFile.read()
		configDict = json.loads(configJson)
		configFile.close()
	except OSError:
		sys.exit("ERROR: cannot open the configuration file.")

	catalogIP = configDict["catalogIP"]
	catalogPort = configDict["catalogPort"]
	catalog_URL = "http://" + catalogIP + ":" + catalogPort + "/"

	print("Catalog IP is: " + catalogIP)
	print("Catalog port is " + catalogPort)

	file2 = open("botconfig.txt", "r")
	info2 = json.loads(file2.read())
	bot_Token = info2["token"]
	file2.close()

	# register ProductInputREST as a web service
	regThread = RegistrationThread(catalogIP, catalogPort, devIP, devPort)
	regThread.start()


	# deploy the BarcodeConversionREST class and start the web server
	cherrypy.tree.mount(ProductInputREST(bot_Token,catalog_URL), '/', conf)
	cherrypy.config.update({'server.socket_host': '0.0.0.0'})
	cherrypy.config.update({'server.socket_port': devPort})
	cherrypy.engine.start()
	cherrypy.engine.block()