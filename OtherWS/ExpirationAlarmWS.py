"""The Expiration Alarm Web Service sends a warning through REST Web Services to the available interfaces
(in this case, Telegram Bot) when a product in the fridge is approaching its expiration date.
The expiration dates of the products are retrieved from the Catalog through REST Web Services.."""


import time
import json
import requests
import cherrypy
import threading
import socket


class ExpirationAlarmThread(threading.Thread):

    def __init__(self, botToken, userID, fridgeID, catalog_URL):
        threading.Thread.__init__(self)
        self.bot_Token = botToken
        self.user_ID = userID
        self.fridge_ID = fridgeID
        self.catalog_url = catalog_URL
        #self.control = control

    def run(self):
        while True:

            r = requests.get(catalog_URL + 'products?Fridge_ID=' + str(self.fridge_ID))
            res = r.json()

            count = 0
            for i in time.localtime(None):
                if (count == 0):
                    year = i
                elif (count == 1):
                    month = i
                elif (count ==2):
                    day = i
                else:
                    break
                count=count+1

            r6 = requests.get(self.catalog_url +
                                  'user?ID=' + str(self.user_ID))
            r6.raise_for_status()
            detail_user = r6.json()
            user = json.loads(detail_user['user'])
            ID_bot = user['ID_bot']

            for product in res['Products']:
                if (int(product['Exp_date']['year']) == int(year)):
                    if (int(product['Exp_date']['month']) == int(month)):
                        if (int(product['Exp_date']['day']) - int(day) <=3 and int(product['Exp_date']['day']) - int(day) >=0):
                            difference =  int(product['Exp_date']['day']) - int(day)
                            try:
                                if difference == 0:
                                    r2 = requests.get('https://api.telegram.org/bot' + self.bot_Token + '/sendMessage?chat_id=' + str(ID_bot) +
                                              '&text=' + 'Attention! Your ' + str(product['product_ID']) + ' ' + str(product['brand']) + ' will expire today')
                                    r2.raise_for_status()
                                else:
                                    r2 = requests.get('https://api.telegram.org/bot' + self.bot_Token + '/sendMessage?chat_id=' + str(ID_bot) +
                                              '&text=' + 'Attention! Your ' + str(product['product_ID']) + ' ' + str(product['brand']) + ' will expire in ' + str(difference) + ' days')
                                    r2.raise_for_status()

                            except requests.HTTPError as error:
                                print(error)


            time.sleep(24*60*60)

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
                web_service = json.dumps({"name": "ExpirationAlarmWS", "IP": self.WS_IP, "port": self.WS_Port})
                r1 = requests.post(catalog_URL + "add_WS", web_service)

                print("ExpirationAlarmWS registered.")

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
    # Register the WS in the CATALOG
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    ip = s.getsockname()[0]
    port = "8684"

    regThread = RegistrationThread(catalog_IP, catalog_Port, ip, port)
    regThread.start()

    #Get the list of the users
    r3 = requests.get(catalog_URL + 'users/')
    users = r3.json()

    for user in users['users']:
        user_ID = user['ID']

        r = requests.get(catalog_URL + "user_fridge?User_ID=" + str(user_ID))

        if (r.status_code == 200):
            fridge_ID = r.json()
            ExpAlarm_Thread = ExpirationAlarmThread(bot_Token, user_ID, fridge_ID, catalog_URL)

            ExpAlarm_Thread.start()
