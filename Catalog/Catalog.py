import time
import json


class Catalog(object):

	def __init__(self, filename):
		self.filename = filename

	# Return information about broker IP address and port
	def broker(self):
		file = open(self.filename, 'r')
		json_file = file.read()
		dict = json.loads(json_file)
		file.close()

		return dict['broker_IP'], dict['broker_port']

	# Update the password when already exists
	def update_pw(self, user_ID, updated_password):
		file = open(self.filename, 'r')
		json_file = file.read()
		dict = json.loads(json_file)
		file.close()

		for user in dict['users']:
			if user['ID'] == user_ID:
				if (user['password'] == updated_password['password']):
					user['password'] = updated_password['new_password']
					file = open(self.filename, 'w')
					file.write(json.dumps(dict))
					file.close()
					return "Password updated!"
				return "Password is not correct!"
		return "User not found!"

	# Update timestamp
	def update_timestamp(self):

		file = open(self.filename, 'r')
		json_file = file.read()
		dict = json.loads(json_file)
		file.close()

		dict['last_edit'] = time.time()
		file = open(self.filename, 'w')
		file.write(json.dumps(dict))
		file.close()
		return

	# Return information about all the catalog
	def all_catalog(self):
		file = open(self.filename, 'r')
		json_file = file.read()
		dict = json.loads(json_file)
		file.close()

		return dict



	# Associate to a user, a specific fridge
	# def associate_user_fridge(self, user_ID, fridge_ID):
	#     file = open(self.filename, 'r')
	#     json_file = file.read()
	#     dict = json.loads(json_file)
	#     file.close()

	#     user_found = 0
	#     for user in dict['users']:
	#         if user['ID'] == user_ID:
	#             user_found = 1

	#     if user_found == 0:
	#         return "User not found!"

	#     # If the user is found, search for the fridge
	#     for fridge in dict['fridges']:
	#         if fridge['ID'] == fridge_ID:
	#             fridge['user'] = user_ID
	#             file = open(self.filename, 'w')
	#             file.write(json.dumps(dict))
	#             file.close()
	#             return "Search is ended, the association is complete"
	#     return "Fridge not found!"


###################################### USERS MANAGEMENT ########################################

	# Return information about users: list of available ones.
	def get_users(self):
		file = open(self.filename, 'r')
		json_file = file.read()
		dict = json.loads(json_file)
		file.close()

		return dict['users']

	# Return information about a specific user: this occurs only if the specified ID is valid.
	def get_user(self, user_ID):
		file = open(self.filename, 'r')
		json_file = file.read()
		dict = json.loads(json_file)
		file.close()

		for user in dict['users']:
			if user['ID'] == user_ID:
				return json.dumps(user)
		return "User not found!"

	# Add a new user
	def add_user(self, added_user):
		file = open(self.filename, 'r')
		json_file = file.read()
		dict = json.loads(json_file)
		file.close()

		for user in dict['users']:
			# If the user is already present in the Catalog
			if (user['ID'] == added_user['ID']):
				return "User already present"

		# If it is not present, add it
		dict['users'].append({'ID': str(added_user['ID']), 'password': str(
			added_user['password']), 'nickname': added_user['nickname'], 'ID_bot': added_user['ID_bot']})
		file = open(self.filename, 'w')
		file.write(json.dumps(dict))
		file.close()
		return "New user has been added"

	# Update the nickname of a user that already exists
	def update_user(self, updated_user):
		file = open(self.filename, 'r')
		json_file = file.read()
		dict = json.loads(json_file)
		file.close()

		for user in dict['users']:
			if user['ID'] == str(updated_user['ID']):
				user['nickname'] = str(updated_user['nickname'])
				user['ID_bot'] = str(updated_user['ID_bot'])
				file = open(self.filename, 'w')
				file.write(json.dumps(dict))
				file.close()
				return "User has been updated"
		return "User not found!"

	# Delete a specified user
	def delete_user(self, user_ID):
		file = open(self.filename, 'r')
		dict = json.loads(file.read())
		file.close()

		# Delete a user from the users list
		flag = 0
		for user in dict['users']:
			if user['ID'] == user_ID:
				dict['users'].remove(user)
				flag = 1
				break

		# Delete the association between user and fridge
		for fridge in dict['fridges']:
			if fridge['user'] == user_ID:
				dict['fridges'].remove(fridge)

		file = open(self.filename, 'w')
		file.write(json.dumps(dict))
		file.close()
		if (flag == 1):
			return "User has been deleted"
		else:
			return "User not found!"

