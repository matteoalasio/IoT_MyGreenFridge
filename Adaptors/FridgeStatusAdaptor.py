# from DeviceConnector import *
from FridgeStatusControl import *
import cherrypy
import json
import socket
import paho.mqtt.client as PahoMQTT
import threading
import requests
import time
import sys
import numpy as np


class FridgeREST():

    exposed = True

    def __init__(self, controller):
        self.controller = controller

    def GET(self, *uri, **params):

        #/status?User_ID=<IDUser>&Fridge_ID=<IDFridge>
        if (uri[0] == "status"):
            user_ID = params['User_ID']
            fridge_ID = params['Fridge_ID']
            info = json.dumps({"Current status": self.controller.get_status_fridge(user_ID, fridge_ID)})
            return info

        else:
            raise cherrypy.HTTPError(400, "Your GET request has URI not correct")


class FridgeStatusMQTT:

    def __init__(self, client_ID, user_ID, fridge_ID, broker_ip, broker_port, control):

        self.client_ID = client_ID
        self.user_ID = user_ID
        self.fridge_ID = fridge_ID
        self.broker = broker_ip
        self.port = broker_port
        self.control = control

        # create an instance of paho.mqtt.client
        self._paho_mqtt = PahoMQTT.Client(self.client_ID)

        # register the callback
        self._paho_mqtt.on_connect = self.myOnConnect
        self._paho_mqtt.on_message = self.myOnMessage

    def myOnConnect(self, paho_mqtt, userdata, flags, rc):
        print ("Connected to broker: " + str(self.broker) +
               ", with result code: " + str(rc))

    def myOnMessage(self, paho_mqtt, userdata, msg):
        # A new message is received
        # self.notifier.notify (msg.topic, msg.payload)
        print("Message received: " + str(msg.payload.decode("utf-8")))
        print("On topic: ", str(msg.topic))
        message = msg.payload.decode("utf-8")
        msg = json.loads(message)

        control_status = self.control.update_status(
            self.user_ID, self.fridge_ID, msg['v'])


    def myPublish(self, topic, msg):
        # if needed, you can do some computation or error-check before publishing
        print ("Publishing message: " + str(msg))
        print("with topic: " + str(topic))
        # publish a message with a certain topic
        self._paho_mqtt.publish(topic, msg, 2)

    def mySubscribe(self, topic):
        # if needed, you can do some computation or error-check before subscribing
        print ("Subscribing to topic: " + str(topic))
        # subscribe for a topic
        self._paho_mqtt.subscribe(topic, 2)

        # just to remember that it works also as a subscriber
        self._isSubscriber = True
        self._topic = topic

    def start(self):
        # manage connection to broker
        self._paho_mqtt.connect(self.broker, self.port)
        self._paho_mqtt.loop_start()

    def stop(self):
        if (self._isSubscriber):
            # remember to unsuscribe if it is working also as subscriber
            self._paho_mqtt.unsubscribe(self._topic)

        self._paho_mqtt.loop_stop()
        self._paho_mqtt.disconnect()


class FridgeStatusThread(threading.Thread):

    def __init__(self, FridgeStatus_MQTT, userID, fridgeID, catalog_URL, control):
        threading.Thread.__init__(self)
        self.FridgeStatus_MQTT = FridgeStatus_MQTT
        self.user_ID = userID
        self.fridge_ID = fridgeID
        self.catalog_url = catalog_URL
        self.control = control

    def run(self):
        while True:

            topic = "/MyGreenFridge/" + \
                str(self.user_ID) + '/' + self.fridge_ID + "/Tcontrol"
            self.FridgeStatus_MQTT.mySubscribe(topic)

            time.sleep(15)

class RegistrationThread(threading.Thread):

        def __init__(self, catalogIP, catalogPort, WS_IP, WS_Port):
            threading.Thread.__init__(self)
            self.catalogIP = catalogIP
            self.catalogPort = catalogPort
            self.WS_IP = WS_IP
            self.WS_Port = WS_Port

        def run(self):
            url = "http://"+ self.catalogIP + ":"+ self.catalogPort + "/"
            while True:

                ### register ProductsControlWS as a web service
                web_service = json.dumps({"name": "FridgeStatusAdaptorWS", "IP": self.WS_IP, "port": self.WS_Port})
                r1 = requests.post(catalog_URL + "add_WS", web_service)

                print("FridgeStatusAdaptorWS registered.")

                time.sleep(60)


