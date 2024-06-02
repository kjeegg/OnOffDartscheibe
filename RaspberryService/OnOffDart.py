import serial
import time
import re
import requests
import threading
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import json

ARDUINO_PORT = "COM8" #Der Port an welchem Der Arduino via USB angeschlossen ist
BAUD_RATE = 9600 #Die Baud Rate für die Arduino-USB-Serial Verbindnung
SERIAL_TIMEOUT = 3#Der Maximal zulässige Tiemout für die Serielle Verbindung

API_SERVER_DOMAIN = "https://api.dascr.local/api"#Die Domain des API-Servers

#-----------------------------
serial_conn = serial.Serial() #Das Objekt für die Serielle Verbindung (wird beim Verbidnugnscheck initialisiert)
last_game_State = None #Speichert den lezten gefechten Spielzustand

requests.packages.urllib3.disable_warnings(InsecureRequestWarning) #Schaltet TLS warnungen aus
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


#Repräsentiert den aktuellen Gamestate
class Gamestate:
	#Todo: Implement 
	def __init__(self, p_uid, p_Game, p_player, p_Variant, p_In, p_Out, p_ActivePlayer, p_ThrowRound, p_Gamestate, p_Settings, p_UndoLog, p_Podium):
		self.uid = p_uid 
		self.Game = p_Game
		self.player = p_player
		self.Variant = p_Variant
		self.In = p_In
		self.Out = p_Out
		self.ActivePlayer = p_ActivePlayer
		self.ThrowRound = p_ThrowRound
		self.GameState = p_Gamestate
		self.Settings = p_Settings
		self.UndoLog = p_UndoLog
		self.Podium = p_Podium


'''
Vergleicht den lezten Gespeicherten Spielstand, mit dem neu gefechten

Bei Änderungen werden diese Automatisch umgesezt

@param newGameState ein neuer Gamestate der zum Vergleich genuzt wird

'''
def checkGamestateDiff(newGameState):
	'''
	TODO: Implement
	'''

	return



'''
Ermittelt den Gamestate für das aktuelle Spiel von der API. Und sezt alle Parameter entsprechend
Nötig, da der Pi ja nicht bei Änderungen durch das Frontend im Backend informiert wird.
Daher ist eine Regelmässige Abfrage nötig um den aktuellen Spielstand zu ermitteln.
Es muss angenommen werden, dass neuste erstellte Spiel das aktuell laufende ist
'''
def getGamestate():
	while 1:
		try:
			spiele_request = requests.get(API_SERVER_DOMAIN + "/game", verify=False)#Lese lisste aller Spiele aus
			spiele = (spiele_request.text).strip()
			'''
			Todo:
				- Extrahiere aktuellstes Spiel (lezter Eintrag im JSON)
				- Lese die entsprechenden Daten aus speicehr in nem GameState Objekt, und vergleiche mit leztem Gamestate
				- Bei Gamestate änderungen oder gar nem Neuen Spiel, aktualisiere (falls nötig für den Arduino etc)
			'''
			if spiele == "null":
				print("WARNING: API - Es wurde noch kein Spiel erstellt - Gameupdate nicht möglich")
			else: #Es wurden Spiele Gefunden
				json_data = json.loads(spiele_request.text)
				#print(json.dumps( json_data[len(json_data)-1] ,indent=4))

				#identifiziere das neuste Spiel, aka das mit höchster uid
				max_uid = 0
				max_index = 0
				for i in range(len(json_data)):
					if int(json_data[i].get('uid')) > max_uid:
						max_uid = int(json_data[i].get('uid'))
						max_index = i


				last_game = json_data[max_index]#Der lezte Datensatz. ACHTUNG muss noch geändert werden, da dieser lieder nicht automatisch das neuste Spiel ist

				uid = last_game.get('uid')
				game = last_game.get('game')
				player = last_game.get('player')
				variant = last_game.get('variant')
				In = last_game.get('in')
				Out = last_game.get('out')
				activePlayer = last_game.get('GameObject').get('Base').get('ActivePlayer')
				throwRound = last_game.get('GameObject').get('Base').get('ThrowRound')
				gameState = last_game.get('GameObject').get('Base').get('GameState')
				settings = last_game.get('GameObject').get('Base').get('Settings')
				undoLog = last_game.get('GameObject').get('Base').get('UndoLog')
				podium = last_game.get('GameObject').get('Base').get('Podium')
				game = Gamestate(uid,game,player,variant,In,Out,activePlayer,throwRound,gameState,settings,undoLog,podium)

				#for attr, value in vars(game).items():#Zum prüfen des Objekte
					#print(f"{attr}: {value}")
				global last_game_State
				if last_game_State is not None:# Dürfte nur beim aller ersten Fetch None sein (da da noch kein Objekt gelesen wurde)
					None;
				else:
					last_game_State = game #Setzte den Initialen Gamestate
		except requests.exceptions.ConnectionError:
			print("ERROR: API - Scheinbar ist die Verbindung zur API abgebrochen")
		time.sleep(3)#Wartet 3 Sekunden bis zur nächsten Gamestate Prüfung
	return


#--------------------------------


# Einfach nurn dictionary zur Schöneren Ausgabe der Empfangenden Werte
dict_punkte = {
	"1" : 'single',
	"2" : 'double',
	"3" : 'tripple',
	"25": 'bull'
}

