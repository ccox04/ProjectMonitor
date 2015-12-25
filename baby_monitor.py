#!/usr/bin/env python
# Created by: Chris Cox
# Baby Motion Monitor Texting Camera
# Credit goes to: 
# Description: Created a program that uses break beam LEDs to detect movement.
# It then relays the detection to the camera pi to take a snap shot.
from PIL import Image, ImageFilter, ImageChops
from twilio.rest import TwilioRestClient
import RPi.GPIO as GPIO
import picamera
import math, operator
import time
import socket
import requests

GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)
motion_sensor_pin = 24
GPIO.setup(motion_sensor_pin, GPIO.IN)

LED = 18
#Set up output LED indicators
GPIO.setup(motion_LED_pin, GPIO.OUT)

camera = picamera.PiCamera()

client = TwilioRestClient(account='ACe3446369fe6f831be04eae238e9bdfa8', token='67fef0ff1be5813a0a162b22200ae2b7')

def sendMessage():
	client.messages.create(to='+15407974693', from_='+15406135061', body="Carleigh is Moving!", media='orig.jpg')
	print('Just ran sendMessage', client)


# This function will be run in the thread.
def motionSensor():
	while True:
		#Update sensor and LED states each loop
		motion = GPIO.input(motion_sensor_pin)
		GPIO.output(motion_LED_pin, motion)
			
		is_active = [False] # It's a list because it'll get passed to the thread by reference this way, not by value.
		# If we just passed False as an argument, changing the local variable here wouldn't change the thread's variable.
		flashthread = Thread(target=flash, args=(is_active,))
		flashthread.daemon = True
		flashthread.start() # start the thread

		if motion:
			is_active[0] = True # Takes a Picture
		else:
			is_active[0] = False # Does Not take a Picture
		
		time.sleep(0.01)

def snapImage(is_active):
	while True:
		if len(is_active) == 0: # empty list means exit, for our purposes
			GPIO.output(LED,GPIO.LOW) # Turn off LED
			break # jump out of this infinite while loop and exit this thread
		if is_active[0]:
			print('Infinite while')
			camera.capture('dump.jpg')
			time.sleep(3)
			camera.capture('orig.jpg') 
			time.sleep(3)
			camera.capture('update.jpg') #capture new image whenever there is a change

			img1 = Image.open('orig.jpg')
			img2 = Image.open('update.jpg')

			print ("Captured Images")

			toSend = img2.resize((400, 400), Image.ANTIALIAS)
			toSend.save('latest.png')
			sendMessage()
		time.sleep(1)
def main():
	try:
		motionSensor()
	except KeyboardInterrupt:
			is_active.remove(0) # Turns the flashing off
			GPIO.cleanup()

if __name__ == '__main__':
	main()
