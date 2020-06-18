import cherrypy
import json
import os, os.path
import socket
import threading
import requests
import time

class FreeBoard:

	exposed = True

	def GET(self, *uri, **params):

		userID = params["userID"]
		fridgeID = params["fridgeID"]
		index = "index_"+userID+"_"+fridgeID+".html"
		index_file = open(index)
		return index_file.read()

	def POST(self, *uri, **params):
		json_string = params['json_string']
		file = open("dashboard/dashboard.json", 'w+')
		file.write(json_string)

class RegistrationThread(threading.Thread):
		
	def __init__(self, catalogIP, catalogPort, devIP, devPort):
		threading.Thread.__init__(self)
	
	def run(self):
		url = "http://"+ catalogIP + ":"+ catalogPort + "/"
		while True:

			dictWS = {"name": ("FreeBoardWS"),
								"IP": devIP,
								"port": devPort}
			jsonWS = json.dumps(dictWS)
			r = requests.post(url+"add_WS", data=jsonWS)
			
			print("FreeBoardWS registered.")

			time.sleep(60)



if __name__ == '__main__':
	conf = {
		'/': {
		'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
		'tools.sessions.on': True,
		'tools.staticdir.root': os.path.abspath(os.getcwd())
	},
	'/static': {
		'tools.staticdir.on': True,
		'tools.staticdir.dir': '.'
	},
	'/img': {
		'tools.staticdir.on': True,
		'tools.staticdir.dir': './img'
	},
	'/plugins': {
		'tools.staticdir.on': True,
		'tools.staticdir.dir': './plugins'
	},
	'/css': {
		'tools.staticdir.on': True,
		'tools.staticdir.dir': './css'
	},
	'/js': {
		'tools.staticdir.on': True,
		'tools.staticdir.dir': './js'
	}
	}
	print(os.getcwd())

	# get IP address
	s = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
	s.connect(("8.8.8.8", 80))
	devIP = s.getsockname()[0]
	devPort = 8081

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

	# register web service on the Catalog
	regThread = RegistrationThread(catalogIP, catalogPort, devIP, devPort)
	regThread.start()


	cherrypy.tree.mount (FreeBoard(), '/', conf)
	cherrypy.config.update({'server.socket_host': '0.0.0.0'})
	cherrypy.config.update({'server.socket_port': 8081})
	cherrypy.engine.start()
	cherrypy.engine.block()