'''
Interpretiert eine erhaltene Serial Nachricht vom Arduino. Und passt entsprechend alles nötige an
aka Aktualisiert den Gamestate lokal, und sendet auch falls nötig die Daten an die API

@param arduinoMsg die auszuwertende Nachricht
'''
def evalArduinoMsg(arduinoMsg):
	if arduinoMsg.isnumeric(): #Es wird ein Zahlenwert empfangen
		if(len(arduinoMsg) == 3 and int(arduinoMsg[0]) < 4 and int(arduinoMsg[0]) >= 0):#Gültige Punktezahl empfangen
			modifier = dict_punkte.get(arduinoMsg[0])#Der Empfangende Modifier (1=single, 2=double, 3=triple)
			wert = dict_punkte.get(str(arduinoMsg[1:3]), arduinoMsg[1:3])#Wenn der Wer 25 -> Bull ansonsten schreib einfach den Wert
			if wert != "bull":#Convertiere den Wert in nen Korrekten Integer wenns kein bullseye war
				wert = str(int(wert)) #Einfach nur in int converten damits sinvoll gesliced ist. Wird aber als String weiterverwendet
			print(f"INFO: Arduino - Empfangende Punktzahl: {modifier} {wert}")

			'''
				Todo:
					Benutze den Empfangenden wert um: 
						a) den Gamestate zu aktualisieren
						b) Die Daten an die API zu senden
			'''
			

			#a) Aktualisierung des Gamestates
				#Todo Implement

			#b) Sende Daten an API
				#Todo Implement
			None

		else:
			print("WARNING: Arduino - Es wurde eine invalide Punktezahl vom Arduino empfangen: " + arduinoMsg)
	elif arduinoMsg == "m": #Es wurde ein Fehlwurf Festgestellt
		print("INFO: Arduino - Es wurde ein Fehlwurf vom Arduino Festgestellt")
		'''
			Todo:
				sende die Entsprechende information über den Fehlwurf an die API
		'''
		None
	else:
		print("WARNING: Arduino - Es wurde eine invalide Nachricht vom Arduino empfangen: " + arduinoMsg)
	return


'''
Stellt den Überliegenden Process für die Arduino - API Kommunikation dar.
Aka liest die Daten des Arduinos aus, und verarbeited diese entsprechend
'''
def arduinoSchnittstelle():
	try:
		while True:
			if serial_conn.in_waiting > 0: #Es kommen Daten auf der Verbindnung an
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
	print("INFO: Prüfe Arduino Serial Verbindung...")
	try:
		serial_conn.open()#Baut eine Serielle Verbindung mit dem Arduino auf
		time.sleep(1)#Warted 1ne Sekunde für den Verbindungsaufbau
		print("INFO: Serielle Verbindung zum Arduino aufgebaut!")
	except serial.serialutil.SerialException:
		print("ERROR: Es konnte keine Serielle Verbindung zum Arduino aufgebaut werden. Bitte Prüfen Sie, ob sie den Korrekten Port angegeben haben")
		return False

	print("INFO: Prüfe API Server Verbindung...")
	try:
		req = requests.get(API_SERVER_DOMAIN, verify=False)
		if req.status_code != 200:
			print("ERROR: Es kann zwar eine Verbindung zur API Aufgebaut werden, aber scheinbar läuft diese nicht korrekt")
			return False
		print("INFO: Verbindung zur API erfolgreich geprüft!")
	except requests.exceptions.ConnectionError:
		print("ERROR: Es konnte keine Korrekte Verbindung zur API aufgebaut werden. Bitte Prüfen Sie, ob sie deren erreichbarkeit, und ob alle Services laufen")
		return False

	'''
	Todo:
		implementiere fehlende prüfunktionen Funktionen
	'''

	return True


def main():
	print("INIT: Starte OnOffDart-Service")

	#Einstellungen für die Serielle Verbindung zum Arduino
	serial_conn.baudrate = BAUD_RATE
	serial_conn.port = ARDUINO_PORT
	serial.timeout = SERIAL_TIMEOUT

	if checkConnections():
		print("INIT: Alle Komponenten scheinen erreichbar zu sein. Setze Fort")
		arduinoKommunikationsThread = threading.Thread(target=arduinoSchnittstelle)
		arduinoKommunikationsThread.start() #Starte Arduino Thread
		updateGameStateThread = threading.Thread(target=getGamestate)
		updateGameStateThread.start() #Startet das Gamestate Update
		
	else:
		print("ERROR: Es gab ein Problem bei einer der Komponenten, das Program kann so leider nicht fortfahren.")

	'''
	Todo: 
		Baue am besten einen Prüfmechnanismus ein, um permanent zu prüfen, ob noch alle benötigten Verbindungen stehen 
		(wird teilweise in den functionen gemacht, sollte aber bei denen ausgelagert, und besser zentral geregelt werden 
		-> starte dann auch die abgestürzten Threads neu, um nen Regelmässigen check zu haben)
		Idealerweise gibts nen Daemon, welcher alle X Sekunden alle Verbindungen prüft, und das Program bei Problemen Pausiert
		den Nutzer informiert, und bei wieder stehender Verbindung fortsezt
	'''
	return


main()