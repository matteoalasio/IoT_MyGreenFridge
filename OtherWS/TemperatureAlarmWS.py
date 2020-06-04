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

    def __init__(self, botToken, userID, fridgeID, catalog_URL):
        threading.Thread.__init__(self)
        self.bot_Token = botToken
        self.user_ID = userID
        self.fridge_ID = fridgeID
        self.catalog_url = catalog_URL
        #self.control = control

    def run(self):
        while True:

            # Get the IP where to find the resource
            r3 = requests.get(
                catalog_URL + "web_service?Name=" + "FridgeStatusAdaptorWS")
            dict = r3.json()
            IP = dict['URL']['IP']
            #port = dict['URL']['port']
            port = 8585
            url_WS = "http://" + str(IP) + ":" + str(port) + "/"

            print(self.user_ID, self.fridge_ID)
            # Make the request to obtain the value of the current status
            url = "status?User_ID=" + \
                str(self.user_ID) + "&Fridge_ID=" + str(self.fridge_ID)
            r4 = requests.get(url_WS + url)
            res = r4.json()

            # Check the status of the fridge
            if (res['Current status'] == 1 or res['Current status'] == -1):

                r5 = requests.get(self.catalog_url +
                                  "fridge?ID=" + str(self.fridge_ID))
                res5 = r5.json()
                alarm_status = res5['fridge']['alarm_status']

                r6 = requests.get(self.catalog_url +
                                  'user?ID=' + str(self.user_ID))
                r6.raise_for_status()
                detail_user = r6.json()
                user = json.loads(detail_user['user'])
                ID_bot = user['ID_bot']

                if str(alarm_status) == "on":
                    try:
                        # Sending the temperature alert'
                        r7 = requests.get('https://api.telegram.org/bot' + self.bot_Token + '/sendMessage?chat_id=' + str(ID_bot) +
                                          '&text=' + 'The temperature of fridge ' + str(self.fridge_ID) + ' is out of the normal range.')
                        r7.raise_for_status()
                    except requests.HTTPError as error:
                        print(error)

            time.sleep(10)

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
                web_service = json.dumps({"name": "TemperatureAlarmWS", "IP": self.WS_IP, "port": self.WS_Port})
                r1 = requests.post(catalog_URL + "add_WS", web_service)

                print("TemperatureAlarmWS registered.")

                time.sleep(60*60)



if __name__ == '__main__':
    # Open file of configuration, including the data of the catalog
    file = open("Configuration.txt", "r")
    info = json.loads(file.read())
    catalog_IP = info["catalog_IP"]
    catalog_Port = info["catalog_port"]
    file.close()

    file2 = open("botconfig.txt", "r")
    info2 = json.loads(file2.read())
    bot_Token = info2["token"]
    file2.close()

    catalog_URL = "http://" + catalog_IP + catalog_Port

    user_ID = 110995  # CAPIRE DA DOVE ARRIVA QUESTO PARAMETRO! PRESUMO DA TELEGRAM
    #Get the list of the users
    r3 = requests.get(catalog_URL + 'users/')
    users = r3.json()



    # Register the WS in the CATALOG
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    ip = s.getsockname()[0]
    port = "8687"

    regThread = RegistrationThread(catalog_IP, catalog_Port, ip, port)
    regThread.start()

    for user in users['users']:
        user_ID = user['ID']
        r = requests.get(catalog_URL + "user_fridge?User_ID=" + str(user_ID))

        if (r.status_code == 200):
            fridge_ID = r.json()

            TempAlarm_Thread = TemperatureAlarmThread(
                bot_Token, user_ID, fridge_ID, catalog_URL)

            TempAlarm_Thread.start()
