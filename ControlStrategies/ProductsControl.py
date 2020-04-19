import pybase64
from pyzbar.pyzbar import decode
import io
import numpy as np    
from PIL import Image
import cv2

class ProductsControl:

	def __init__(self, initialImageString):

		self.imageString = initialImageString

	def updateImage(self, imageString):

		self.imageString = imageString
		print("Image updated!")

	def imageToEan(self, imageString):

		# base64 decoding
		
		imageBytes = imageString.encode() # convert string into bytes
		imagePIL = Image.open(io.BytesIO(imageBytes))
		imageArray = np.asarray(imagePIL)

		grayImage = cv2.cvtColor(imageArray, cv2.COLOR_BGR2GRAY)
		barcodes = decode(grayImage)
		
		if len(barcodes) == 1:
			EANcode = barcodes[0].data
		else:
			EANcode = None #??

		print(EANcode)
		time.sleep(10)
		return EANcode
