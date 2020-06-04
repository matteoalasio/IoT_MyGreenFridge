import cherrypy
import json
import time
import requests
from Catalog import *

"""
GET:
- /broker/ : Provide information about the broker IP address and port
- /users/ : Provide information about the available users
- /user?ID=<id> : Provide information about a user with a specific ID
- /fridges/ : Provide information about all the available fridges
- /fridge?ID=<id> : Provide information about a fridge with a specific fridge_ID
- /products?Fridge_ID=<IDFridge> : Provide information about the available products in a fridge
- /web_service?Name=<NameWS> : Provide the IP and the port of a specified WS
- /wasted?Fridge_ID=<IDFridge> : Provide information about the wasted products of a fridge
- /expiration_date?Fridge_ID=<IDFridge>&Product_ID=<IDProduct> : Provide information about the expiration date
                                                                of a specified product
- /association?Fridge_ID=<IDFridge>&User_ID=<IDUser> : Association between a user and a fridge
- /user_fridge?User_ID=<IDUser> : Given a user, it returns his fridge
- /alarm_status?Fridge_ID=<IDFridge>&Alarm=<Status> :  Given a fridge, it updates the status of its alarm related to temperature
"""

"""
POST:
- /add_fridge/ : Registration of a new fridge
    he body required is : {"ID":"", "user":"", "API":""}
- /add_user/ : Registration of a new user
    The body required is {"ID":"", "password":""}
- /add_sensor?Fridge_ID=<IDFridge> : Add a sensor to the correspondant Fridge
    The body required is {"sensor_ID":"", "Value":""}
- /add_product?Fridge_ID=<IDFridge> : Add a product to the correspondant Fridge
    The body required is {"product_ID":"", "brand":""}
- /add_expiration?Fridge_ID=<IDFridge>&Product_ID=<IDProduct> : Add the expiration date of a specified product
    The body required is {"day":"", "month":"", "year":""}
- /add_wasted?Fridge_ID=<IDFridge> : Add a wasted product to a specified fridge
    The body required is {"product_ID":""}
- /add_WS :Add a Web Service to the catalog structure
    #The body required is {"name":"", "IP":"", "port":""}
"""

"""
PUT:
- /update_user/ : Update a specified user adding the nickname
    The body required is {"ID":"", "nickname":"", "ID_bot":""}
- /update_fridge/ : Update a specified fridge
     The body required is : {"ID":"", "user":"", "sensors":[], "products":[], "wasted": [], "insert-timestamp": "", "IP": "", "port": ""}
- /update_sensor?Fridge_ID=<IDFridge> : Update a sensor given the correspondant fridge
    The body required is {"sensor_ID":"", "Value":""}
- /update_password?User_ID=<IDUser> : Update the password of the specified user
    The body required is {"password":"", "new_password":""}
"""

"""
DELETE:
- /fridge?ID=<id> : Delete a specified fridge
- /user?ID=<id> : Delete a specified user
- /sensor/fridge_ID?Sensor_ID=<IDSensor> : Delete a specified sensor.
                                        Replace "fridge_ID" in the uri with the ID of the fridge where the sensor is present

- /product/Fridge_ID?Prod_ID=<IDProd> : Delete a product for a specified fridge.
                                        Replace "fridge_ID" in the uri with the ID of the fridge where the product is present
"""



