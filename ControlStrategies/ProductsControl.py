import pybase64
from pyzbar.pyzbar import decode
import io
import numpy as np    
from PIL import Image
import cv2
import pybase64


class ProductsControl:

	def __init__(self, initialImageString):

		self.imageString = initialImageString

	def getImage(self):

		return self.imageString

	def updateImage(self, imageString):

		self.imageString = imageString
		print("Image updated!")

	def imageToEan(self, imageString):

		# base64 decoding
		imageBytes = pybase64.b64decode(str(imageString))
	
		imagePIL = Image.open(io.BytesIO(imageBytes))

		imageArray = np.asarray(imagePIL)

		grayImage = cv2.cvtColor(imageArray, cv2.COLOR_BGR2GRAY)
		barcodes = decode(grayImage)
		
		if len(barcodes) == 1:
			EANBytes = barcodes[0].data
			EANcode = EANBytes.decode() # convert bytes into string
		else:
			EANcode = None #??

		print("EAN code is: " + str(EANcode))

		return EANcode
