import cherrypy
import json
import threading
import requests
import sys
from pyzbar.pyzbar import decode
import cv2

class BarcodeConversionREST(object):
    
    # expose the Web Services
    exposed = True

    def __init__(self):
        pass

    def GET (self, *uri, **params):
        if (len(uri)!=1):
            raise cherrypy.HTTPError(404, "Error: wrong number of uri")
        # /product?EAN=<ean>
        elif (uri[0] == "product"):
            ean = params["EAN"]
            jsonProduct = self.get_product_brand(ean)
            return jsonProduct

    def POST (self, *uri, **params):
        pass
        return

    def PUT (self, *uri, **params):
        pass
        return

    def DELETE(self):
        pass
        return
    
    def get_product_brand(self,ean):
        # build url to access info about the product on website "world.openfoodfacts.org"
        url = "https://it.openfoodfacts.org/api/v0/product/{}.json".format(ean)
        data = requests.get(url).json()
        if data["status"] == 1:
            # get all the info about the product in json format
            product = data["product"]
            # retrieve only the product's name and brand
            product_name = product["product_name"]
            brand = product["brands"]
        else:
            product_name = None
            brand = None
        
        dictOutput = {"product": product_name, "brand": brand}
        jsonOutput = json.dumps(dictOutput)
        return jsonOutput




if __name__ == '__main__':
    
    
    # standard configuration
    conf = {
        '/': {
            'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
            'tools.sessions.on': True
        }
    }

    devPort = 8080

    #filename = "barcode_image.jpg"
    #img = cv2.imread(filename)
    #gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    #barcodes = decode(gray_img)
    
    #print(barcodes)
    #
    ## this prints:
    # [Decoded(data=b'8076809531191',
    # type='EAN13',
    # rect=Rect(left=419, top=115, width=240, height=122),
    # polygon=[Point(x=419, y=153), Point(x=419, y=235), Point(x=536, y=237),
    #           Point(x=659, y=236), Point(x=659, y=148), Point(x=658, y=116),
    #           Point(x=536, y=115), Point(x=420, y=115)])]

    
    # deploy the DeviceConnectorREST class and start the web server
    cherrypy.tree.mount(BarcodeConversionREST(), '/', conf)
    cherrypy.config.update({'server.socket_host': '0.0.0.0'})
    cherrypy.config.update({'server.socket_port': devPort})
    cherrypy.engine.start()
    cherrypy.engine.block()