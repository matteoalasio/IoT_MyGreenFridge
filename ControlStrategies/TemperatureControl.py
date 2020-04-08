class TemperatureControl:

	def __init__(self, t_init, t_curr):
		self.t_init = t_init
		self.t_curr = t_curr
		print("Init of Temperature Controller is concluded")

	#Change the value of current temperature
	def get_init_temperature(self):
		return self.t_init

	def get_temperature(self):
		return self.t_curr

	def update_init_temperature (self, t_curr):
		self.t_init = t_curr
		return self.t_init

	def update_temperature(self, t_curr):
		self.t_curr = t_curr
		return self.t_curr

	#Check the current temperature
	def temp_check(self, t_curr):
		self.t_curr = int(t_curr)

		t_high_lim = 6 #6 degrees are considered as the highest temperature in the fridge
		t_low_lim = 1 #1 degree is considered as the lowest temperature in the fridge

		if (self.t_curr>=t_high_lim):
			return 1

		if (self.t_curr<=t_low_lim):
			return -1

		return None
