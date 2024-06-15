import serial
import time
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import threading
from threading import Lock
import json
import logging

ARDUINO_PORT = "COM8" #Der Port an welchem Der Arduino via USB angeschlossen ist
BAUD_RATE = 9600 #Die Baud Rate für die Arduino-USB-Serial Verbindnung
SERIAL_TIMEOUT = 3#Der Maximal zulässige Tiemout für die Serielle Verbindung

API_SERVER_DOMAIN = "http://localhost:8000/api"#Die Domain des API-Servers

THREAD_CHECK_INTERVAL = 5 # Prüfe alle X Sekunden ob noch alle Threads laufen oder iwo probleme aufgetreten sind, versuche bei Problemen neu zu starten


#-----------------------------
serial_conn = serial.Serial() #Das Objekt für die Serielle Verbindung (wird beim Verbidnugnscheck initialisiert)

# Create a custom logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)#Logger loggt erstmal alles

# Create handlers
consoleLogHandler = logging.StreamHandler()
consoleLogHandler.setLevel(logging.INFO)#Auf der console wird maximal INFO lvl ausgegeben

logFileHandler = logging.FileHandler('OnOff-Dart.log')
logFileHandler.setLevel(logging.DEBUG)#In der Log Datei wird alles gespeicehrt bis einschließlich DEBUG

consoleLogFormat = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', "%d-%m-%Y %H:%M:%S")
consoleLogHandler.setFormatter(consoleLogFormat)

fileLogFormat = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', "%d-%m-%Y %H:%M:%S")
logFileHandler.setFormatter(fileLogFormat)

# Add handlers to the logger
logger.addHandler(consoleLogHandler)
logger.addHandler(logFileHandler)


requests.packages.urllib3.disable_warnings(InsecureRequestWarning) #Schaltet TLS warnungen aus
#-----------------------------

'''
Liest den Camera Feed der Onboard Camera ein
'''
def readCamera():
	#Todo: Implement
	return




'''
Wertet den Camera Feed aus, aka Führt die Bildereknneugn für die Linie aus, und
nuzt die API funktionen 
'''
def evaluateCameraFeed():
	#Todo: Implement
	return


'''
Schickt den Camera Feed an den API Server
'''
#Todo: Implement
def sendCameraFeed():
	return



#-----------------------------

'''
Schaltet den angeschlossenden LED Strip
'''
def enableLEDs():
	#Todo: Implement
	return


#-----------------------------


#Repräsentiert den Zustand des Spiels
class Spiel:
	def __init__(self, p_uid, p_Game, p_playerIDs, p_player, p_Variant, p_In, p_Out, p_ActivePlayer, p_ThrowRound, p_Gamestate, p_UndoLog):
		self.uid = p_uid #Die Uid des Spiels (GET/game->id->UID)
		self.Game = p_Game 
		self.playerIDs = p_playerIDs #Die Ids der Spieler als Array
		self.player = p_player #Die Spielerobjekte wie sie von der API zurückgegeben werden
		self.Variant = p_Variant #(GET/game->id->variant)
		self.In = p_In   #(GET/game->id->in)
		self.Out = p_Out #(GET/game->id->out)
		self.ActivePlayer = p_ActivePlayer #(GET/game->id->GameObject->ActivePlayer)
		self.ThrowRound = p_ThrowRound #(GET/game->id->GameObject->ThrowRound)
		self.GameState = p_Gamestate #(GET/game->id->GameObject->GameState)
		self.UndoLog = p_UndoLog

#-----------------------------

'''
Gibt vom einem Spiel den json des aktiven Spielers zurück
@param game Das zu nuzende Spiel Objekt
@return Der aktive Spieler als json Objekt
'''
def getCurrentPlayer(game: Spiel):
	spielerListe = game.player
	activePlayer = game.ActivePlayer
	return spielerListe[activePlayer]

'''
Gibt vom zu prüfenden Spieler die gesammtzahl an bisherigen Würfen zurück
@param spieler Das Spieler json
@return die Gesammtzahl an bisherigen Würfen als Integer
'''
def getPlayerThrowTotal(spieler):
	return int(spieler['TotalThrowCount'])

'''
Gibt vom zu prüfenden Spieler die gesammtzahl an Punkten in der aktuellen Runde zurück
@param spieler Das Spieler json
@return  die gesammtzahl an Punkten in der aktuellen Runde als Integer
'''
def getPlayerRoundThrowSum(spieler):
	return int(spieler['ThrowSum'])

