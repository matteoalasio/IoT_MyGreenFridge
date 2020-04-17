import json
import paho.mqtt.client as PahoMQTT
import datetime
import time
import requests
import sys
import urllib.request
import cherrypy
import threading

class ThingSpeakDataManager:

    def __init__(self, client_ID, user_ID, fridge_ID, broker_ip, broker_port):
        self.user_ID = user_ID
        self.client_ID = client_ID
        self.fridge_ID = fridge_ID
        self.broker = broker_ip
        self.port = broker_port

        self._paho_mqtt = PahoMQTT.Client(self.client_ID)
        self._paho_mqtt.on_connect = self.myOnConnect
        self._paho_mqtt.on_message = self.myOnMessageReceived

        self.value_t = None
        self.value_h = None

    def myOnConnect(self, paho_mqtt, userdata, flags, rc):
        print("Connected to %s with result code: %d" %(self.broker, rc))

    def start(self):
        self._paho_mqtt.connect(self.broker, self.port)
        self._paho_mqtt.loop_start()

    def stop (self):

        if self._isSubscriber :
            self._paho_mqtt.unsubscribe(self.topic)

        self._paho_mqtt.loop_stop()
        self._paho_mqtt.disconnect()
    
    def mySubscribe(self, topic):
        #print("Subscribing to %s" %(topic))
        self._paho_mqtt.subscribe(topic, 2)

    def myOnMessageReceived (self, paho_mqtt, userdata, msg):
        
        message_received = json.loads(msg.payload.decode("utf-8"))
        message = int(((message_received["e"])[0])["v"])
        print("A message has been received.")
        if (msg.topic == "MyGreenFridge/"+str(self.user_ID)+"/"+str(self.fridge_ID)+"/temperature"):
            self.value_t = message
        elif(msg.topic == "MyGreenFridge/"+str(self.user_ID)+"/"+str(self.fridge_ID)+"/humidity"):
            self.value_h = message

    #def update_temperature(temperature):
    #    try:
    #        print("I AM HERE: 1")
    #        data = urllib.request.urlopen("https://api.thingspeak.com/update?api_key="+self.fridgeAPI+"&field1="+str(temperature))
    #        print("Temperature value updated on ThingSpeak: "+str(temperature))
    #    except:
    #        print("An exception occurred")

    #def update_humidity(humidity):
    #    print("I AM HERE: 2")
    #    data = urllib.request.urlopen("https://api.thingspeak.com/update?api_key="+self.fridgeAPI+"&field2="+str(humidity))
    #    print("Humidity value updated on ThingSpeak: "+str(humidity))
        #self.tsdm.value_h = None

class TemperatureThread(threading.Thread):
    def __init__(self, tsdm, userID, fridgeID, fridgeAPI, catalog_URL):
        threading.Thread.__init__(self)
        self.tsdm = tsdm
        self.userID = userID
        self.fridgeID = fridgeID
        self.fridgeAPI = fridgeAPI
        self.catalog_url = catalog_URL

    def run(self):
        while True:

            topic_t = "MyGreenFridge/"+str(self.userID)+"/"+str(self.fridgeID)+"/temperature"
            self.tsdm.mySubscribe(topic_t)
            if (self.tsdm.value_t):
                data_t = urllib.request.urlopen("https://api.thingspeak.com/update?api_key="+self.fridgeAPI+"&field1="+str(self.tsdm.value_t))
                print("Temperature value updated on ThingSpeak: "+str(self.tsdm.value_t))
                self.tsdm.value_t = None

            time.sleep(13)

class HumidityThread(threading.Thread):
    def __init__(self, tsdm, userID, fridgeID, fridgeAPI, catalog_URL):
        threading.Thread.__init__(self)
        self.tsdm = tsdm
        self.userID = userID
        self.fridgeID = fridgeID
        self.fridgeAPI = fridgeAPI
        self.catalog_URL = catalog_URL
    
    def run(self):
        while True:
            topic_h = "MyGreenFridge/"+str(self.userID)+"/"+str(self.fridgeID)+"/humidity"
            self.tsdm.mySubscribe(topic_h)
            if (self.tsdm.value_h):
                data_h = urllib.request.urlopen("https://api.thingspeak.com/update?api_key="+self.fridgeAPI+"&field2="+str(self.tsdm.value_h))
                print("Humidity value updated on ThingSpeak: "+str(self.tsdm.value_h))
                self.tsdm.value_h = None

            time.sleep(11)


if __name__ == "__main__":

    conf = {
        '/': {
            'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
            'tools.sessions.on': True
        }
    }

    try:
        configFile = open("configThingSpeak.txt", "r")
        configJson = configFile.read()
        configDict = json.loads(configJson)
        configFile.close()
    except OSError:
        sys.exit("ERROR: cannot open the configuration file.")

    userID = configDict['userID']
    fridges = []
    fridges = configDict['fridges']
    catalogIP = configDict['catalogIP']
    catalogPort = configDict['catalogPort']

    print("Catalog IP is: " + catalogIP)
    print("Catalog port is " + catalogPort)

    # retrieve the broker IP and the broker port from the Catalog
    catalogURL = "http://" + catalogIP + ":" + catalogPort
    try:
        r = requests.get(catalogURL + "/broker")
        broker = r.json()
        brokerIP = broker["broker_IP"]
        brokerPort = broker["broker_port"]
        print("Broker IP is: " + str(brokerIP))
        print("Broker port is: " + str(brokerPort))
    except requests.RequestException as err:
        sys.exit("ERROR: cannot retrieve the Broker IP from the Catalog.")

    print ("This is the list of fridges:")
    print (fridges)
    n_fridges = len(fridges)
    print ("It contains a number of fridges equal to: " + str(n_fridges))

    i=0
    for f in fridges:
        fridgeID = f["fridgeID"]
        fridgeAPI = f["API"]
        print(fridgeID)
        print(fridgeAPI)
        catalogURL = catalogURL+"/wasted?Fridge_ID="+fridgeID
        # Taking the wasted products here
        try:
            r2 = requests.get(catalogURL)
            wasted_json = r2.json()
            value = len(wasted_json["Wasted_products"])
            data = urllib.request.urlopen("https://api.thingspeak.com/update?api_key="+fridgeAPI+"&field3="+str(value))
            print ("Wasted products updated on ThingSpeak")
        except requests.RequestException as err:
            sys.exit("ERROR: did not find the list of wasted products")

        client_ID = "client_"+str(i)
        i = i+1
        
        tsdm = ThingSpeakDataManager(client_ID, userID, fridgeID, brokerIP, brokerPort)
        tsdm.start()
        tempThread = TemperatureThread(tsdm, userID, fridgeID, fridgeAPI, catalogURL)
        tempThread.start()
        humThread = HumidityThread(tsdm, userID, fridgeID, fridgeAPI, catalogURL)
        humThread.start()
