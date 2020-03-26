import cherrypy
import json
import time
import requests
from Catalog import *


class Catalog_REST:
    exposed = True

    def __init__(self):
        self.catalog = Catalog("Catalog_test.txt")


########################################## GET FUNCTION ############################################
    def GET(self, *uri, **params):
        if len(uri) == 0:
            raise cherrypy.HTTPError(400)

        #/broker/
        # Information about the broker IP address and port
        if uri[0] == 'broker':
            IP, Port = self.catalog.broker()
            info = json.dumps({'broker_IP': IP, 'broker_port': Port})
            return info

        #/users/
        # Information about the available users
        elif uri[0] == 'users':
            info = json.dumps({'users': self.catalog.get_users()})
            return info

        # /user?ID=<id>
        # Information about a user with a specific ID
        elif uri[0] == 'user':

            info_user = self.catalog.get_user(params['ID'])
            if info_user == "User not found!":
                raise cherrypy.HTTPError(404, info_user)
            else:
                info = json.dumps({'user': info_user})
                return info

        #/fridges/
        # Information about all the available fridges
        elif uri[0] == 'fridges':
            info = json.dumps({'fridges': self.catalog.get_fridges()})
            return info

        # /fridge?ID=<id>
        # Information about a fridge with a specific fridge_ID
        elif uri[0] == 'fridge':
            info_fridge = self.catalog.get_fridge(params['ID'])

            if info_fridge == "Fridge not found!":
                raise cherrypy.HTTPError(404, info_fridge)
            else:
                info = json.dumps({'fridge': info_fridge})
                return info

        # /association?Fridge_ID=<IDFridge>&User_ID=<IDUser>
        # Association between a user and a fridge
        elif uri[0] == 'association':
            user_ID = params['User_ID']
            fridge_ID = params['Fridge_ID']

            info_association = self.catalog.associate_user_fridge(user_ID, fridge_ID)

            if info_association == "User not found!":
                raise cherrypy.HTTPError(404, info_association)
            if info_association == "Fridge not found!":
                raise cherrypy.HTTPError(404, info_association)


########################################## POST FUNCTION ############################################

    def POST(self, *uri, **params):

        if len(uri) == 0:
            raise cherrypy.HTTPError(400)

        json_body = cherrypy.request.body.read()
        body = json.loads(json_body)

        #/add_fridge/
        # Registration of a new fridge
        if uri[0] == 'add_fridge':
            info_added = self.catalog.add_fridge(body)


        #/update_fridge/
        # Update a specified fridge
        elif uri[0] == 'update_fridge':
            info_updated = self.catalog.update_fridge(body)

        #/add_user/
        # Registration of a new user
        elif uri[0] == 'add_user':
            info_added = self.catalog.add_user(body)
            print info_added

        #/update_user/
        # Update a specified user
        elif uri[0] == 'update_user':
            info_updated = self.catalog.update_user(body)

        #/add_sensor?Fridge_ID=<IDFridge>
        # Add a sensor to the correspondant Fridge
        elif uri[0] == 'add_sensor':
            fridge_ID = params['Fridge_ID']
            info_updated = self.catalog.add_sensor(fridge_ID, body)

        else:
            raise cherrypy.HTTPError(400)

########################################## DELETE FUNCTION ############################################

    def DELETE(self, *uri, **params):
        ID = params['ID']

        #/fridge?ID=<id>
        # Delete a specified fridge
        if uri[0] == 'fridge':
            self.catalog.delete_fridge(ID)

        #/user?ID=<id>
        # Delete a specified user
        elif uri[0] == 'user':
            self.catalog.delete_user(ID)

        #/sensor?Fridge_ID=<IDFridge>
        # Delete a sensor for a specified fridge
        if uri[0] == 'sensor':
            fridge_ID = params['Fridge_ID']
            self.catalog.delete_sensor(fridge_ID)

        else:
            raise cherrypy.HTTPError(400)


########################################## MAIN FUNCTION ############################################

if __name__ == '__main__':
    conf = {
        '/': {
            'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
            'tools.sessions.on': True,
        }
    }

cherrypy.tree.mount(Catalog_REST(), '/', conf)
cherrypy.config.update({'server.socket_host': '127.0.0.1'})
cherrypy.config.update({'server.socket_port': 8080})
cherrypy.engine.start()
cherrypy.engine.block()
