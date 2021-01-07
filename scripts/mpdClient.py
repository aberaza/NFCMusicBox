#!/usr/bin/env python
from mpd import MPDClient
#from readtest import *
import re
#from CardList import CardList
#from Reader import Reader
#import sys

CLIENT = None

def connectMPD(host="localhost", port=6600):
	global CLIENT
	try:
		client = MPDClient()               # create client object
		client.timeout = 200
		client.idletimeout = None
		# client.use_unicode = True No es necesario y peta!
		print (f"Connecting $host:$port...")
		client.connect(host, port) 
		CLIENT = client
		print("Connected!")
		return client
	except Exception as e:
		print('Could not connect to MPD server')
		print(e)

def stop(client=CLIENT):
	try:
		client.stop()
		client.clear()
	except:
		print('Could not stop player')

def play(url, client = CLIENT):
	stop(client)
	try:
		client.add(url)
		client.play()
	except:
		print(f"Can't play playlist $url")


def toggleVolume(amount=15, max = 95, min=5, client=CLIENT):
	newVolume = int(client.status()['volume']) + amount
	if newVolume > max:
		newVolume = min
	client.setvol(newVolume)
	return newVolume

def __init__(self):
	if client is None:
		client = connectMPD()
	
	print(client.status())
	play("spotify:track:0cKk8BKEi7zXbdrYdyqBP5", client)

