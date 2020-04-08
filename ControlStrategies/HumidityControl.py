class HumidityControl:

    def __init__(self, h_init, h_curr):
        self.h_init = h_init
        self.h_curr = h_curr
        print("Init of Humidity Controller is concluded")

    #Change the value of current temperature
    def get_init_humidity(self):
        return self.h_init

    def get_humidity(self):
        return self.h_curr

    def update_init_humidity (self, h_curr):
        self.h_init = h_curr
        return self.h_init

    def update_humidity(self, h_curr):
        self.h_curr = h_curr
        return self.h_curr

    #Check the current humidity
    def hum_check(self, h_curr):
        self.h_curr = int(h_curr)

        h_high_lim = 50 #50% is considered as the highest humidity in the fridge
        h_low_lim = 10 #10% is consideres as the lowest humidity in the fridge

        if (self.h_curr>=h_high_lim):
            return 1

        if (self.h_curr<=h_low_lim):
            return -1

        return None
