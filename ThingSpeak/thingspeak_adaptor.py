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

"""
Quello che tu (essendo thinkspeak) sai è l'user_ID, perché altrimenti dubito potrai mai sapere quali sono i prodotti che stai buttando o in generale i dati che ti appartengono
Esiste una funzione sul catalog che, dato lo user_ID, ti restituisce il fridge_ID corrispondente. (Un frigo può avere un solo user)

*questa richiesta va fatta con una GET al catalog, ed è del tipo /user_fridge?User_ID=...*
Quindi la prima cosa che devi fare è sicuramente una get di questo tipo per conoscere chi è il frigo

Dopo che sai chi è perché appunto ti viene ritornato, puoi fare un'altra GET al Catalog chiedendo 
con /wasted?Fridge_ID=... l'elenco dei prodotti che l'utente ha buttato
@PetronillaR spero di averti chiarito le idee
Nel primo caso devi scrivere:

url_richiesta= http://catalogIP:catalogPort/user_fridge?User_ID=QUELLO CHE CONOSCI
richiesta = requests.get(url_richiesta)

Nel secondo caso sarà:
url_richiesta= http://catalogIP:catalogPort/wasted?Fridge_ID=QUELLO CHE ORMAI CONOSCI
richiesta = requests.get(url_richiesta)

"""
## ---> subscriber class, to manage the messages in MQTT
class ThingSpeakDataManager :

    def __init__(self, userID, fridgeID, broker, port):
        """ 
        This is the constructor function of the class. 
        -----
        userID : identification of a device to which subscribing
              string
        broker : identifying the broker of the communication

        port : identifying the port in which the communication takes place

        """
        self.userID = userID
        self.fridgeID = fridgeID
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

        if (msg.topic == '/MyGreenFridge/'+ self.userID + "/" + self.fridgeID + "/temperature"):
            # This is all temporary. I don't know what to put in these links
            # CANALI DIVERSI CON UN SOLO FIELD? O STESSO CANALE E VARI FIELD?
            data = urllib.urlopen("https://api.thingspeak.com/update?api_key=PM5FIRRRHSDYV80C&field1="+str(value))
            print ("Temperature value updated")
            # Where do I take the value? 
            print value

            elif (msg.topic == '/MyGreenFridge/'+ self.userID + "/" + self.fridgeID +"/humidity") :
                data = urllib.urlopen("https://api.thingspeak.com/update?api_key=PM5FIRRRHSDYV80C&field2="+str(value))
                print ("Humidity value updated")
                print value

            elif (msg.topic =='/MyGreenFridge/'+ self.userID + "/" + self.fridgeID +"/wasted_products") :
                data = urllib.urlopen("https://api.thingspeak.com/update?api_key=PM5FIRRRHSDYV80C&field3="+str(value))
                print ("Input EAN code updated")
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
    catalogIP = configDict['catalogIP']
    catalogPort = configDict['catalogPort']
    fridgeID = configDict["fridgeID"] # Do I have it? Or should I ask for the conversion to the catalog?

    print("Catalog IP is: " + catalogIP)
    print("Catalog port is " + catalogPort)
    
    # retrieve the broker IP and the broker port from the Catalog
    catalogURL = "http://" + catalogIP + ":" + catalogPort
    try:
        r = requests.get(catalogURL + "/broker")
        broker = r.json()
        brokerIP = broker["broker_IP"]
        brokerPort = broker["broker_port"]
    except requests.RequestException as err:
        #sys.exit("ERROR: cannot retrieve the Broker IP from the Catalog.")
        pass
    
    # Taking the wasted products here
    try:
        r2 = requests.get(catalogURL+ "/wasted")
        wasted_json = r2.json()
    except requests.RequestException as err:
        #did not find the list of wasted products
        pass

    tsdm = ThingSpeakDataManager(deviceID, brokerip, brokerport)

    tsdm.start()
    time.sleep(2) # do I need this? Probably I will understand only when I run it...
    tsdm.mySubscribe('/MyGreenFridge/#')

    while True:
        time.sleep(1)



# Per prendere informazioni sui prodotti che sono consumati la richiesta va fatta in REST al catalog.

# PER TESTARE DEVO USARE MOSQUITTO
# Devo configurare la pagina di MQTT sul thingspeak adaptor, dopodiché quando uso Mosquitto devo specificare qual è
# il mio broker, la porta, qual è la funzione (pub), il topic e il messaggio. Apro il terminale
# gli passo questa linea di codice. Prima ovviamente devo runnare il thingspeak adaptor. Quello che lui fa è il
# subscriber. Scrivi prima il topic, assicurati che esca SUBSCRIBING TO TOPIC ETC. ETC. Quando il codice sta runnando
# apro un'altra finestra e inizio a fare da publisher con mosquitto. Il broker non devo aprirlo, lo fa in automatico
# quando apro mosquitto.

# se voglio testare solo thingspeak e non anche il mqtt posso passare dei valori a caso nel main. Magari devo cambiare
# un po' il modo in cui ho impostato le clasi in questo programma. Vedere il main del temperatureWS. 

### DA CHIEDERE MARTEDì:

# Perché io nel config non dovrei avere il frigdeID?

# Il device connector è il modo di registrarsi al sistema. Il thingspeak adaptor... invece...........
# deve fare il servizio che svolge per tutti gli utenti del sistema. Il device connector è associato ad una
# raspberry, quindi è posseduto da una persona. 

# dovrei fare get users dal catalog, e fare un for per tutti gli user, forse?
# DEVO METTERE ANCHE L'API NELLA CONFIGURAZIONE --> mettere un dizionario che associa
# un API a ogni frigorifero.
# fridges = { "ID": #API; }