'''
Gibt vom zu prüfenden Spieler den Punkteschnitt zurück
@param spieler Das Spieler json
@return Der Punkteschnitt als float
'''
def getPlayerThrowAverage(spieler):
	return float(spieler['Average'])



'''
Fetched einmal alle Spiele von der API
@return spiele json, oder None (falls keine exestieren oder der Verbindugnsaufbau gescheitert ist)
@throws requests.exceptions.ConnectionError Falls keine Verbindung aufgebaut werden kann
'''
def getAPIGames():
	try:
		gamesRequest = requests.get(f"{API_SERVER_DOMAIN}/game", verify=False)#Lese lisste aller Spiele aus
		games = (gamesRequest.text).strip() #Aufräumen des Response
		if games == "null":
			logger.warning('Es konnten keine Spiele gefeched werden, da bisher keine erstellt wurden')
			return None
		else:
			return json.loads(gamesRequest.text) #Gebe Daten als json zurück
	except requests.exceptions.ConnectionError:
		logger.critical('Es Konnte keine Verbindung zur API aufgebaut werden!')
		return None




'''
Gibt das aktuelle Spiel zurück in dem es aus der liste aller Spieler das mit höchster uid bestimmt 
Wenn eine ungültige UID in den Daten gefunden wird, wird diese Ignoriert

@param gamesJSON eine gamesJSON welche alle Spiele enthält 
@return json Die json des aktuell laufenden Spiels. None, falls keine gültige UID gefunden wurde
'''
def getCurrentGame(gamesJSON):
	max_uid = -1
	max_index  = -1 #Die höchste gefundene UID & zugeöriger INDEX
	try:
		if gamesJSON != None:
			for i in range(len(gamesJSON)): #Durchsuche gamesJson nach höchster uid (nötig da reihenfolge der daten unbestimmt ist)
				curUID = gamesJSON[i].get('uid')
				if int(curUID) > max_uid:
					max_uid = int(gamesJSON[i].get('uid'))
					max_index = i
		else:
			logger.error("Es wurden keine Daten zur auswertung gegeben. Diese Funktion hätte nicht ausgeführt werden dürfen")
			return None
	except ValueError: #Es befand sich eine ungültige uid in der JSON
		logger.warning(f"Ungültige UID in den Daten gefunden: {curUID}")

	return gamesJSON[max_index].get('GameObject').get('Base') if max_index>-1 else None


'''
Gibt die aktuelle UID zurück
@return UID als Integer,o der None bei Problemen
'''
def getCurrentUID() -> int:
	aktuellesSpiel = fetchCurrentGame()
	if(aktuellesSpiel != None):
		return int(aktuellesSpiel.uid)
	else:
		return None




#-----------------------------

'''
Erhält die JSON von einem Gameobject und gibt ein Spiel Objekt zurück

'''
def createSpiel(gameJSON) -> Spiel:
	uid = gameJSON.get('UID')
	game = gameJSON.get('Game')
	players = gameJSON.get("Player")
	playerIDs = [int(players[0].get('UID')), int(players[1].get('UID'))]
	variant = gameJSON.get('Variant')
	In = gameJSON.get('In')
	Out = gameJSON.get('Out')
	activePlayer = gameJSON.get('ActivePlayer')
	throwRound = gameJSON.get('ThrowRound')
	gameState = gameJSON.get('GameState')
	undoLog = gameJSON.get('UndoLog')

	aktuellesSpiel = Spiel(uid,game,playerIDs,players,variant,In,Out,activePlayer,throwRound,gameState,undoLog)
	logger.debug(f"Der aktuelle Spielstand wurde erfolgreich von der API abgefragt: UID: {aktuellesSpiel.uid}")
	return aktuellesSpiel