###################################### FRIDGES MANAGEMENT ########################################

	# Return the information about all the available fridges
	def get_fridges(self):
		file = open(self.filename, 'r')
		json_file = file.read()
		dict = json.loads(json_file)
		file.close()

		return dict['fridges']

	# Return information about a specific fridge: in particular its ID and the associated user
	def get_fridge(self, fridge_ID):
		file = open(self.filename, 'r')
		json_file = file.read()
		dict = json.loads(json_file)
		file.close()

		for fridge in dict['fridges']:
			if fridge['ID'] == fridge_ID:
				return fridge
		return "Fridge not found!"

	# Add a new fridge
	# def add_fridge(self, added_fridge):
	#     file = open(self.filename, 'r')
	#     json_file = file.read()
	#     dict = json.loads(json_file)
	#     file.close()

	#     flag = 0
	#     for fridge in dict['fridges']:
	#         if fridge['ID'] == added_fridge['ID']:
	#             flag = 1
	#             fridge['insert-timestamp'] = time.time()
	#             file = open(self.filename, 'w')
	#             file.write(json.dumps(dict))
	#             file.close()
	#             return "Fridge already present. Time has been updated."

	#     if flag == 0:
	#         dict['fridges'].append({'ID': added_fridge['ID'], 'user': None,
	#                                 'sensors': added_fridge['sensors'],
	#                                 'products': added_fridge['products'],
	#                                 'wasted': [],
	#                                 'alarm_status': "off",
	#                                 'insert-timestamp': time.time(),
	#                                 'IP': added_fridge['IP'],
	#                                 'port': added_fridge['port']})
	#     file = open(self.filename, 'w')
	#     file.write(json.dumps(dict))
	#     file.close()

	#     return "New fridge has been added"

   # Add a new fridge
	def add_fridge(self, fridge_user):
		file = open(self.filename, 'r')
		json_file = file.read()
		dict = json.loads(json_file)
		file.close()


		for user in dict['users']:
			if user['ID'] == fridge_user['user']:
				dict['fridges'].append({'ID': fridge_user['ID'], 'user': fridge_user['user'],
									'API':fridge_user['API'],
									'channel':fridge_user['channel'],
									'sensors': [],
									'products': [],
									'wasted': [],
									'alarm_status': "off",
									'insert-timestamp': None})
									#'IP': None,
									#'port': None})

				file = open(self.filename, 'w')
				file.write(json.dumps(dict))
				file.close()
				return "The fridge has been associated with the user."
		return "User not found!"


	# Update a fridge that already exists
	def update_fridge(self, updated_fridge):
		file = open(self.filename, 'r')
		json_file = file.read()
		dict = json.loads(json_file)
		file.close()


		for fridge in dict['fridges']:
			if fridge['ID'] == str(updated_fridge['ID']):
				fridge['ID'] = updated_fridge['ID']
				fridge['sensors'] = updated_fridge['sensors']
				fridge['insert-timestamp']=time.time()
				#fridge['IP'] = updated_fridge['IP'],
				#fridge['port'] = updated_fridge['port']
				file = open(self.filename, 'w')
				file.write(json.dumps(dict))
				file.close()

				return "Fridge has been updated"
		return "Fridge not found!"

	# Delete a specified fridge
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

				return "Fridge has been deleted"
		return "Fidge not found!"

	# Given the user_ID, it returns the relative fridge
	def get_user_fridge(self, user_ID):
		file = open(self.filename, 'r')
		dict = json.loads(file.read())
		file.close()

		for fridge in dict['fridges']:
			if fridge['user'] == user_ID:
				return fridge['ID']
		return "User not found!"

	def update_alarm_status(self, fridge_ID, alarm_status):
		file = open(self.filename, 'r')
		dict = json.loads(file.read())
		file.close()

		for fridge in dict['fridges']:
			if fridge['ID'] == str(fridge_ID):
				fridge['alarm_status'] = str(alarm_status)
				file = open(self.filename, 'w')
				file.write(json.dumps(dict))
				file.close()

				return "Alarm status has been updated!"
		return "Fridge not found!"