class Catalog_REST:
    exposed = True

    def __init__(self):
        self.catalog = Catalog("test_file_2.json")



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

        #/products?Fridge_ID=<IDFridge>
        # Information about the available products in a fridge
        elif uri[0] == 'products':
            fridge_ID = params['Fridge_ID']
            info = json.dumps(
                {'Products': self.catalog.get_products(fridge_ID)})
            return info

        #/wasted?Fridge_ID=<IDFridge>
        # Information about the wasted products of a fridge
        elif uri[0] == 'wasted':
            fridge_ID = params['Fridge_ID']
            info = json.dumps(
                {'Wasted_products': self.catalog.get_wasted(fridge_ID)})
            return info

        #/web_service?Name=<NameWS>
        # Information about the wasted products of a fridge
        elif uri[0] == 'web_service':
            name = params['Name']
            info = json.dumps({"URL" : self.catalog.get_ws(name)})
            if info == "Web Service not found!":
                raise cherrypy.HTTPError(404, info)
            return info

        #/expiration_date?Fridge_ID=<IDFridge>&Product_ID=<IDProduct>
        # Information about the expiration date of a specified product
        elif uri[0] == 'expiration_date':
            product_ID = params['Product_ID']
            fridge_ID = params['Fridge_ID']
            info = self.catalog.get_expiration(fridge_ID, product_ID)
            info_2 = json.dumps(
                {'expiration_date': self.catalog.get_expiration(fridge_ID, product_ID)})
            if info == "Product not found!":
                raise cherrypy.HTTPError(404, info)
            if info == "Fridge not found!":
                raise cherrypy.HTTPError(404, info)
            return info_2

        # /association?Fridge_ID=<IDFridge>&User_ID=<IDUser>
        # Association between a user and a fridge
        elif uri[0] == 'association':
            user_ID = params['User_ID']
            fridge_ID = params['Fridge_ID']

            info_association = self.catalog.associate_user_fridge(
                user_ID, fridge_ID)

            if info_association == "User not found!":
                raise cherrypy.HTTPError(404, info_association)
            if info_association == "Fridge not found!":
                raise cherrypy.HTTPError(404, info_association)

            return info_association

        # /user_fridge?User_ID=<IDUser>
        # Given a user, it returns his fridge
        elif uri[0] == 'user_fridge':
            user_ID = params['User_ID']
            info = self.catalog.get_user_fridge(user_ID)
            if info == "User not found!":
                raise cherrypy.HTTPError(404, info)
            return info

        # /alarm_status?Fridge_ID=<IDFridge>&Alarm=<Status>
        # Given a fridge, it updates the status of its alarm related to temperature
        elif uri[0] == 'alarm_status':
            fridge_ID = params['Fridge_ID']
            alarm = params['Alarm']
            info = self.catalog.update_alarm_status(fridge_ID, alarm)
            if info == "Fridge not found!":
                raise cherrypy.HTTPError(404, info)
            return info


        else:
            raise cherrypy.HTTPError(
                400, "Your GET request has URI not correct")


########################################## POST FUNCTION ############################################

    def POST(self, *uri, **params):

        if len(uri) == 0:
            raise cherrypy.HTTPError(400)

        json_body = cherrypy.request.body.read()
        body = json.loads(json_body)

        #/add_fridge/
        # Registration of a new fridge
        # The body required is : {"ID":"", "user":"", "API":""}
        if uri[0] == 'add_fridge':
            info_added = self.catalog.add_fridge(body)
            return info_added

        #/add_user/
        # Registration of a new user
        # The body required is {"ID":"", "password":"", "nickname": "", "ID_bot":""}
        elif uri[0] == 'add_user':
            info_added = self.catalog.add_user(body)
            if info_added == "User already present":
                raise cherrypy.HTTPError(404, info_added)
            return info_added


        #/add_sensor?Fridge_ID=<IDFridge>
        # Add a sensor to the correspondant Fridge
        # The body required is {"sensor_ID":"", "Value":""}
        elif uri[0] == 'add_sensor':
            fridge_ID = params['Fridge_ID']
            info_added = self.catalog.add_sensor(fridge_ID, body)
            if info_added == "Fridge not found!":
                raise cherrypy.HTTPError(404, info_added)
            return info_added


        #/add_product?Fridge_ID=<IDFridge>
        # Add a product to the correspondant Fridge
        # The body required is {"product_ID":"", "brand":""}
        elif uri[0] == 'add_product':
            fridge_ID = params['Fridge_ID']
            info_added = self.catalog.add_product(fridge_ID, body)
            if info_added == "Fridge not found!":
                raise cherrypy.HTTPError(404, info_added)
            return info_added

        #/add_expiration?Fridge_ID=<IDFridge>&Product_ID=<IDProduct>
        # Add the expiration date of a specified product
        # The body of the request has to be {"day":"", "month":"", "year":""}
        if uri[0] == 'add_expiration':
            product_ID = params['Product_ID']
            fridge_ID = params['Fridge_ID']
            info_added = self.catalog.add_expiration(
                fridge_ID, product_ID, body)
            if info_added == "Fridge not found!":
                raise cherrypy.HTTPError(404, info_added)
            if info_added == "Product not found!":
                raise cherrypy.HTTPError(404, info_added)
            return info_added

        #/add_wasted?Fridge_ID=<IDFridge>
        # Add a wasted product to a specified fridge
        # The body of the request has to be {"product_ID":""}
        if uri[0] == 'add_wasted':
            fridge_ID = params['Fridge_ID']
            info_added = self.catalog.add_wasted(fridge_ID, body)
            if info_added == "Fridge not found!":
                raise cherrypy.HTTPError(404, info_added)
            if info_added == "Product was not present in the fridge!":
                raise cherrypy.HTTPError(404, info_added)
            return info_added


        #/add_WS
        #Add a Web Service to the catalog structure
        #The body required is {"name":"", "IP":"", "port":""}
        if uri[0] == 'add_WS':
            info_added = self.catalog.add_WS(body)
            return info_added

        else:
            raise cherrypy.HTTPError(
                400, "Your POST request has URI not correct")

