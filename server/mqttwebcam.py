#!/usr/bin/python


# listens on mqtt, returns base64 encoded webcam image on mqtt, see webclient for democlient


import cv2
import base64
import mosquitto as mqtt
import sys
import time


#mqtt settings
MQTT_HOST = '192.168.140.30'
MQTT_PORT = 1883
MQTT_BASE_TOPIC = 'mik/webcam'

#camera settings
camera = 0
dummyframes = 10
old_time = 0
minimal_wait = 5

webcam = cv2.VideoCapture(camera)

def get_single_image():
   retval, im = webcam.read()
   return im


def on_connect(mosq,obj,rc):
   sys.stderr.write ('Connected with result code:' + str(rc) + ' to ' + MQTT_HOST + '\r\n')  
  
   # Subscribing in on_connect() means that if we lose the connection and  
   # reconnect then subscriptions will be renewed.  
   client.subscribe(MQTT_BASE_TOPIC)  
   sys.stderr.write ('Listening on ' + MQTT_BASE_TOPIC + '\r\n')  


# The callback for when a message is received from the server.  
def on_message(client, userdata, msg):  
	global old_time
	sys.stderr.write ('Received message:' + str(msg.payload) + ' on: ' + MQTT_BASE_TOPIC + '\r\n')  

	epoch_time = int(time.time())

	if ((old_time + minimal_wait) <= epoch_time):
		#boot camera with dummyframes
		for i in xrange(dummyframes):
		   get_single_image()

		camera_capture = get_single_image()
		resized_camera_capture = cv2.resize(camera_capture, (100, 50)) 
		retval, data =  cv2.imencode('.jpeg', resized_camera_capture)
		client.publish(MQTT_BASE_TOPIC+'/image', base64.b64encode(data.tostring()),qos=0,retain=True)
		client.publish(MQTT_BASE_TOPIC+'/time', epoch_time,qos=0,retain=True)
		sys.stderr.write ('Published message to :' + MQTT_BASE_TOPIC + '/image\r\n')  
		old_time = epoch_time

client = mqtt.Mosquitto()  
client.on_connect = on_connect  
client.on_message = on_message  
  
client.connect(MQTT_HOST, MQTT_PORT, 60)  
  
# Blocking call that processes network traffic, dispatches callbacks and  
# handles reconnecting.  
# Other loop*() functions are available that give a threaded interface and a  
# manual interface.  
client.loop_forever()  

del(webcam)