###################################### SENSORS MANAGEMENT ########################################

	# Add a new sensor to a specified fridge
	def add_sensor(self, fridge_ID, added_sensor):
		file = open(self.filename, 'r')
		json_file = file.read()
		dict = json.loads(json_file)
		file.close()

		for fridge in dict['fridges']:
			if fridge['ID'] == fridge_ID:
				for sensor in fridge['sensors']:
					# If the sensor already exist, don't add it
					if sensor['sensor_ID'] == str(added_sensor['sensor_ID']):
						return "Sensor already present"
				# If the sensor doesn't exist, add it to the fridge
				fridge['sensors'].append(
					{'sensor_ID': str(added_sensor['sensor_ID']), 'Value': added_sensor['Value']})

				file = open(self.filename, 'w')
				file.write(json.dumps(dict))
				file.close()

				return "Sensor has been added"
		return "Fridge not found!"

	# Update the value of a sensor, having the fridge_ID
	def update_sensor(self, fridge_ID, added_sensor):
		file = open(self.filename, 'r')
		json_file = file.read()
		dict = json.loads(json_file)
		file.close()

		for fridge in dict['fridges']:
			if fridge['ID'] == fridge_ID:
				for sensor in fridge['sensors']:
					if sensor['sensor_ID'] == str(added_sensor['sensor_ID']):
						sensor['Value'] = added_sensor['Value']

				file = open(self.filename, 'w')
				file.write(json.dumps(dict))
				file.close()

				return "Sensor has been updated"
		return "Fridge not found!"

	# Delete a specified sensor given its ID and the fridge_ID
	def delete_sensor(self, fridge_ID, sensor_del):
		file = open(self.filename, 'r')
		json_file = file.read()
		dict = json.loads(json_file)
		file.close()

		flag = 0
		for fridge in dict['fridges']:
			if fridge['ID'] == fridge_ID:
				for sensor in fridge['sensors']:
					if sensor['sensor_ID'] == str(sensor_del['sensor_ID']):
						fridge['sensors'].remove(sensor)
						flag = 1

				file = open(self.filename, 'w')
				file.write(json.dumps(dict))
				file.close()
				if (flag == 1):
					return "Sensor has been removed"
				else:
					return "Sensor is not present in the fridge!"
		return "Fridge not found!"

###################################### PRODUCTS MANAGEMENT ########################################

	# Get the list of available products in a fridge
	def get_products(self, fridge_ID):
		file = open(self.filename, 'r')
		json_file = file.read()
		dict = json.loads(json_file)
		file.close()

		for fridge in dict['fridges']:
			if (fridge['ID'] == fridge_ID):
				return fridge['products']
		return "Fridge not found!"

	# Add a new product in a specified fridge
	def add_product(self, fridge_ID, added_product):
		file = open(self.filename, 'r')
		json_file = file.read()
		dict = json.loads(json_file)
		file.close()

		for fridge in dict['fridges']:
			if fridge['ID'] == fridge_ID:

				fridge['products'].append(
					{'product_ID': str(added_product['product_ID']), 'brand': str(added_product['brand']), 'Exp_date': {}})

				file = open(self.filename, 'w')
				file.write(json.dumps(dict))
				file.close()

				return "Product has been added"
		return "Fridge not found!"

	# Update a specified product --------> EQUAL TO ADD EXP_DATE
	def update_product(self, fridge_ID, updated_product):
		file = open(self.filename, 'r')
		json_file = file.read()
		dict = json.loads(json_file)
		file.close()

		for fridge in dict['fridges']:
			if fridge['ID'] == fridge_ID:
				for product in fridge['products']:
					if product['product_ID'] == str(updated_product['product_ID']):
						product['Exp_date'] = update_product['Exp_date']

				file = open(self.filename, 'w')
				file.write(json.dumps(dict))
				file.close()

				return "Expiration date of the product has been updated"
		return "Fridge not found!"

	# Delete a speicified product
	def delete_product(self, fridge_ID, del_product):
		file = open(self.filename, 'r')
		json_file = file.read()
		dict = json.loads(json_file)
		file.close()
		flag = 0
		for fridge in dict['fridges']:
			if (fridge['ID'] == fridge_ID):
				for product in fridge['products']:
					if (product['product_ID'] == del_product["product_ID"] and
						product['Exp_date']["day"] == del_product["expiration_date"]["day"] and
						product['Exp_date']["month"] == del_product["expiration_date"]["month"] and
						product['Exp_date']["year"] == del_product["expiration_date"]["year"]):
						flag = 1
						fridge['products'].remove(product)

				file = open(self.filename, 'w')
				file.write(json.dumps(dict))
				file.close()

				if (flag == 1):
					return "Product has been removed"
				else:
					return "Product not found!"
		return "Fridge not found!"

	# Add the expiration date to a product
	def add_expiration(self, fridge_ID, product_ID, added_exp_date):
		file = open(self.filename, 'r')
		json_file = file.read()
		dict = json.loads(json_file)
		file.close()
		for fridge in dict['fridges']:
			if (fridge['ID'] == fridge_ID):
				for product in fridge['products']:
					if (product['product_ID'] == product_ID) and (product['Exp_date']=={}) :
						expiration_date = product['Exp_date']
						expiration_date['day'] = added_exp_date['day']
						expiration_date['month'] = added_exp_date['month']
						expiration_date['year'] = added_exp_date['year']

						file = open(self.filename, 'w')
						file.write(json.dumps(dict))
						file.close()
						return "Expiration date has been added"
				return "Product not found!"
		return "Fridge not found!"

	# Return the expiration date of a specified product
	def get_expiration(self, fridge_ID, product_ID):
		file = open(self.filename, 'r')
		json_file = file.read()
		dict = json.loads(json_file)
		file.close()
		for fridge in dict['fridges']:
			if fridge['ID'] == fridge_ID:
				for product in fridge['products']:
					if (product['product_ID'] == product_ID):
						return product['Exp_date']
				return "Product not found!"
		return "Fridge not found!"