########################################## PUT FUNCTION ############################################


    def PUT(self, *uri, **params):
        if len(uri) == 0:
            raise cherrypy.HTTPError(400)

        json_body = cherrypy.request.body.read()
        body = json.loads(json_body)

        #/update_user/
        # Update a specified user adding the nickname
        # The body required is {"ID":"", "nickname":"", "ID_bot":""}
        if uri[0] == 'update_user':
            info_updated = self.catalog.update_user(body)
            if info_updated == "User not found!":
                raise cherrypy.HTTPError(404, info_updated)
            return info_updated


        #/update_fridge/
        # Update a specified fridge
        # The body required is : {"ID":"", "sensors":[], "IP": "", "port": ""}
        elif uri[0] == 'update_fridge':
            info_updated = self.catalog.update_fridge(body)
            if info_updated == "Fridge not found!":
                raise cherrypy.HTTPError(404, info_updated)
            return info_updated


        #/update_sensor?Fridge_ID=<IDFridge>
        # Update a sensor given the correspondant fridge
        # The body required is {"sensor_ID":"", "Value":""}
        elif uri[0] == 'update_sensor':
            fridge_ID = params['Fridge_ID']
            info_updated = self.catalog.update_sensor(fridge_ID, body)
            if info_updated == "Fridge not found!":
                raise cherrypy.HTTPError(404, info_updated)
            return info_updated

        #/update_password?User_ID=<IDUser>
        # Update the password of the specified user
        # The body required is {"password":"", "new_password":""}
        elif uri[0] == 'update_password':
            user_ID = params['User_ID']
            info_updated = self.catalog.update_pw(user_ID, body)
            if info_updated == "Password is not correct!":
                raise cherrypy.HTTPError(401, info_updated)
            if info_updated == "User not found!":
                raise cherrypy.HTTPError(404, info_updated)
            return info_updated

        else:
            raise cherrypy.HTTPError(
                400, "Your PUT request has URI not correct")


########################################## DELETE FUNCTION ############################################

    def DELETE(self, *uri, **params):

        #/fridge?ID=<id>
        # Delete a specified fridge
        if uri[0] == 'fridge':
            ID = params['ID']
            info_updated = self.catalog.delete_fridge(ID)
            if info_updated == "Fridge not found!":
                raise cherrypy.HTTPError(404, info_updated)
            return info_updated

        #/user?ID=<id>
        # Delete a specified user
        elif uri[0] == 'user':
            ID = params['ID']
            info_updated = self.catalog.delete_user(ID)
            if info_updated == "User not found!":
                raise cherrypy.HTTPError(404, info_updated)
            return info_updated

        #/sensor/fridge_ID?Sensor_ID=<IDSensor>
        # Delete a specified sensor
        elif uri[0] == 'sensor':
            fridge_ID = (uri[1])
            sensor_ID = params['Sensor_ID']
            info_updated = self.catalog.delete_sensor(fridge_ID, sensor_ID)
            if info_updated == "Sensor is not present in the fridge!":
                raise cherrypy.HTTPError(404, info_updated)
            if info_updated == "Fridge not found!":
                raise cherrypy.HTTPError(404, info_updated)
            return info_updated

        #/product?Fridge_ID=<Fridge_ID>&Prod_ID=<IDProd>
        # Delete a product for a specified fridge
        if uri[0] == 'product':
            product_ID = params['Prod_ID']
            fridge_ID = (params['Fridge_ID'])
            info_updated = self.catalog.delete_product(fridge_ID, product_ID)
            if info_updated == "Product not found!":
                raise cherrypy.HTTPError(404, info_updated)
            if info_updated == "Fridge not found!":
                raise cherrypy.HTTPError(404, info_updated)
            return info_updated

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
#cherrypy.config.update({'server.socket_host': '127.0.0.1'})
cherrypy.config.update({'server.socket_host': '0.0.0.0'})
cherrypy.config.update({'server.socket_port': 8080})
cherrypy.engine.start()
cherrypy.engine.block()
