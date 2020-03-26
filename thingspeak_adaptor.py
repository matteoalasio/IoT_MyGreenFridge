# The purpose of this script is to subscribe to topics, 
# receiving data from the sensors in MQTT and then 
# publishing them on ThingSpeak channels via HTTP request

## ---> check after if all these libraries are needed
#import thingspeak
#import threading
import json
import paho.mqtt.client as PahoMQTT
import datetime
import time
import requests
import sys
import urllib

## ---> subscriber class, to manage the messages in MQTT
class ThingSpeakDataManager :

    def __init__(self, userID, broker, port):
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
    
    def myOnConnect (self, paho_mqtt, userdata, flags, rc):
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

        msg_dict = json.loads(msg.payload.decode('string-escape').strip('"'))
        value = ((msg_dict["e"])[0])["v"]

        if (msg.topic == '/MyGreenFridge/'+ self.userID +"temperature"):
            # This is all temporary. I don't know what to put in these links
            data = urllib.urlopen("https://api.thingspeak.com/update?api_key=AFD10RO5MXMAS7XU&field1="+str(value))
            print ("Temperature value updated")
            # Where do I take the value? 
            print value

            elif (msg.topic == '/MyGreenFridge/'+ self.userID +"/humidity") :
                data = urllib.urlopen("https://api.thingspeak.com/update?api_key=AFD10RO5MXMAS7XU&field1="+str(value))
                print ("Humidity value updated")
                print value

            elif (msg.topic =='/MyGreenFridge/'+ self.userID +"/ean0") :
                data = urllib.urlopen("https://api.thingspeak.com/update?api_key=J4GGNYGH12CM8ZGY&field1="+str(value))
                print ("Input EAN code updated")
                print value

            elif (msg.topic == '/MyGreenFridge/'+ self.userID +"/ean1") :
                self.pCalc.energyLightCalc(int(value))
                data = urllib.urlopen("https://api.thingspeak.com/update?api_key=U5K874E6RLTA6PCE&field1="+str(value))
                print ("Outout EAN code updated")
                print value

            #elif (msg.topic == '/MyGreenFridge/'+ self.userID +"/Tcontrol"):
                #msg_dict = json.loads (msg.payload)
                #value = int(msg_dict["v"])
                #self.pCalc.energyHeatCalc(value)

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

    conf_file = open("configControl.txt", 'r') 
    conf_file_dict = json.loads(conf_file.read())
    conf_file.close()
    userID = conf_file_dict['userID'] # I guess this is how it will be called in the config file
    catalogIP = conf_file_dict['catalogip'] # Check

    try:
		r2 = requests.get('http://'+ catalogIP + ':8080/broker')
		r2.raise_for_status()

		brokerip = r2.json()['broker_IP']
		print brokerip
		brokerport = r2.json()['broker_port']
    except requests.HTTPError as err:
            print 'Error in posting, aborting' 
            sys.exit()

    # in case I do some other estimation, see at github for references. 

    tsdm = ThingSpeakDataManager(deviceID, brokerip, brokerport)

    tsdm.start()
    time.sleep(2) # do I need this? Probably I will understand only when I run it...
    tsdm.mySubscribe('/MyGreenFridge/#')

    while True:
        time.sleep(1)



