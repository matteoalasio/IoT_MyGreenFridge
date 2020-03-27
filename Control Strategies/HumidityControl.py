class HumidityControl:

	def __init__(self, h_init, h_curr):
		self.h_init = h_init
		self.h_curr = h_curr
		print("Init complete")

	#Change the value of current temperature
	def get_init_humidity(self):	
		return self.h_init

	def get_humidity(self):
		return self.h_curr

	#Check the current temperature
	def hum_check(self, h_curr):
	
		self.h_curr = int(h_curr)

		h_high_lim =  50 #50% of humidity is considered as the highest humidity in the fridge
		h_low_lim = 10 #10% of humidity is considered as the lowest humidity in the fridge

		if (self.h_curr>=h_high_lim):
			return 1

		if (self.h_curr<=h_low_lim):
			return -1

		return None