import cherrypy
import socket
import threading
import json
import requests
import time
import sys

class ProductOutputREST(object):

	# expose the Web Services
	exposed = True

	def __init__(self , bot_Token , catalog_URL):
		self.bot_Token = bot_Token
		self.catalog_URL = catalog_URL

	def GET (self, *uri, **params):
		if (len(uri)!=1):
			raise cherrypy.HTTPError(404, "Error: wrong number of uri")
		# /remove_product?product_name=<name>&brands=<brand>
		elif (uri[0] == "delete_product"):
			product_name = params["product_name"]
			brand = params["brands"]

		if (len(uri)!=1):
			raise cherrypy.HTTPError(404, "Error: wrong number of uri")
		# /delete_product?userID=<IDuser>&product_name=<name>&brands=<brand>
		elif (uri[0] == "delete_product"):
			userID = params["userID"]
			product_ID = params["product_name"]
			brand = params["brands"]

			print("wasted ricevuto")

			r = requests.get(self.catalog_URL + 'user?ID=' + str(userID))
								  
			r.raise_for_status()
			detail_user = r.json()
			user = json.loads(detail_user['user'])
			ID_bot = user['ID_bot']

			print ("get al telegram bot")
			# richiesta BOT

			r2 = requests.get('https://api.telegram.org/bot' + self.bot_Token + '/sendMessage?chat_id=' + str(ID_bot) +
										  '&text=' + 'The product ' + str(self.product_ID) + ' has been removed. Please write /delete_product and specify if it is wasted or not.')


		# # richiedere exp_date mediante BOT
		# mystring = "nome prodotto = " + product_name + "	brand = " + brand
		# return mystring

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
				dictWS = {"name": ("ProductOutputWS"),
									"IP": devIP,
									"port": devPort}
				jsonWS = json.dumps(dictWS)
				r = requests.post(url+"add_WS", data=jsonWS)

				print("ProductOutputWS registered.")

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
	devPort = 8691 #inserire numero porta per prod Output ws

	try:
		configFile = open("configProdInput.txt", "r")
		configJson = configFile.read()
		configDict = json.loads(configJson)
		configFile.close()
	except OSError:
		sys.exit("ERROR: cannot open the configuration file.")

	catalogIP = configDict["catalogIP"]
	catalogPort = configDict["catalogPort"]
	catalog_URL = "http://" + catalogIP + catalogPort

	print("Catalog IP is: " + catalogIP)
	print("Catalog port is " + catalogPort)

	file2 = open("botconfig.txt", "r")
	info2 = json.loads(file2.read())
	bot_Token = info2["token"]
	file2.close()

	# register ProductOutputREST as a web service
	regThread = RegistrationThread(catalogIP, catalogPort, devIP, devPort)
	regThread.start()


	# deploy the BarcodeConversionREST class and start the web server
	cherrypy.tree.mount(ProductOutputREST(bot_Token,catalog_URL), '/', conf)
	cherrypy.config.update({'server.socket_host': '0.0.0.0'})
	cherrypy.config.update({'server.socket_port': devPort})
	cherrypy.engine.start()
	cherrypy.engine.block()