###################################### WASTED PRODUCTS MANAGEMENT ########################################

	# Add a wasted product to a specified fridge
	def add_wasted(self, fridge_ID, wasted_product):
		file = open(self.filename, 'r')
		json_file = file.read()
		dict = json.loads(json_file)
		file.close()

		for fridge in dict['fridges']:
			if fridge['ID'] == fridge_ID:
				for product in fridge['products']:
					if (product['product_ID'] == str(wasted_product['product_ID']) and
						product['Exp_date']["day"] == str(wasted_product['expiration_date']["day"]) and
						product['Exp_date']["month"] == str(wasted_product['expiration_date']["month"]) and
						product['Exp_date']["year"] == str(wasted_product['expiration_date']["year"]) ):

						fridge['wasted'].append(
							{'product_ID': str(wasted_product['product_ID'])})
						# The product has to be eliminated also from the list of those available
						fridge['products'].remove(product)

						file = open(self.filename, 'w')
						file.write(json.dumps(dict))
						file.close()
						return "Wasted product has been added"
				return "Product was not present in the fridge!"
		return "Fridge not found!"

	# Return the list of wasted products in a fridge
	def get_wasted(self, fridge_ID):
		file = open(self.filename, 'r')
		json_file = file.read()
		dict = json.loads(json_file)
		file.close()

		for fridge in dict['fridges']:
			if fridge['ID'] == fridge_ID:
				return fridge['wasted']
		return "Fridge not found!"

###################################### INACTIVE FRIDGE MANAGEMENT ########################################

	# Delete fridges older than an hour
	def remove_inactive_fridge(self):
		actual_time = time.time()
		file = open(self.filename, 'r')
		dict = json.loads(file.read())
		file.close()

		for fridge in dict['fridges']:
			if actual_time - fridge['insert-timestamp'] > 5 * 60:
				dict['fridges'].remove(fridge)
				dict['last_edit'] = actual_time

		file = open(self.filename, 'w')
		file.write(json.dumps(dict))
		file.close()


###################################### WEB SERVICES ########################################

	# Register a new WS on Catalog
	def add_WS(self, added_WS):
		file = open(self.filename, 'r')
		json_file = file.read()
		dict = json.loads(json_file)
		file.close()
		current_time = time.time()
		for WS in dict['web_services']:
			if (WS['name'] == str(added_WS['name'])):
				if (WS['IP'] == str(added_WS['IP'])):
					if (WS['port'] == str(added_WS['port'])):
						WS['insert-timestamp'] = current_time
						file = open(self.filename, 'w')
						file.write(json.dumps(dict))
						file.close()
						return "Web Service already present"
					else:
						WS['port'] = str(added_WS['port'])
						WS['insert-timestamp'] = current_time
						file = open(self.filename, 'w')
						file.write(json.dumps(dict))
						file.close()
						return "Port number has been updated"
				else:
					WS['IP'] = str(added_WS['IP'])
					WS['port'] = str(added_WS['port'])
					WS['insert-timestamp'] = current_time
					file = open(self.filename, 'w')
					file.write(json.dumps(dict))
					file.close()
					return "IP has been updated"

		dict['web_services'].append({'name': str(added_WS['name']),
									'IP': str(added_WS['IP']),
									'port': str(added_WS['port']),
									'insert-timestamp': current_time})
		file = open(self.filename, 'w')
		file.write(json.dumps(dict))
		file.close()
		return "WS has been added"

	# It returns the IP of a specified WS
	def get_ws(self, Name_WS):
		file = open(self.filename, 'r')
		json_file = file.read()
		dict = json.loads(json_file)
		file.close()

		for ws in dict['web_services']:
			if (ws['name'] == Name_WS):
				ip_port = {"IP": str(ws['IP']), "port": str(ws['port'])}
				return ip_port
		return "Web Service not found!"


	# Delete ws older than 5 minutes
	def remove_inactive_ws(self):
		actual_time = time.time()
		file = open(self.filename, 'r')
		dict = json.loads(file.read())
		file.close()

		for ws in dict['web_services']:
			if actual_time - ws['insert-timestamp'] > 60 * 5:
				dict['web_services'].remove(ws)
				dict['last_edit'] = actual_time

		file = open(self.filename, 'w')
		file.write(json.dumps(dict))
		file.close()
