"""The Temperature Alarm Web Service sends a warning through REST Web Services to the
available interfaces (in this case, Telegram Bot) when the temperature is above the threshold and
the alarm has been enabled by the user. The communication about the status of the temperature is
received from the Fridge Status Adaptor through REST Web Services."""


import time
import json
import requests
import cherrypy
import threading
import socket

class TemperatureAlarmThread(threading.Thread):
        
        def __init__(self, userID, fridgeID, catalog_URL):
            threading.Thread.__init__(self)
            self.user_ID = userID
            self.fridge_ID = fridgeID
            self.catalog_url = catalog_URL
            #self.control = control
        
        def run(self):
            while True:

                #Get the IP where to find the resource
                r3 = requests.get(catalog_URL+"web_service?Name="+"FridgeStatusWS")
                dict = r3.json()
                IP = dict['URL']['IP']
                port = dict['URL']['port']
                url_WS = "http://" + IP + ":" + port + "/"
                
                print (self.user_ID, self.fridge_ID)
                #Make the request to obtain the value of the current status
                url = "status?User_ID="+ str(self.user_ID) + "&Fridge_ID=" + str(self.fridge_ID)
                r4 = requests.get(url_WS + url)
                res = r4.json()
                print (res)

                #Check the status of the fridge
                if (res['Current status']==1 or res['Current status']== -1):
                    #Alarm the bot
                    #Qui deve fare una richiesta con GET al bot, che deve restituirgli se lo stato di allarme
                    #è stato selezionato o meno. Se lo stato di allarme è stato selezionato,
                    #deve fare una POST al bot per attivare il warning. (PENSO)
                    return
                return



if __name__ == '__main__':
    #Open file of configuration, including the data of the catalog
    file = open("Configuration.txt","r")
    info = json.loads(file.read())

    catalog_IP = info["catalog_IP"]
    catalog_Port = info["catalog_port"]

    file.close()
    catalog_URL = "http://" + catalog_IP + catalog_Port

    user_ID = 110995 #CAPIRE DA DOVE ARRIVA QUESTO PARAMETRO! PRESUMO DA TELEGRAM

    r = requests.get(catalog_URL + "user_fridge?User_ID="+ str(user_ID))
    fridge_ID = r.json()

    #Register the WS in the CATALOG
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    ip = s.getsockname()[0]
    port = "8687"
    web_service = json.dumps({"name":"TemperatureAlarmWS", "IP":ip, "port":port})
    r2 = requests.post(catalog_URL + "add_WS", web_service)

    TempAlarm_Thread = TemperatureAlarmThread(user_ID, fridge_ID, catalog_URL)

    TempAlarm_Thread.start()
