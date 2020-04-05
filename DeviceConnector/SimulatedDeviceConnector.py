import time
import pybase64
import socket

class DeviceConnector(object):
    
    # constructor
    def __init__(self, ip, port, userID, fridgeID, temperatureID, humidityID, camera0ID, camera1ID):

        # IP and port
        self.ip = ip
        self.port = port
        
        self.userID = userID
        self.fridgeID = fridgeID
        self.temperatureID = temperatureID
        self.humidityID = humidityID
        self.camera0ID = camera0ID
        self.camera1ID = camera1ID


    def get_temperature(self):
        """retrieve temperature value from sensor DHT22 and return a senml with the temperature"""
        # retrieve humidity and temperature from sensor DHT22
        humidity = 22
        temperature = 20
        bn = "http://" + self.ip + "/Tsensor/" # base name
        n = "temperature" # resource name
        u = "Celsius" # units
        t = time.time() # timestamp
        
        if temperature is not None:
            v = temperature # value
        else:
            v = "Reading error"
        
        Tsenml = {"bn": bn, "e": [{ "n": n, "u": u,"t": t, "v": v}]}
        print ("Temperature is: " + str(v) + " Celsius")
        return Tsenml
    
    def get_humidity(self):
        """retrieve humidity value from sensor DHT22 and return a senml with the humidity"""
        # retrieve humidity and temperature from sensor DHT22
        humidity = 22
        temperature = 20
        
        bn = "http://" + self.ip + "/Hsensor/" # base name
        n = "humidity" # resource name
        u = "%" # units
        t = time.time() # timestamp
        
        if humidity is not None:
            v = humidity # value
        else:
            v = "Reading error"
        
        Hsenml = {"bn": bn, "e": [{ "n": n, "u": u,"t": t, "v": v}]}
        print ("Humidity is: " + str(v) + " %")
        return Hsenml
    
    def get_camera0(self):
        """retrieve an image from the camera0 and return it in a senml"""

        
        with open("camera0image.jpg", "rb") as image_file:
            # base64 encoding
            image_base64 = pybase64.b64encode(image_file.read())
            image_base64 = image_base64.decode() # convert bytes into string
            
        bn = "http://" + self.ip + "/Camera0/" # base name
        n = "camera0" # resource name
        u = "base64" # units
        t = time.time() # timestamp
        
        if image_base64 is not None:
            v = image_base64 # value
        else:
            v = "Reading error"
        
        C0senml = {"bn": bn, "e": [{ "n": n, "u": u,"t": t, "v": v}]}
        print ("Image captured from Camera0")
        return C0senml
        
    
    def get_camera1(self):
        """retrieve an image from the camera1 and return it in a senml"""
        
        
        with open("camera1image.jpg", "rb") as image_file:
            # base64 encoding
            image_base64 = pybase64.b64encode(image_file.read())
            image_base64 = image_base64.decode() # convert bytes into string
            
        bn = "http://" + self.ip + "/Camera1/" # base name
        n = "camera1" # resource name
        u = "base64" # units
        t = time.time() # timestamp
        
        if image_base64 is not None:
            v = image_base64 # value
        else:
            v = "Reading error"
        
        C1senml = {"bn": bn, "e": [{ "n": n, "u": u,"t": t, "v": v}]}
        print ("Image captured from Camera1")
        return C1senml
    
    
if __name__ == '__main__':
    
    # get IP address of the RPI
    s = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    ip = s.getsockname()[0] # "192.168.1.128"
    
    userID = "1234"
    fridgeID = "5678"
    temperatureID = "12"
    humidityID = "12"
    camera0ID = "34"
    camera1ID = "56"
    dev = DeviceConnector(ip, userID, fridgeID, temperatureID, humidityID, camera0ID, camera1ID)
    dev.get_temperature()
    dev.get_humidity()
    dev.get_camera0()
    dev.get_camera1()