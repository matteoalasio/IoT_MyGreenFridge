import telepot
import time
from telepot.loop import MessageLoop
import telepot.api
import requests
import json
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
import re
import threading
import urllib3
import sys


#chat_id is a unique identifier for the target chat or username of the target channel (in the format @channelusername)

class MyGreenFridgeBot:

    def __init__(self, conf_file):

        file = open(conf_file, 'r')
        dict = json.loads(file.read())
        file.close()

        # Variables that keep track of a conversation
        self.user_states = [] # list of dictionaries with {'user': chat_id, 'state': temp|light, 'terr': terr_id}

        self.token = dict['token']
        self.catalogIP = dict['catalog_IP']
        self.catalogport = str(dict['catalog_port'])
        self.bot = telepot.Bot(token=str(self.token))

        MessageLoop(self.bot, {'chat': self.on_chat_message, 'callback_query': self.on_callback_query}).run_as_thread()

    def on_chat_message(self, msg):

        content_type, chat_type, chat_id = telepot.glance(msg)

        if content_type == 'text':

            name = msg["from"]["first_name"]
            command = msg['text']

            if command == '/start':
                self.bot.sendMessage(chat_id, "Hello " + name + "! Please register yourself with /register to get started. If you need more infos, use the command /info.")

            elif command == '/info':
                self.bot.sendMessage(chat_id, """You can register yourself on the system with: /register. Remember to use your user_ID! \n
To associate a fridge to your user, use the command /add_fridge.\n
Don't you remember you password? No problem! Use the command /password. \n
To change your password, use the command /update_pw.\n
To check the status of your fridge, use the command /check. The available infos are related to humidity, fridge, products in the fridge and the products that you have wasted.\n
To delete yourself from the system, use the command /delete. \n
To be informed when the temperature becomes out of range, please set it with /alarm. \n
                 """)

            #Registration of a new user
            elif command.startswith ('/register'):

                params_bot = command.split(' ')
                if len(params_bot) < 3:
                    self.bot.sendMessage(chat_id, 'The correct syntax is:\n /register user_ID password')
                    return
                ID = params_bot[1]
                pw = params_bot[2]

                payload = {'ID': ID, 'nickname':name, 'ID_bot':chat_id, 'password':pw}
                #URL = 'http://' + self.catalogIP + ':' + self.catalogport + '/update_user'
                URL = 'http://' + self.catalogIP + ':' + self.catalogport + '/add_user'
                try:
                	r = requests.post(URL, data = json.dumps(payload))
                	r.raise_for_status()
                except requests.HTTPError as err:
                    self.bot.sendMessage(chat_id, 'An error happened during registration. Try again.')
                    print (err)
                    return

                self.bot.sendMessage(chat_id, "Hello " + name + "! You're now registered in the system." )


            #Registration of a fridge
            elif command.startswith ('/add_fridge'):

                params_bot = command.split(' ')
                if len(params_bot) < 4:
                    self.bot.sendMessage(chat_id, 'The correct syntax is:\n /add_fridge user_ID password fridge_ID')
                    return
                ID = params_bot[1]
                pw = params_bot[2]
                fridge_ID = params_bot[3]

                payload = {'ID': fridge_ID, 'user': ID}

                URL = 'http://' + self.catalogIP + ':' + self.catalogport + '/add_fridge/'
                try:
                    #Check if the user has the permission to register the fridge
                    r = requests.get('http://' + self.catalogIP + ':' + self.catalogport + '/user?ID=' + str(ID))
                    r.raise_for_status()
                    detail_user = r.json()
                    user = json.loads(detail_user['user'])
                    password = user['password']
                    if (str(password) != str(pw)):
                        self.bot.sendMessage(chat_id, "You can't apply any modification on this user. Please try another user_ID or insert the correct password.")
                        return

                    r2 = requests.post(URL, data = json.dumps(payload))
                    r2.raise_for_status()
                except requests.HTTPError as err:
                    self.bot.sendMessage(chat_id, 'An error happened during registration of the fridge. Try again.')
                    print (err)
                    return

                self.bot.sendMessage(chat_id, "Hello " + name + "! The fridge " + fridge_ID + " is now registered in your system." )

            #Obtain your password
            elif command.startswith ('/password'):

                params_bot = command.split(' ')
                if len(params_bot) < 2:
                    self.bot.sendMessage(chat_id, 'The correct syntax is:\n /password user_ID')
                    return
                ID = params_bot[1]

                try:
                #Check if the user has the permission to get the password
                    r = requests.get('http://' + self.catalogIP + ':' + self.catalogport + '/user?ID=' + str(ID))
                    r.raise_for_status()
                    detail_user = r.json()
                    user = json.loads(detail_user['user'])
                    nickname = user['nickname']
                    ID_bot = user['ID_bot']
                    if (str(ID_bot) != str(chat_id)):
                        self.bot.sendMessage(chat_id, "You can't know the password of this user. Please try another user_ID.")
                        return
                    password = user['password']

                except requests.HTTPError as err:
                    self.bot.sendMessage(chat_id, 'An error happened during registration of the fridge. Try again.')
                    print (err)
                    return

                self.bot.sendMessage(chat_id, "Hello " + name + "! Your password is " + password)


            #Update the password
            elif command.startswith ('/update_pw'):

                params_bot = command.split(' ')
                if len(params_bot) < 4:
                    self.bot.sendMessage(chat_id, 'The correct syntax is:\n /update_pw user_ID password new_password')
                    return
                user_ID = params_bot[1]
                pw = params_bot[2]
                new_pw = params_bot[3]

                payload = {'password': pw, 'new_password': new_pw}

                URL = 'http://' + self.catalogIP + ':' + self.catalogport + '/update_password?User_ID=' + str(user_ID)
                try:
                    r = requests.put('http://' + self.catalogIP + ':' + self.catalogport + '/update_password?User_ID=' + str(user_ID), data = json.dumps(payload))
                    r.raise_for_status()

                except requests.HTTPError as err:
                    self.bot.sendMessage(chat_id, 'An error happened while changing password. Try again.')
                    print (err)
                    return

                self.bot.sendMessage(chat_id, "Hello " + name + "! Your password has been updated. ")


            elif command.startswith ('/delete'):

                params_bot = command.split(' ')
                if len(params_bot) < 3:
                    self.bot.sendMessage(chat_id, 'The correct syntax is:\n /delete user_ID password')
                    return
                user_ID = params_bot[1]
                pw = params_bot[2]

                try:
                	#Check if the user has the persmission to register itself with that user_ID
	                r = requests.get('http://' + self.catalogIP + ':' + self.catalogport + '/user?ID=' + str(user_ID))
	                r.raise_for_status()
	                detail_user = r.json()
	                user = json.loads(detail_user['user'])
	                password = user['password']
	                if (str(password) != str(pw)):
	                	self.bot.sendMessage(chat_id, "You can't delete this user. Please try another user_ID or insert the correct password.")
	                	return

                	URL = 'http://' + self.catalogIP + ':' + self.catalogport + '/user?ID=' + str(user_ID)

                	r2 = requests.delete(URL)
                	r2.raise_for_status()
                except requests.HTTPError as err:
                    self.bot.sendMessage(chat_id, 'An error happened during cancellation. Try again.')
                    print (err)
                    return

                self.bot.sendMessage(chat_id, "Hello " + name + "! You're no more part of the system.. Bye!")


            elif command.startswith('/check'):

                params_bot = command.split(' ')

                if len(params_bot) < 2:
                    self.bot.sendMessage(chat_id, 'Correct syntax is:\n /check user_ID password fridge_ID')
                    return

                try:
                    ID = params_bot[1]
                    pw = params_bot[2]
                    fridge_ID = params_bot[3]

                    #Check if the user has the permission to register the fridge
                    r = requests.get('http://' + self.catalogIP + ':' + self.catalogport + '/user?ID=' + str(ID))
                    r.raise_for_status()
                    detail_user = r.json()
                    user = json.loads(detail_user['user'])
                    password = user['password']
                    if (str(password) != str(pw)):
                        self.bot.sendMessage(chat_id, "You can't apply any modification on this user. Please try another user_ID or insert the correct password.")
                        return

                except requests.HTTPError as err:
                    self.bot.sendMessage(chat_id, 'An error happened. Correct syntax is: /check user_ID. Please, try again.')
                    return


                keyboard = InlineKeyboardMarkup(inline_keyboard=[
                     [InlineKeyboardButton(text='Humidity', callback_data='humidity_' + str(fridge_ID)),
                     InlineKeyboardButton(text='Temperature', callback_data='temperature_' + str(fridge_ID))],
                     [InlineKeyboardButton(text='Wasted', callback_data='wasted_' + str(fridge_ID)),
                     InlineKeyboardButton(text='Products', callback_data='products_' + str(fridge_ID))]])

                msg = self.bot.sendMessage(chat_id, 'What do you want to check?', reply_markup=keyboard)



            elif command.startswith('/add_product'):
                params_bot = command.split(' ')

                if len(params_bot) < 3:
                    self.bot.sendMessage(chat_id, 'Correct syntax is: /add_product fridge_ID product_name expiration_date. Please insert expiration date as dd/mm/yyyy')
                    return

                fridge_ID = params_bot[1]
                product_ID = params_bot[2]
                exp_date = params_bot[3]

                try:
                    #Get the ip and port of ProductAdaptorWS
                    r = requests.get('http://' + self.catalogIP + ':' + self.catalogport + "/web_service?Name=" + "ProductAdaptorWS")
                    dict = r.json()
                    IP = dict['URL']['IP']
                    port = dict['URL']['port']
                    url_WS = "http://" + str(IP) + ":" + str(port) + "/"

                    expiration_date = exp_date.split('/')
                    day = expiration_date[0]
                    month = expiration_date[1]
                    year = expiration_date[2]
                    body = json.dumps({"day":day, "month":month, "year":year})

                    r2 = requests.post(str(url_WS) + "add_expiration?Fridge_ID=" +str (fridge_ID) + "&Product_ID=" + str(product_ID), data=body)

                except requests.HTTPError as err:
                    self.bot.sendMessage(chat_id, 'An error happened. Please, try again.')
                    return

                self.bot.sendMessage(chat_id, "The expiration date of the " + str(product_ID) + " has been updated.")


            elif command.startswith('/add_wasted'):
                params_bot = command.split(' ')

                if len(params_bot) < 3:
                    self.bot.sendMessage(chat_id, 'Correct syntax is: /add_wasted fridge_ID product_name.')
                    return

                fridge_ID = params_bot[1]
                product_ID = params_bot[2]

                keyboard = InlineKeyboardMarkup(inline_keyboard=[
                     [InlineKeyboardButton(text='Wasted', callback_data='wastedProduct_' + str(fridge_ID) +'_' + str(product_ID)) ,
                     InlineKeyboardButton(text='Consumed', callback_data='consumedProduct_'+ str(fridge_ID) +'_' + str(product_ID))]])

                msg = self.bot.sendMessage(chat_id, 'Did you eat or waste the product ' + str(product_ID) +'?', reply_markup=keyboard)



            elif command.startswith('/alarm'):
                params_bot = command.split(' ')

                if len(params_bot) < 3:
                    self.bot.sendMessage(chat_id, 'Correct syntax is:\n /alarm user_ID password fridge_ID')
                    return

                user_ID = params_bot[1]
                pw = params_bot[2]
                fridge_ID = params_bot[3]

                try:
                    #Check if the user has the persmission to register itself with that user_ID
                    r = requests.get('http://' + self.catalogIP + ':' + self.catalogport + '/user?ID=' + str(user_ID))
                    r.raise_for_status()
                    detail_user = r.json()
                    user = json.loads(detail_user['user'])
                    password = user['password']
                    if (str(password) != str(pw)):
                        self.bot.sendMessage(chat_id, "You can't make modification on this user. Please try another user_ID or insert the correct password.")
                        return


                except requests.HTTPError as err:
                    self.bot.sendMessage(chat_id, 'An error happened. Correct syntax is: /check user_ID. Please, try again.')
                    return

                keyboard = InlineKeyboardMarkup(inline_keyboard=[
                     [InlineKeyboardButton(text='ON', callback_data='on_' + str(fridge_ID)),
                     InlineKeyboardButton(text='OFF', callback_data='off_' + str(fridge_ID))]])

                msg = self.bot.sendMessage(chat_id, 'Set the alarm status for the temperature:', reply_markup=keyboard)


    def on_callback_query(self, msg):
        query_id, chat_id, query_data = telepot.glance(msg, flavor='callback_query')
        query = query_data.split('_')[0]
        fridge_ID = query_data.split('_')[1]


        URL = 'http://' + self.catalogIP + ':' + self.catalogport


        if query == 'temperature':
            try:
                # /fridge?ID=<id> : Provide information about a fridge with a specific fridge_ID
                r = requests.get(URL + '/fridge?ID=' + str(fridge_ID))
                r.raise_for_status()
                res = r.json()
                fridge = res['fridge']
                for sensor in fridge['sensors']:
                    if (sensor['sensor_ID']=='temperature'):
                        temp = sensor['Value']
            except:
                self.bot.sendMessage(chat_id, 'An error happened. Try again.')
                return

            self.bot.sendMessage(chat_id, 'The current temperature is %d'%temp + '°C')

        elif query == 'humidity':
            try:
                # /fridge?ID=<id> : Provide information about a fridge with a specific fridge_ID
                r2 = requests.get(URL + '/fridge?ID=' + str(fridge_ID))
                r2.raise_for_status()
                res = r2.json()
                fridge = res['fridge']
                for sensor in fridge['sensors']:
                    if (sensor['sensor_ID']=='humidity'):
                        hum = sensor['Value']
            except:
                self.bot.sendMessage(chat_id, 'An error happened. Try again.')
                return

            self.bot.sendMessage(chat_id, 'The current humidity is %d'%hum + '%')


        elif query == 'products':
            #- /products?Fridge_ID=<IDFridge>
            try:
                # /fridge?ID=<id> : Provide information about a fridge with a specific fridge_ID
                r2 = requests.get(URL + '/products?Fridge_ID=' + str(fridge_ID))
                r2.raise_for_status()
                res = r2.json()
                products = res['Products']
                i=1
                list_products = []
                for product in products:
                    print ("Sei qui!")
                    expirationdate = product['Exp_date']
                    if expirationdate:
                        listed_product = str(i) +") " + str(product['product_ID']) + " " + str(product['brand']) + " with expiration date: " + str(expirationdate['day']) + '/' + str(expirationdate['month']) + '/' + str(expirationdate['year']) + " "
                        list_products.append(listed_product)
                    else:
                        listed_product = str(i) +") " + str(product['product_ID']) + " " + str(product['brand'])
                        list_products.append(listed_product)
                    i=i+1

            except:
                e = sys.exc_info()[0]
                print(e)
                self.bot.sendMessage(chat_id, 'An error happened. Try again.')

                return

            self.bot.sendMessage(chat_id, "List of available product: \n"  + str(list_products))


        elif query == 'wasted':
            try:
                # /wasted?Fridge_ID=<IDFridge>
                r2 = requests.get(URL + '/wasted?Fridge_ID=' + str(fridge_ID))
                r2.raise_for_status()
                res = r2.json()
                # {"Wasted_products": [{"product_ID": "Patata"}]}
                was_products = res['Wasted_products']
                i=1
                list_was_products = []
                for was_product in was_products:
                    listed_was_product = str(i) +") " + str(was_product['product_ID'])
                    list_was_products.append(listed_was_product)
                    i=i+1


            except:
                self.bot.sendMessage(chat_id, 'An error happened. Try again.')
                return

            self.bot.sendMessage(chat_id, "List of wasted product: \n" + str(list_was_products))

        elif query == 'wastedProduct':
            product_ID = query_data.split('_')[2]

            try:
                #Get the ip and port of ProductAdaptorWS
                r = requests.get('http://' + self.catalogIP + ':' + self.catalogport + "/web_service?Name=" + "ProductAdaptorWS")
                dict = r.json()
                IP = dict['URL']['IP']
                port = dict['URL']['port']
                url_WS = "http://" + str(IP) + ":" + str(port) + "/"
                print(url_WS)

                body = json.dumps({"status":"wasted"})

                r2 = requests.post(str(url_WS) + "add_wasted?Fridge_ID=" +str (fridge_ID) + "&Product_ID=" + str(product_ID), data=body)
                #headers = {'Content-Type':'text/html'}
                #r2 = requests.request("POST", str(url_WS), headers=headers)

            except:
                self.bot.sendMessage(chat_id, 'An error happened. Try again.')
                return
            self.bot.sendMessage(chat_id, 'The product has been successfully registered as wasted.')

        elif query == 'consumedProduct':
            product_ID = query_data.split('_')[2]
            try:
                #Get the ip and port of ProductAdaptorWS
                r = requests.get('http://' + self.catalogIP + ':' + self.catalogport + "/web_service?Name=" + "ProductAdaptorWS")
                dict = r.json()
                IP = dict['URL']['IP']
                port = dict['URL']['port']
                url_WS = "http://" + str(IP) + ":" + str(port) + "/"

                body = json.dumps({"status":"consumed"})

                r2 = requests.post(str(url_WS) + "add_wasted?Fridge_ID=" +str (fridge_ID) + "&Product_ID=" + str(product_ID), data=body)

            except:
                self.bot.sendMessage(chat_id, 'An error happened. Try again.')
                return
            
            self.bot.sendMessage(chat_id, 'The product has been successfully removed from the fridge.')

        elif query == 'on':
            try:
                #Changing the status of the alarm on the Catalog
                r = requests.get(URL + '/alarm_status?Fridge_ID=' + str(fridge_ID) + '&Alarm=on')
                r.raise_for_status()

            except:
                self.bot.sendMessage(chat_id, 'An error happened. Try again.')
                return

            self.bot.sendMessage(chat_id, "The alarm has been turned ON, as you requested.")


        elif query == 'off':
            try:
                #Changing the status of the alarm on the Catalog
                r = requests.get(URL + '/alarm_status?Fridge_ID=' + str(fridge_ID) + '&Alarm=off')
                r.raise_for_status()

            except:
                self.bot.sendMessage(chat_id, 'An error happened. Try again.')
                return

            self.bot.sendMessage(chat_id, "The alarm has been turned OFF, as you requested.")



if __name__ == '__main__':

    Fridge_Bot = MyGreenFridgeBot("botconfig.txt")


    while 1:
        time.sleep(10)
