import cherrypy
import json
import os, os.path


class FreeBoard:

	exposed = True

	def GET(self, *uri, **params):
		if (len(uri) == 2):
			index = "index_"+str(uri[0])+"_"+str(uri[1])+".html"
			index_file = open(index)
			return index_file.read()
		else:
			raise cherrypyHTTPError(404, "Error, you must specify user_ID and fridge_ID in the GET request")

	def POST(self, *uri, **params):
		json_string = params['json_string']
		file = open("dashboard/dashboard.json", 'w')
		file.write(json_string)

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
cherrypy.tree.mount (FreeBoard(), '/', conf)
cherrypy.config.update({'server.socket_host': '0.0.0.0'})
cherrypy.config.update({'server.socket_port': 8081})
cherrypy.engine.start()
cherrypy.engine.block()