'''
Ermittelt die aktuellen Werte fürs Spiel von der API.
Nötig, da der Pi ja nicht bei Änderungen durch das Frontend im Backend informiert wird.
Daher ist eine Regelmässige Abfrage vor veränderungen nötig um den aktuellen Spielstate zu ermitteln.
Es wird vorausgesezt das die höchste numerische uid, die des aktuell, laufenden Spiels ist.
@return Spiel gibt die informationen in Spiel-Objekt zurück. None bei fehlern
'''
def fetchCurrentGame() -> Spiel:
			js = getAPIGames() #Feche einaml alle Spiele als JSON von der API
			if(js != None):
				curGameJSON = getCurrentGame(js)#Bestimme die JSON des aktuellen Spiels
				if(curGameJSON != None):					
					aktuellesSpiel = createSpiel(curGameJSON)
					return aktuellesSpiel
				else:
					logger.error("Es konnte kein aktives Spiel ermittelt werden")
					#KA muss ich mir noch überlgen was sinvoll ist
					return None
			else: #Es Gab Probleme beim Fechen der Games
				#KA muss ich mir noch überlgen was sinvoll ist
				return None

# Einfach nurn dictionary zur Schöneren Ausgabe der Empfangenden Werte
dict_punkte = {
	"1" : 'single',
	"2" : 'double',
	"3" : 'tripple',
	"25": 'bull'
}

'''
Sendet einen Wurf an die API
@param gameUID Die UID des Piels, an welches übertragen werden soll
@param modifier 1==Singel, 2==double, 3==Tripple, 25==bull. Wird als Zahl übergeben
@param value Der Zahlenwert als String
@return Gibt den Statuscode zurück, oder bei Verbindungsproblemen None
'''
def sendThrow(gameUID: int, modifier: int, value: int) -> [int, json]:
	try:
		reqURL = f"{API_SERVER_DOMAIN}/game/{str(gameUID)}/throw/{str(value)}/{str(modifier)}"
		req = requests.post(reqURL, verify=False)
		response = None
		if req.status_code == 200:
			response = json.loads(req.text)
		return [req.status_code, response]
	except requests.exceptions.ConnectionError:
		logger.critical(f'Es Konnte keine Verbindung zur API aufgebaut werden. Der wurf: {modifier},{value} konnte nicht übertragen werden')
		return None



#-----------------------------


'''
Prüft ob eine vom Arduino empfangende Nachricht überhaupt valide Daten enthält. Und welch art von NAchricht es ist
@param arduinoMsg Die Nachricht
@return [bool_1, bool_2]. Bool_1=True wenn valide Nachricht (bei falschen zahlenwerten wirds wie nen Fehlwruf behandelt), sonst false. Bool_2=true wenn numerisch, sonst false flas Fehlwurf
'''
def checkArduinoMsgValidity(arduinoMsg: str) -> [bool, bool]:
	if arduinoMsg.isnumeric() and len(arduinoMsg) == 3: #Es wird ein Zahlenwert mit korrekter länge empfangen
		modifier = int(arduinoMsg[0])
		value = int(arduinoMsg[1:3])

		if modifier < 1 or modifier > 3:#Ungültiger Modifier Wert -> Fehlwurf
			logger.warning(f"Es wurden ungültige Werte für den Modifier({modifier}) vom Arduino Empfangen. Interpretiere als Fehlwurf")
			return [True, False]
		if value < 1 or modifier > 20:#Ungültiger Feld Wert -> Fehlwurf
			logger.warning(f"Es wurden ungültige Werte für den Feldwert({value}) vom Arduino Empfangen. Interpretiere als Fehlwurf")
			return [True, False]
		return [True, True]# Gültige Zahlen
	elif arduinoMsg == "m": #Fehlwurf
		logger.info("Es wurde ein Fehlwurf festgestellt")
		return [True, False]
	else:
		logger.warning(f"Es wurde eine invalide Nachricht vom Arduino empfangen. Nachricht: {arduinoMsg}")
		return [False, False]



'''
Feched ein Spiel mit gegebener UID
@uid die Uid als integer
@return Gibt das Spiel als Spiel objekt zurück. Oder None bei Problemen
'''
def getGame(uid : int) -> Spiel:
	try:
		gameRequest = requests.get(f"{API_SERVER_DOMAIN}/game/{str(uid)}", verify=False)#Lese spiel mit uid aus
		if gameRequest.status_code == 200:
			gameJSON  = (json.loads(gameRequest.text))
			return createSpiel(gameJSON)
			#return json.loads(gamesRequest.text) #Gebe Daten als json zurück
		else: #Spiel exestiert nicht
			logger.error(f'Das Spiel mit der UID: {uid} konnte nicht von der API gefunden werden')
			return None
	except requests.exceptions.ConnectionError:
		logger.critical('Es Konnte keine Verbindung zur API aufgebaut werden!')
		return None
	return

