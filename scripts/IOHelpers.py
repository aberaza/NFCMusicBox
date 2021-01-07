from gpiozero import LED, Button
import subprocess
import random
import os

from mpdClient import toggleVolume, stop

SOUNDS_PATH = "/usr/local/share/cajaSounds/"


MUSIC_LED = LED(25)
MUSIC_BTN = Button(23)


PLAYER = None

holdCount = 0
def _onHold():
	global holdCount
	print("holding...")
	holdCount += 1
	toggleLed()
	playBeep(2)
	if holdCount > 6:
		doShutdown()
	
def _onRelease():
	global holdCount
	print("released!! holdCount::", holdCount)
	
	if holdCount <= 1:
		switchVolume()
	elif holdCount == 2:
		stopPlayback()
	elif holdCount >= 6:
		doShutdown()
	elif holdCount >= 3:
		doReboot()
		
def _onPress():
	global holdCount
	print("pressed")
	holdCount = 0


def CTRLSetup():
	holdCount = 0
	MUSIC_BTN.when_pressed = _onPress
	MUSIC_BTN.when_released = _onRelease
	MUSIC_BTN.when_held = _onHold
	MUSIC_BTN.hold_repeat = True
	
def CTRLsetPlayer(pl):
	global PLAYER
	PLAYER = pl
	return PLAYER
	
def play(file):
	subprocess.run(["aplay", "-q", file])

def playBeep(type = None):
	if type is None:
		type = random.randint(1, 4)
	play(f"{SOUNDS_PATH}beep{type}.wav")
	
def playHello(type = None):
	if type is None:
		type = random.randint(1, 4)
	play(f"{SOUNDS_PATH}yawaa{type}.wav")
	
def playGoodBye(type = None):
	if type is None:
		type = random.randint(1, 2)
	play(f"{SOUNDS_PATH}oooo{type}.wav")
	
def playError(type=None):
	if type is None:
		type = random.randint(1, 2)
	play(f"{SOUNDS_PATH}error{type}.wav")
	
def doShutdown():
	slowBlink()
	playGoodBye()
	os.system("sudo poweroff")

def doReboot():
	slowBlink()
	playGoodBye()
	os.system("sudo reboot")
	
def switchVolume():
	global PLAYER
	if PLAYER is None:
		return
	toggleVolume(client=PLAYER)
		
def stopPlayback():
	global PLAYER
	if PLAYER is None:
		return
	stop(client=PLAYER)

def slowBlink(led = MUSIC_LED):
	led.blink(0.75, 0.75, None, True)
	
def fastBlink(led = MUSIC_LED):
	led.blink(0.10, 0.10, None, True)

def turnLedOff(led = MUSIC_LED):
	led.off()

def turnLedOn(led = MUSIC_LED):
	led.on()

def toggleLed(led = MUSIC_LED):
	led.toggle()
