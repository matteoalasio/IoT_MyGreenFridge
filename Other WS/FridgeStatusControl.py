class FridgeStatusControl:
	def __init__(self, status_init, status_curr):
		self.status_init = status_init
		self.status_curr = status_curr
		self.list_status = []
		

	def update_status(self, user_ID, fridge_ID, current_status):
		self.status_curr = current_status
		
		for element in self.list_status:
			if (element['user_ID']==user_ID):
				element['current_status']=current_status
				return self.list_status
		
		self.list_status.append({"user_ID":user_ID, "fridge_ID":fridge_ID, "current_status":current_status})
		print (self.list_status)
		return self.list_status


	def get_status (self):
		return self.status_curr
		

	def get_status_fridge(self, user_ID, fridge_ID):
		for element in self.list_status:
			if (element['user_ID']==user_ID):
				if (element['fridge_ID']==fridge_ID):
					return element['current_status']
		return "User not found!"