'''
Interpretiert eine erhaltene Serial Nachricht vom Arduino.
Und behandelt die erhaltenen Daten entsprechend.

@param arduinoMsg die auszuwertende Nachricht
'''
def evalArduinoMsg(arduinoMsg: str):
	modifier = -1
	value = -1
	nachrichtValidity = checkArduinoMsgValidity(arduinoMsg)
	if(nachrichtValidity[0] == True):# Es wird nur auf valide Nachrichten reagiert
		if(nachrichtValidity[1] == True):# Gültige Zahlen erkannt
			modifier = int(arduinoMsg[0])
			value = int(arduinoMsg[1:3])
		else:#Fehlwurf irgendeiner Art wurde erkannt
			modifier = 0
			value = 0
		

		uid = getCurrentUID()
		if uid != None:
			throwResponse = sendThrow(uid, modifier, value)#Übertrage den wurf
			throwResponseCode = throwResponse[0]
			if throwResponseCode != None: #Keine Verbindungsprobleme bei übertragung
				if throwResponseCode == 200:
					logger.debug(f"Der Wurf wurde erfolgreich an die API übertragen. SpielUID: {uid}, Wurf: {modifier},{value}")
					spiel = createSpiel(throwResponse[1].get('Base'))
					showRoundStatus(spiel)
				elif throwResponseCode == 400: #Entweder hatte der Spieler schon 3 würfe, oder der Wert ist zu hoch und übersteigt die Restlichen Punkte

					spiel = getGame(uid)
					if(spiel != None):
						spieler = getCurrentPlayer(spiel)
						wurfzahl = len(spieler.get('LastThrows')) #Anzahl der Würfe des Spielers in der aktuellen Runde
						wurfWert = int(int(modifier) * int(value)) #Der Wert des Lezten versuchten Wurfes
						restScore = spieler.get('Score').get('Score')
						if wurfzahl < 3:
							logger.warning(f"Der Wurf({wurfWert}) war leider zu hoch. Aktueller Score: {restScore}")
						else:
							logger.error(f'Der Wurf: {modifier},{value}, konnte nicht übertragen werden, da der Spieler schon alle 3 Würfe hatte. Bitte Spieler wechseln')
					else: #Sollte hoffentlich nie triggern
						logger.error(f"Der Wurf: {modifier},{value}, konnte nicht übertragen werden, da der Spieler entweder schon alle 3 Würfe hatte, oder der Wert zu hoch zum Gewinnen war")
				elif throwResponseCode == 404:
					logger.critical(f"Der Wurf: {modifier},{value}, konnte nicht übertragen werden, da das Spiel mit der UID: {uid}, nicht gefunden werden konnte")
				else:
					logger.critical(f"Der Wurf konnte nicht übertragen werden, aufgrund eines unbeaknnten Fehlers im Backend. Status Code: {throwResponseCode}")
		else:
			logger.critical("Der Wurf konnte nicht übertragen werden, da die UID des aktuellen SPiels nicht ermittelt werden konnte. Prüfen ob auch wirklich bereits ein Spiel erstellt wurde")


'''
Stellt den Überliegenden Process für die Arduino - API Kommunikation dar.
Aka liest die Daten des Arduinos aus, und gibt diese entsprechend an die 
weiteren Methoden weiter.
'''
def arduinoSerialReceiver():
	try:
		while True:
			if serial_conn.in_waiting > 0: #Es kommen Daten auf der Verbindnung an
				arduinoMsg = serial_conn.readline().decode().strip()#Einlesen, Bytecode umwandeln, + extrazeichen entfernen
				evalArduinoMsg(arduinoMsg)
	except serial.serialutil.SerialException:
		logger.critical("Die Verbindung zum Arduino ist abgebrochen")
	return


#-----------------------------

