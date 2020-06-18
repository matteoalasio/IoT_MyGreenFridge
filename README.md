## My Green Fridge

### Programming for IoT applications, A.A. 2018-2019

###### Authors:
- Martina Andrulli (s255191)
- Letizia Bergamasco (s263328)
- Stefano Grasso (s242455)
- Piera Riccio (s262849)

###### Description:
My Green Fridge is an Iot platform that offers the possibility to turn a fridge into a smart fridge. With this system, users can have a better control of their fridge and they can improve their impact on the environment, by reducing food waste.\
My Green Fridge offers the following functionalities:
- fridge temperature monitoring;
- fridge humidity monitoring;
- fridge products monitoring;
- user awareness about food waste.

###### System actors and communications:
The system has been developed following a microservices approach. Two communication protocols are exploited: MQTT, based on a publish/subscribe paradigm, and REST, based on a request/response paradigm. A diagram describing all the system actors and communications is available here:
![alt text](https://github.com/letiziabergamasco/IoT_MyGreenFridge/blob/master/UseCaseDiagram.png?raw=true)

The Python scripts corresponding to each microservice are listed below:
- Catalog --> /Catalog/Catalog_REST.py
- Raspberry PI Connector --> /DeviceConnector/DeviceConnectorWS.py
- Temperature Control --> /ControlStrategies/TemperatureWS.py
- Humidity Control --> /ControlStrategies/HumidityWS.py
- Products Control --> /ControlStrategies/ProductsControlWS.py
- Consumption Control --> /ControlStrategies/ConsumptionControlWS.py
- ThingSpeak Adaptor --> /Adaptors/thingspeak_adaptor.py
- Products Adaptor --> /Adaptors/Product_Adaptor.py
- Fridge Status Adaptor --> /Adaptors/FridgeStatusAdaptor.py
- Barcode Conversion Web Service --> /OtherWS/BarcodeConversionWS.py
- Temperature Alarm Web Service --> /OtherWS/TemperatureAlarmWS.py
- Expiration Alarm Web Service --> /OtherWS/ExpirationAlarmWS.py
- Product Input Web Service --> /OtherWS/Product_Input_WS.py
- Product Removal Web Service --> /OtherWS/Product_Output_WS.py
- Freeboard --> /Freeboard/FreeBoard.py
- Telegram Bot --> /TelegramBot.py
