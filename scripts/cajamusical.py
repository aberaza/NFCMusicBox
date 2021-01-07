import time
import binascii

# import ndef
from pn532pi import Pn532, pn532
from pn532pi import Pn532I2c

import mpdClient
from IOHelpers import *

PN_532_I2C = Pn532I2c(1)
nfc = Pn532(PN_532_I2C)

KEY_ZERO = bytearray([0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
KEY_DEFAULT = bytearray([0xA0, 0xA1, 0xA2, 0xA3, 0xA4, 0xA5])
KEY_UNIVERSAL = bytearray([0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF])

NDEF_SECTOR1 = bytearray([0x14, 0x01, 0x03, 0xE1, 0x03, 0xE1, 0x03, 0xE1, 0x03, 0xE1, 0x03, 0xE1, 0x03, 0xE1, 0x03, 0xE1])
NDEF_SECTOR2 = bytearray([0x03, 0xE1, 0x03, 0xE1, 0x03, 0xE1, 0x03, 0xE1, 0x03, 0xE1, 0x03, 0xE1, 0x03, 0xE1, 0x03, 0xE1])

def setupNFC():
	ready = False
	while not ready :
		nfc.begin()
		versiondata = nfc.getFirmwareVersion()
		if not versiondata:
			print("Can't connect, retry in 5 sec")
			time.sleep(5)
			#raise RuntimeError("Didn't find PN532 board")
			continue
		nfc.SAMConfig()
		ready = True
	print("NFC532 Reader up")
	return True
	
def setupIO(mpdClient):
	CTRLsetPlayer(mpdClient)
	CTRLSetup()


def setupMPD():
	client = None
	while client is None :	
		client =  mpdClient.connectMPD()
		time.sleep(1)
	#client.setvol(40)
	return client


def getCardID(card_type = pn532.PN532_MIFARE_ISO14443A_106KBPS):
	isCard, uid = nfc.readPassiveTargetID(card_type)
	if not isCard:
		raise Exception("Card Not Found/Readable")
	return uid

def readBlock(uid, block=0, keya = KEY_ZERO):
	auth = nfc.mifareclassic_AuthenticateBlock(uid, block, 1, keya)
	if not auth:
		raise Exception(f"Can't authenticate block {block}")
	success, data = nfc.mifareclassic_ReadDataBlock(block)
	if not success:
		raise Exception(f"Can't read block {block}")
	return data

def readBlockLight(block):
	s, data = nfc.mifareultralight_ReadPage(block)
	if not s:
		raise Exception(f"Can't read block {block}")
	return data

def isNDEF(uid, key = KEY_UNIVERSAL):
	isNDEF = True
	try:
		reg1 = readBlock(uid, 1, key)
		reg2 = readBlock(uid, 2, key)
        
		
		for r1, r2, n1, n2 in zip(reg1, reg2, NDEF_SECTOR1, NDEF_SECTOR2):
			if r1 != n1 or r2 != n2:
				#return False
				raise ValueError("Not NDEF")
	except:
		isNDEF = False
	return isNDEF	

def getKeys(uid, key = KEY_UNIVERSAL):
	try:
		reg3 = readBlock(uid, 3, key)
		return (reg3[:6], reg3[10:])
	except:
		return KEY_UNIVERSAL
	
def _dumpMifare(uid, keya):
	if not isNDEF(uid, keya):
		raise ValueError("Not Valid NDEF format card")
	
	# key_a, key_b = getKeys(uid)
	bl = 4
	
	keepReading = not nfc.mifareclassic_IsFirstBlock(bl)
	# Find first block
	while(bl < 64 and keepReading):
		bl += 1
		keepReading = not nfc.mifareclassic_IsFirstBlock(bl)
		
	fb = readBlock(uid, bl, KEY_UNIVERSAL)
	payloadLength = fb[3]
	idLength = fb[5]
	payloadType = fb[7]
	payloadId =  fb[8]
	
	print(f"payloadLength {payloadLength}, idLength {idLength}, payloadType {payloadType}")
	print(f"Card contains {payloadLength} bytes") 
	print(fb)
	loadType = fb[5]
	dataNFC = fb[5:]
	print("\n\n", fb, "\n\n")
	while(bl < 64 and len(dataNFC) < payloadLength):
		bl+=1
		print(f"We have {len(dataNFC)} so far") 
		try:
			data = readBlock(uid, bl, KEY_UNIVERSAL)
			print(data)
		except:
			print(f"Could not read block {bl}")
			data = None
		finally:	
			if data is not None:
				dataNFC += data
			
	return (loadType, dataNFC[4:payloadLength - 1])
	##message = ndef.NdefMessage(binascii.hexlify(bytearray(dataNFC)))

def _dumpUltraLight():
	print("Read ultralight")
	success, data = nfc.mifareultralight_ReadPage(4)
	print("Read page 4 was ", success, data)
	try:
		bl = 4
		d1 = readBlockLight(bl)
		bl+=1
		d2 = readBlockLight(bl)
		bl+=1
	except:
		print("Can't read extra data")
		return None
		
	dataLength = d1[1]
	idLength = d1[3]
	dataType = d2[1]
	dataNFC = d2[2:]
	print(f"payloadLength {dataLength}, idLength {idLength}, payloadType {dataType}")
	
	blockRetry = 0
	while(bl < 64 and len(dataNFC) < dataLength and blockRetry < 3):

		try:
			data = readBlockLight(bl)
			if data is  not None:
				dataNFC += data
			bl += 1
			blockRetry = 0
		except:
			print(f"Could not read block {bl}")
			blockRetry +=1
			time.sleep(0.1)
				
		
	print("RAW DATA:: ", dataNFC)
	print("TRIMMED DATA:: ", dataNFC[1:dataLength - 4])
	return (dataType, dataNFC[1:dataLength - 4])
	
def dumpCard(card_type = pn532.PN532_MIFARE_ISO14443A_106KBPS, keya = KEY_ZERO):
	uid = getCardID(card_type)
	fastBlink()
	
	print("LENGTH OF UID = ", len(uid))
	if len(uid) == 4: # Normal card, mifare
		return _dumpMifare(uid, keya)
	elif len(uid) == 7: # Ultralight
		return _dumpUltraLight()
	else:
		return None
	

def readCard(card_type = pn532.PN532_MIFARE_ISO14443A_106KBPS, key = None):
	try:
		loadType, payload = dumpCard(card_type, key)
	except Exception as e:
		print("Ooops: ", e)
		return None
		
	print(f"GOT type {loadType} with payload:\n {payload.decode('utf-8')}")
	#print("load type ", loadType)	
	url = payload.decode('utf-8')
	turnLedOff()
	'''
	
	if loadType == 33: # TODO: file:// cambiar 33 por el valor real... magicnumbers
		payload = "file://" + payload
	elif loadType == 85: # %U -> URN formato libre, no tocar
		pass
	else : # Por defecto tampoco hacemos nada
		pass
	'''
	return url
		

if __name__ == '__main__':
	# SLOW blink LED
	slowBlink()
	setupNFC()
	#client = mpdClient.connectMPD()
	client = setupMPD()
	setupIO(client)
	time.sleep(2)
	turnLedOn()
	playHello()
	print("Starting infinite loop!")
	while True:
		#if client == None:
		#	client = mpdClient.connectMPD()
		#	time.sleep(1)
		#elif client.status()['error']:
		#	print("MPD ERROR:\n", client.status()['error'])	
		#else:
			#url = dump(keya=KEY_UNIVERSAL)
		turnLedOn()
		url = readCard(key = KEY_UNIVERSAL)
		if url is not None:
			mpdClient.play(url, client)
			playBeep()
		time.sleep(5)