'''
Gibt bei neuen Würfen den aktuellen Stand aus
'''
def showRoundStatus(game: Spiel):
	if game is not None:
		aktuellerSpieler = getCurrentPlayer(game)
		spielerName = aktuellerSpieler['Name']
		spielerRunden = aktuellerSpieler['ThrowRounds']#Die Runden des Spielers
		spielerRundenZahl = len(spielerRunden)-1#Die Anzahl an Runden des Spielers
		aktuelleSpielerRunde = spielerRunden[spielerRundenZahl]#Die aktuelle Runde des Spielers
		aktuelleSpielerRundeWuerfe = aktuelleSpielerRunde['Throws']#Die Würfe des Spielrs in der aktuellen Runde
		aktuelleRundeAktuellerWurfzahl = len(aktuelleSpielerRundeWuerfe)#Die Anzahl an Würfen des Spielers in der aktuellen Runde
		aktuelleRundeAktuellerWurf = aktuelleSpielerRundeWuerfe[aktuelleRundeAktuellerWurfzahl-1]#Der Aktuellste Wurf des Spielers
		wurfWert = (int(aktuelleRundeAktuellerWurf.get('Number')) * int(aktuelleRundeAktuellerWurf.get('Modifier')))
		logger.info(f"Aktueller Spieler: {spielerName}, in Runde: {spielerRundenZahl}. Mit {aktuelleRundeAktuellerWurfzahl} Würfen. Average: {getPlayerThrowAverage(aktuellerSpieler)}. Lezter Wurf-Wert: {wurfWert}")
	return


#-----------------------------

'''
Prüft ob eine Serielle Verbindung zum Arduino aufgebaut werden kann
@return True, wenn ja, False wenn nein
'''
def checkArduinoConnection() -> bool:
	logger.info("Prüfe die Verbindung zum Arduino...")
	try:
		serial_conn.open()#Baut eine Serielle Verbindung mit dem Arduino auf
		time.sleep(1)#Warted 1ne Sekunde für den Verbindungsaufbau
		logger.info("Verbindung zum Arduino erfolgreich aufgebaut.")
		return True
	except serial.serialutil.SerialException:
		logger.critical("Es konnte keine Verbindung zum Arduino aufgebaut werden")
		return False


'''
Prüft ob eine Verbindung zur API aufgebaut werden kann
@return True, wenn ja, False wenn nein
'''
def checkApiConnection() -> bool:
	logger.info("Prüfe die Verbindung zur API...")
	try:
		req = requests.get(API_SERVER_DOMAIN, verify=False)
		if req.status_code != 200:
			logger.critical(f"Es konnte zwar eine Verbindung zum Server, nicht aber zur API aufgebaut werden. Statuscode: {req.status_code}")
			return False
		else:
			logger.info("Verbindung zur API erfolgreich aufgebaut.")
			return True
	except requests.exceptions.ConnectionError:
		logger.critical("Es konnte keine Verbindung mit dem API Server aufgebaut werden")
		return False

'''
Prüft ob eine Verbindung zur Onboard Kamera aufgebaut werden kann
@return True, wenn ja, False wenn nein
'''
def checkCameraConnection() -> bool:
	'''
		TODO. Implement
	'''
	return True

'''
Prüft ob die angeschlossenden LEDs angesteuert werden können
@return True, wenn ja, False wenn nein
'''
def checkLedConnection() -> bool:
	'''
		TODO. Implement
	'''
	return True


'''
Prüft ob beim Setup, die Verbindungen zu allen Komponenten aufgebaut werden konnten
@return True, wenn ja, false wenn nein
'''
def checkConnectionsSetup() -> bool :
	return checkArduinoConnection() and checkApiConnection() and checkCameraConnection() and checkLedConnection()


#-----------------------------

def main():
	global serial_conn
	while True:
		logger.info('Starte OnOffDart-Service')
		#Einstellungen für die Serielle Verbindung zum Arduino
		serial_conn.baudrate = BAUD_RATE
		serial_conn.port = ARDUINO_PORT
		serial.timeout = SERIAL_TIMEOUT
		if checkConnectionsSetup():
			arduCom_Thread = threading.Thread(target=arduinoSerialReceiver)
			arduCom_Thread.start()
			while True:
				time.sleep(THREAD_CHECK_INTERVAL)
				if not arduCom_Thread.is_alive(): #Thread ist fertig/abgestürzt
					serial_conn.close() #Alte Serielle Verbindung beenden
					checkArduinoConnection()
					arduCom_Thread = threading.Thread(target=arduinoSerialReceiver)
					arduCom_Thread.start()
		else:
			logger.critical("Es gab Probleme bei einer Verbindung, bitte Prüfen sie die entsprechende Komponente. Das Program started in 5 Sekunden neu und versucht es erneut")
		serial_conn.close() #Alte Serielle Verbindung beenden
		time.sleep(5)


main()