class ControlThread(threading.Thread):

        def __init__(self, catalogIP, catalogPort, initFridges, brokerIP, brokerPort):

            threading.Thread.__init__(self)

            self.catalogIP = catalogIP
            self.catalogPort = catalogPort
            self.initFridges = initFridges
            self.broker_IP = brokerIP
            self.broker_port = brokerPort


        def run(self):


            catalog_URL = "http://" + self.catalogIP + ":" + self.catalogPort + '/'
            oldFridges = self.initFridges

            while True:

                # retrieve all the fridges from the Catalog
                r = requests.get(catalog_URL + "fridges")
                i=0

                FridgeStatus_Controller = FridgeStatusControl(3, 3)

                dictCurrFridges = r.json() # fridges is a Python dictionary
                currFridges = []
                for fridge in dictCurrFridges["fridges"]:
                    currFridges.append(fridge["ID"])


                # get new fridges that have been added
                diffFridges = list(set(currFridges) - set(oldFridges))

                #listThreads = threading.enumerate()
                #print(listThreads)

                for fridge_ID in diffFridges:

                    for fridge in dictCurrFridges["fridges"]:

                        if fridge_ID == fridge["ID"]:

                            user_ID =  fridge["user"]
                            client_ID = "fridgestatusclient_" + str(i)

                            i=i+1

                            FridgeStatus_MQTT = FridgeStatusMQTT(client_ID, user_ID, fridge_ID, self.broker_IP, self.broker_port, FridgeStatus_Controller)

                            FridgeStatus_MQTT.start()

                            FridgeStatus_Thread = FridgeStatusThread(FridgeStatus_MQTT, user_ID, fridge_ID, catalog_URL, FridgeStatus_Controller)
                            FridgeStatus_Thread.start()



                time.sleep(60*60)
                oldFridges = currFridges.copy()


if __name__ == '__main__':

    # standard configuration to serve the url "localhost:8080"
    conf = {
        '/': {
            'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
            'tools.sessions.on': True
        }
    }

    # get IP address of the RPI
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    ip = s.getsockname()[0]
    port = 8585


    file = open("../configSystem.json","r")
    info = json.loads(file.read())

    catalog_IP = info["catalogIP"]
    catalog_Port = info["catalogPort"]

    file.close()
    catalog_URL = "http://" + catalog_IP + ":" + catalog_Port + "/"

    regThread = RegistrationThread(catalog_IP, catalog_Port, ip, port)
    regThread.start()

    try:
        r = requests.get(catalog_URL + "broker")
        broker = r.json()
        broker_IP = broker["broker_IP"]
        broker_Port = broker["broker_port"]
    except requests.RequestException as err:
        sys.exit("ERROR: cannot retrieve the Broker IP from the Catalog.")

    r2 = requests.get(catalog_URL + "fridges")
    fridges = r2.json()

    FridgeStatus_Controller = FridgeStatusControl(3, 3)

    # It iterates on all the available fridges in the system
    i = 0
    for fridge in fridges["fridges"]:
        user_ID = fridge['user']
        fridge_ID = fridge['ID']
        client_ID = "fridgestatusclient_" + str(i)
        i = i + 1

        FridgeStatus_MQTT = FridgeStatusMQTT(
            client_ID, user_ID, fridge_ID, broker_IP, broker_Port, FridgeStatus_Controller)

        FridgeStatus_MQTT.start()

        FridgeStatus_Thread = FridgeStatusThread(FridgeStatus_MQTT, user_ID, fridge_ID, catalog_URL, FridgeStatus_Controller)
        FridgeStatus_Thread.start()

    cherrypy.tree.mount(FridgeREST(FridgeStatus_Controller), '/', conf)
    cherrypy.config.update({'server.socket_host': '0.0.0.0'})
    cherrypy.config.update({'server.socket_port': port})
    cherrypy.engine.start()
    cherrypy.engine.block()
