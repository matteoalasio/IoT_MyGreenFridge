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

            print (time.localtime(None))
            count = 0
            for i in time.localtime(None):
                if (count == 0):
                    year = i
                    print (year)
                elif (count == 1):
                    month = i
                    print (month)
                elif (count ==2):
                    day = i
                    print (day)
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
                        if (int(product['Exp_date']['day']) - int(day) <=3):
                            difference =  int(product['Exp_date']['day']) - int(day)
                            try:
                                if difference == 0:
                                    r2 = requests.get('https://api.telegram.org/bot' + self.bot_Token + '/sendMessage?chat_id=' + str(ID_bot) +
                                              '&text=' + 'Attention! Your ' + str(product['product_ID']) + ' will expire today')
                                    r2.raise_for_status()
                                else:
                                    r2 = requests.get('https://api.telegram.org/bot' + self.bot_Token + '/sendMessage?chat_id=' + str(ID_bot) +
                                              '&text=' + 'Attention! Your ' + str(product['product_ID']) + ' will expire in ' + str(difference) + ' days')
                                    r2.raise_for_status()

                            except requests.HTTPError as error:
                                print(error)


            time.sleep(24*60*60)



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
    web_service = json.dumps(
        {"name": "ExpirationAlarmWS", "IP": ip, "port": port})
    r2 = requests.post(catalog_URL + "add_WS", web_service)

    user_ID = 110995  # CAPIRE DA DOVE ARRIVA QUESTO PARAMETRO! PRESUMO DA TELEGRAM

    r = requests.get(catalog_URL + "user_fridge?User_ID=" + str(user_ID))
    fridge_ID = r.json()

    ExpAlarm_Thread = ExpirationAlarmThread(bot_Token, user_ID, fridge_ID, catalog_URL)

    ExpAlarm_Thread.start()
