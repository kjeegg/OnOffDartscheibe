import serial
import time
from enum import Enum

ARDUINO_PORT = "COM8" #Der Port an welchem Der Arduino via USB angeschlossen ist
BAUD_RATE = 9600 #Die Baud Rate für die Arduino-USB-Serial Verbindnung
SERIAL_TIMEOUT = 3#Der Maximal zulässige Tiemout für die Serielle Verbindung

API_SERVER_DOMAIN = "api.dascr.local"#Die Domain des API-Servers

#-----------------------------
serial_conn = serial.Serial() #Das Objekt für die Serielle Verbindung (wird beim Verbidnugnscheck initialisiert)

#-----------------------------

'''
Liest den Camera Feed der Onboard Camera ein
'''
#Todo: Implement
def readCamera():
	return




'''
Wertet den Camera Feed aus, aka Führt die Bildereknneugn für die Linie aus, und
nuzt die API funktionen 
'''
#Todo: Implement
def evaluateCameraFeed():
	return


'''
Schcikt den Camera Feed an den API Server
'''
#Todo: Implement
def sendCameraFeed():
	return



#-----------------------------

'''
Schaltet den angeschlossenden LED Strip
'''
#Todo: Implement
def enableLEDs():
	return



#-----------------------------


'''
Empfängt Daten vom API Server
'''
#Todo: Implement
def recvFromApiServer():
	return


'''
Sendet einen Request an die API
'''
#Todo: Implement
def sendToAPIServer():
	return


#--------------------------------

'''
Sendet einen Request an den Arduino via USB Serial
'''
#Todo: Implement
def sendArduino():
	return

'''
Empfängt Daten vom Arduino via USB Serial
'''
#Todo: Implement
def recvArduino():
	return





class AruinoState(Enum):
	INIT = 0
	THROW = 1
	NEXT_PLAYER = 2
	MOTION_DETECTED = 3
	RESET_ULTRASONIC = 4
	WON = 5
	CONNECTED = 9


'''
Überträgt die Konfigurationsinformationen für den Arduino
'''
def configureArduino():
	'''
	Commandos:
		p == piezo threshold
		u == debounce wobble time
		b == Schalted den Button ein/aus
			0 == aus
			1 == ein
		s == new game state aka Spielzustand wechseln
			1==TRHOW
			2==Nextplayer
			3==Motion Detected
			4==Reset Ultrasonic
			9==Service Connected
	'''
	return

'''
Interpretiert eine erhaltene Serial Nachricht vom Arduino
'''
def evalArduinoMsg(arduinoMsg):
	print("ARDUINO: " + arduinoMsg)
	valide_Nachrichten = (
		"b",
		"m",
		"u"
	)

	if arduinoMsg in valide_Nachrichten or arduinoMsg.isnumeric(): #Prüfe ob die Empfangende Information ein valide Nachricht
		if arduinoMsg.isnumeric(): #Es wird ein Zahlenwert empfangen
			#Todo Implement
			None
		else: #Es Wurde ein/e Befehl/Information empfangen
			match arduinoMsg:
				case "b": #Der Button wurde gedrückt
					#Todo Implement
					None
				case "m": #Ein Fehlwurf wurde festgestellt
					#Todo Implement
					None
				case "u": #Die Distanz laut Ultraschall ist zu groß
					#Todo Implement
					None
	else:
		print("INFO: Arduino - Es wurde eine invalide Nachricht vom Arduino empfangen")
	return

'''
Stellt den Überliegenden Process für die Arduino - API Kommunikation dar.
Aka liest die Daten des Arduinos aus, und leited diese an die API weiter
'''
def arduinoSchnittstelle():
	try:
		while True:
			if serial_conn.in_waiting > 0: #Es kommen Daten auf der Verbidnung an
				arduinoMsg = serial_conn.readline().decode().strip()#Einlesen, Bytecode umwandeln, + extrazeichen entfernen
				evalArduinoMsg(arduinoMsg)
	except serial.serialutil.SerialException:
			print("ERROR: Die Verbindung zum Arduino wurde unterbrochen")
	return

#--------------------------------


'''
Prüft ob alle nötigen Componenten vorhanden sind
- Prüft ob Verbindung zum API Server möglich
- Prüft ob Verbindung zum Arduino besteht
- Prüft ob Camera Modul reagiert
'''
def checkConnections():
	#Todo: Implement
	try:
		serial_conn.open()#Baut eine Serielle Verbindung mit dem Arduino auf
		time.sleep(1)#Warted 1ne Sekunde für den Verbindungsaufbau
		print("INFO: Prüfe Arduino Serial Verbindung...")
	except serial.serialutil.SerialException:
		print("ERROR: Es konnte keine Serielle Verbindung zum Arduino aufgebaut werden. Bitte Prüfen Sie, ob sie den Korrekten Port angegeben haben")
		return False
	return True


def main():
	print("INFO: Starte OnOffDart-Service")

	#Einstellungen für die Serielle Verbindung zum Arduino
	serial_conn.baudrate = BAUD_RATE
	serial_conn.port = ARDUINO_PORT
	serial.timeout = SERIAL_TIMEOUT

	if checkConnections():
		print("INFO: Alle Komponenten scheinen erreichbar zu sein. Setze Fort")
		arduinoSchnittstelle()
	else:
		print("ERROR: Es gab ein Problem bei einer der Komponenten, das Program kann so leider nicht fortfahren.")
	return


main()