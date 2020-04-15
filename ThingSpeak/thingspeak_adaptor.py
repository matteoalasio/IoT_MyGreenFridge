# The purpose of this script is to subscribe to topics,
# receiving data from the sensors in MQTT and then
# publishing them on ThingSpeak channels via HTTP request

## ---> check after if all these libraries are needed
#import thingspeak
import json
#import paho.mqtt.client as PahoMQTT
import datetime
import time
import requests
import sys
import urllib
import cherrypy

## ---> subscriber class, to manage the messages in MQTT
class ThingSpeakDataManager :

    def __init__(self, userID, broker, port, fridges):
        """
        This is the constructor function of the class.
        -----
        userID : identification of a device to which subscribing
              string
        broker : identifying the broker of the communication

        port : identifying the port in which the communication takes place

        """
        self.userID = userID
        self.broker = broker
        self.port = port
        self.topic = ""
        self._isSubscriber = False
        self._paho_mqtt = PahoMQTT.Client(userID, False)
        self._paho_mqtt.on_connect = self.myOnConnect
        self._paho_mqtt.on_message = self.myOnMessageReceived
        self.fridges = fridges

    def mySubscribe (self, topic):
        """
        This function allows the subscription to a specific topic,
        passed as parameters. It is a string.
        """
        # Maybe implement some error-check before subscribing ?
        print ("subscribing to %s" % (topic))
        self._isSubscriber = True
        self._paho_mqtt.subscribe(topic, 2)
        self._topic = topic

    def myOnConnect (self, paho_mqtt, userdata):
        """
        This manages the opening of a connection.
        -----
        paho_mqtt : ???????????????

        userdata : ???????????

        flags : ?????????

        rc : result code

        """
        print ("Connected to %s with result code: %d" % (self.broker, rc))

    def myOnMessageReceived (self, paho_mqtt , userdata, msg):
        # here I must still understand precisely which topics ThingSpeak wants
        """
        This function manages the recption of a message.
        -----
        paho_mqtt : ????
        userdata: ??????
        msg : message received
           JSON?
        """
        # print ("!")

        # capire bene cosa fare di TControl e di HControl
        # I am assuming the topic is correct. Maybe I should check this somewhere.

        for f in self.fridges:
            fridgeID = f["fridgeID"]
            fridgeAPI = f["API"]

            msg_dict = json.loads(msg.payload.decode('string-escape').strip('"'))
            value = ((msg_dict["e"])[0])["v"]

            if (msg.topic == '/MyGreenFridge/'+ self.userID + "/" + fridgeID + "/temperature"):
                # This is all temporary. I don't know what to put in these links
                # CANALI DIVERSI CON UN SOLO FIELD? O STESSO CANALE E VARI FIELD?
                data = urllib.urlopen("https://api.thingspeak.com/update?api_key="+fridgeAPI+"&field1="+str(value))
                print ("Temperature value updated on ThingSpeak")
                # Where do I take the value?
                print (value)

            elif(msg.topic == '/MyGreenFridge/'+ self.userID + "/" + self.fridgeID +"/humidity"):
                data = urllib.urlopen("https://api.thingspeak.com/update?api_key="+fridgeAPI+"&field2="+str(value))
                print ("Humidity value updated on ThingSpeak")
                print value

    def start(self):
		"""
        Manages the connection to the broker through a certain port.
        """
		self._paho_mqtt.connect(self.broker , self.port)
		self._paho_mqtt.loop_start()

    def stop (self):
        """
        Stops the connection to the broker.
        """
        if self._isSubscriber :
            self._paho_mqtt.unsubscribe(self.topic)

        self._paho_mqtt.loop_stop()
        self._paho_mqtt.disconnect()

if __name__ == "__main__":

    conf = {
        '/': {
            'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
            'tools.sessions.on': True
        }
    }

    # ???
    # s = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    # s.connect(("8.8.8.8", 80))
    # devIP = s.getsockname()[0]
    # devPort = 8082

    # read configuration file
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
            data = urllib.urlopen("https://api.thingspeak.com/update?api_key="+fridgeAPI+"&field3="+str(value))
            print ("Wasted products updated on ThingSpeak")
        except requests.RequestException as err:
            sys.exit("ERROR: did not find the list of wasted products")

    tsdm = ThingSpeakDataManager(deviceID, brokerip, brokerport, fridges)

    tsdm.start()
    time.sleep(2) # do I need this? Probably I will understand only when I run it...
    tsdm.mySubscribe('/MyGreenFridge/#')

    while True:
        time.sleep(1)
