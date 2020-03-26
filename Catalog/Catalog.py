import time
import json


class Catalog(object):

	def __init__(self, filename):
		self.filename = filename 
        #Inizializziamo il catalog con un file in cui sono raccolte tutte le informazioni


    #Return information about broker IP address and port
	def broker(self):
		file = open(self.filename, 'r')
		json_file = file.read()
		dict = json.loads(json_file)
		file.close()

		return dict['broker_IP'], dict['broker_port']


    #Associate to a user, a specific fridge
	def associate_user_fridge(self, user_ID, fridge_ID):
		file = open(self.filename, 'r')
		json_file = file.read()
		dict = json.loads(json_file)
		file.close()

		# Search for the user
		user_found = 0
		for user in dict['users']:
			if user['ID'] == user_ID:
				user_found = 1
				break
			if user_found == 0:
				return "User not found!"

		#If the user is found, search for the fridge
		for fridge in dict['fridges']:
			if fridge['ID'] == fridge_ID:
				fridge['user'] = user_ID
				file = open(self.filename, 'w')
				file.write(json.dumps(dict))
				file.close()
				return "Search is ended, the association is complete"

		#If the fridge is not found, return an error
		return "Fridge not found!"


###################################### USERS MANAGEMENT ########################################

    #Return information about users: list of available ones.    
	def get_users (self):
		file = open(self.filename, 'r')
		json_file = file.read()
		dict = json.loads(json_file)
		file.close()

		return dict['users']


    #Return information about a specific user: this occurs only if the specified ID is valid.
	def get_user(self, user_ID):
		file = open(self.filename, 'r')
		json_file = file.read()
		dict = json.loads(json_file)
		file.close()

		for user in dict['users']:
			if user['ID'] == user_ID:
				return json.dumps(user)

		#If the user is not found, return an error
		return "User not found!"


    #Add a new user
	def add_user(self, added_user):
		file = open(self.filename, 'r')
		json_file = file.read()
		dict = json.loads(json_file)
		file.close()

		dict['users'].append({'ID': str(added_user['ID']),'nickname': added_user['nickname']})
		file = open(self.filename, 'w')
		file.write(json.dumps(dict))
		file.close()

		return "New user has been added"


    #Update an user that already exists
	def update_user(self, updated_user):
		file = open(self.filename, 'r')
		json_file = file.read()
		dict = json.loads(json_file)
		file.close()

		for user in dict['users']:
			if user['ID'] == str(updated_user['ID']):
				user['nickname'] = updated_user['nickname']
				file = open(self.filename, 'w')
				file.write(json.dumps(dict))
				file.close()
				return "User has been updated"

		return "User not found!"


    #Delete a specified user 
	def delete_user(self, user_ID):
		file = open(self.filename, 'r')
		dict = json.loads(file.read())
		file.close()

		#Delete a user from the users list
		for user in dict['users']:
			if user['ID'] == user_ID:
				dict['users'].remove(user)
				break

		#Delete a user from the dictionary of fridges
		for fridge in dict['fridges']:
			if fridge['user'] == user_ID:
				fridge['user'] = None #Dobbiamo inserire un valore di default?

		#Update the file after all the modification
		file = open(self.filename, 'w')
		file.close()
		print ("User has been deleted")

###################################### FRIDGES MANAGEMENT ########################################

	#Returns the information about all the available fridges
	def get_fridges(self):
		file = open(self.filename, 'r')
		json_file = file.read()
		dict = json.loads(json_file)
		file.close()

		return dict['fridges']


	#Return information about a specific fridge: in particular its ID and the associated user
	def get_fridge(self, fridge_ID):
		file = open(self.filename, 'r')
		json_file = file.read()
		dict = json.loads(json_file)
		file.close()

		for fridge in dict['fridges']:
			if fridge['ID'] == fridge_ID:
				return fridge

		#If the fridge is not found, return an error
		return "Fridge not found!"


	#Add a new fridge
	def add_fridge(self, added_fridge):
		file = open(self.filename, 'r')
		json_file = file.read()
		dict = json.loads(json_file)
		file.close()

		dict['fridges'].append({'ID': added_fridge['ID'],'user': None,
                                'sensors': added_fridge['sensors'],
                                'products': added_fridge['products'],
                                'insert-timestamp': time.time(),
                                'IP': added_fridge['IP'],
                                'port': added_fridge['port']})
		file = open(self.filename, 'w')
		file.write(json.dumps(dict))
		file.close()

		return "New fridge has been added"


	#Update a fridge that already exists
	def update_fridge(self, updated_fridge):
		file = open(self.filename, 'r')
		json_file = file.read()
		dict = json.loads(json_file)
		file.close()

		for fridge in dict['fridges']:
			if fridge['ID'] == str(updated_fridge['ID']):
				fridge['sensors'] = updated_fridge['sensors']
				fridge['products'] = updated_fridge['products']
				fridge['insert-timestamp'] = time.time()
				fridge['IP'] = updated_fridge['IP']
				fridge['port'] = updated_fridge['port']

				file = open(self.filename, 'w')
				file.write(json.dumps(dict))
				file.close()

				return "Fridge has been updated"

		return "Fridge not found!"


	#Delete a specified fridge
	def delete_fridge(self, fridge_ID):
		file = open(self.filename, 'r')
		dict = json.loads(file.read())
		file.close()

		for fridge in dict['fridges']:
			if fridge['ID'] == fridge_ID:
				dict['fridges'].remove(fridge)

				file = open(self.filename, 'w')
				file.write(json.dumps(dict))
				file.close()

				print ("Fridge has been deleted")
				break

###################################### SENSORS MANAGEMENT ########################################

    #Add a new sensor to a specified fridge
	def add_sensor(self, fridge_ID, added_sensor):
		file = open(self.filename, 'r')
		json_file = file.read()
		dict = json.loads(json_file)
		file.close()

		for fridge in dict['fridges']:
			if fridge['ID'] == fridge_ID:
				fridge['sensors'] = added_sensor
			
				file = open(self.filename, 'w')
				file.write(json.dumps(dict))
				file.close()

				return "Sensors have been added"

		return "Fridge not found!"

###################################### INACTIVE FRIDGE MANAGEMENT ########################################
   	
   	#Delete fridges older than an hour
	def remove_inactive_fridge(self):
		self.actual_time=time.time() 
		file = open(self.filename, 'r')
		dict = json.loads(file.read())
		file.close()

		for fridge in dict['fridges']:
			if actual_time - fridge['insert-timestamp'] > 60*60:
				dict['fridges'].remove(fridge)

		file = open(self.filename, 'w')
		file.write(json.dumps(dict))
		file.close()

