import serial
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import json
import logging
import threading
from threading import Lock
import time
from lcdSelect import lcdUserListSelect


ARDUINO_PORT:str = "/dev/ttyUSB0" #Der Port an welchem Der Arduino via USB angeschlossen ist
BAUD_RATE:int = 9600 #Die Baud Rate für die Arduino-USB-Serial Verbindnung
SERIAL_TIMEOUT:int = 3#Der Maximal zulässige Tiemout für die Serielle Verbindung

API_SERVER_DOMAIN:str = "https://api.onoff-dart.de/api"#Die Domain des API-Servers

THREAD_CHECK_INTERVAL:int = 5 # Prüfe alle X Sekunden ob noch alle Threads laufen oder iwo probleme aufgetreten sind, versuche bei Problemen neu zu starten

LOG_FILE_LOCATION = './1.log'

'''
Das Interval wann für das aktuell laufende Spiel nach updates gesucht werden soll.
MAX = Die Obergrenze wenn das lokale Spiel dran ist.
MIN = Wenn der andere Spieler dran ist, oder wir im INIT sind
'''
CHECK_GAME_UPDATE_INTERVAL_MAX:int = 5
CHECK_GAME_UPDATE_INTERVAL_MIN:int = 2

SHOW_GAME_INTERVALL:int = 3 #Das intervall in dem der Aktuelle Spielzustand auf der Konsole angezeigt werden soll



LOCAL_GAME_UID:int = -1#Muss über Display ein gegeben werden
LOCAL_PLAYER_UID:int = -1#Wird auch übers Display eingestellt






#-----------------------------
'''
INIT = Es wurde ne UID ermittelt aber der aktuelle Spieler für die aktuelle Scheibe ist noch nicht ermittelt
THROW_1 - 3 =  Verschiedene Würfe
OTHER_PLAYER = Der andere Spieler ist am Zug
UEBERTRITT = Es wurde ein lokaler übertritt festgestellt
WIN = Das Spiel ist Vorbei, und ein Spieler hat gewonnen

'''
PREVIOUS_STATE:str = 'INIT' #Der Vorherige Zustand des Automaten (bei start INIT) (für zustände+übergaänge siehe Zustandsdiagram in Dokumentation)
PREVIOUS_STATE_LOCK = Lock()
CURRENT_STATE:str = 'INIT' #Der Aktuelle Zustand des Automaten (bei start INIT) (für zustände+übergaänge siehe Zustandsdiagram in Dokumentation)
CURRENT_STATE_LOCK = Lock()

SPIEL = None#Speichert das aktuellste Spielupdate
SPIEL_LOCK = Lock()
LOKAL_PLAYER = None
LOKAL_PLAYER_LOCK = Lock()





serial_conn = serial.Serial() #Das Objekt für die Serielle Verbindung (wird beim Verbidnugnscheck initialisiert)

# Create a custom logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)#Logger loggt erstmal alles

# Create handlers
consoleLogHandler = logging.StreamHandler()
consoleLogHandler.setLevel(logging.INFO)#Auf der console wird maximal INFO lvl ausgegeben

logFileHandler = logging.FileHandler(LOG_FILE_LOCATION)
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
Verkabelung:
	PI   	| 	LED
	----------------- 
	GND 	-> 	GND 
	GPIO18	->	DIN
	

'''



'''
Schaltet den angeschlossenden LED Strip
'''
def enableLEDs():
	#Todo: Implement
	return



'''
Zeigt dem Spieler an das er/sie Verloren hat
'''
def showLoose():
	'''
	TODO:
		implement. soll später via leds anzeigen, aktuell Placeholder mit einfacher Text ausgabe
	'''
	print("PLACEHOLDER: Sie haben leider verloren")
	return


'''
Zeigt dem Spieler an das er/sie Gewonnen hat
'''
def showWin():
	'''
	TODO:
		implement. soll später via leds anzeigen, aktuell Placeholder mit einfacher Text ausgabe
	'''
	print("PLACEHOLDER: Sie haben gewonnen")
	return



'''
Zeigt dem Spieler an das er/sie nicht werfen darf
'''
def showNotReady():
	'''
	TODO:
		implement. soll später via leds anzeigen, aktuell Placeholder mit einfacher Text ausgabe
	'''
	print("PLACEHOLDER: Sie dürfen NICHT werfen")
	return


'''
Zeigt dem Spieler an das er/sie werfen darf
'''
def showReady():
	'''
	TODO:
		implement. soll später via leds anzeigen, aktuell Placeholder mit einfacher Text ausgabe
	'''
	print("PLACEHOLDER: Sie dürfen werfen")
	return


#-----------------------------

class Spieler:
	def __init__(self, p_uid, p_name, p_nickname, p_image, p_throwRounds, p_totalThrowCount, p_score, p_lastThrows, p_throwSum, p_average):
		self.uid = p_uid #Int
		self.name = p_name #String
		self.nickname = p_nickname#String
		self.image = p_image #String
		self.throwRounds = p_throwRounds #JSON
		self.totalThrowCount = p_totalThrowCount #int
		self.score = p_score #json
		self.lastThrows = p_lastThrows #json
		self.throwSum = p_throwSum #int
		self.average = p_average #int



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
Erhält die JSON von einem Gameobject und gibt ein Spiel Objekt zurück

'''
def createSpiel(gameJSON: json) -> Spiel:
	if gameJSON.get('GameObject') != None:
		gameJSON = gameJSON.get('GameObject').get('Base')

	if(gameJSON.get('Base') != None):#Bei ner etwas anders formatierten json einen Layer tiefer gehen
		gameJSON = gameJSON.get('Base')

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
	logger.debug(f"Das Spiel wurde erfolgreich von der API abgefragt: UID: {aktuellesSpiel.uid}")

	return aktuellesSpiel


#-----------------------------

'''
Versuche bei der API den Spieler zu wechseln
@return bool Gibt zurück, ob der Spielerwechsel erfolgreich war
'''
def requestPlayerChange() -> bool:
	uid = getUID()
	if uid != None:
		try:
			req = requests.post(f"{API_SERVER_DOMAIN}/game/{str(uid)}/nextPlayer", verify=False)
			if req.status_code == 200:
				return True
			else: #Spiel exestiert nicht
				logger.error(f'Spielerwechsel nicht möglich!. Das Spiel mit der UID: {uid} konnte nicht von der API gefunden werden. Statuscode: {req.status_code}')
				return False
		except requests.exceptions.ConnectionError:
			logger.critical('Es Konnte keine Verbindung zur API aufgebaut werden!')
			return False
	else:
		logger.error("Spielerwechsel nicht möglich, da noch keine Spiel UID ermittelt wurde")
		return False


'''
Fetched ein Spiel mit gegebener UID
@uid die Uid als integer
@return Gibt das Spiel als Spiel objekt zurück.
@return None bei Problemen
'''
def fetchUIDGame(uid : int) -> Spiel:
	try:
		gameRequest = requests.get(f"{API_SERVER_DOMAIN}/game/{str(uid)}/display", verify=False)#Lese spiel mit uid aus
		if gameRequest.status_code == 200:
			gameJSON  = (json.loads(gameRequest.text))
			return createSpiel(gameJSON)
		else: #Spiel exestiert nicht
			logger.error(f'Das Spiel mit der UID: {uid} konnte nicht von der API gefunden werden')
			return None
	except requests.exceptions.ConnectionError:
		logger.critical('Es Konnte keine Verbindung zur API aufgebaut werden!')
		return None
	return





'''
Fetched einmal alle Spiele von der API
@return Spiel[] Eine Liste aller Spiele
@return None falls der Verbindungsaufbau gescheitert ist
@throws requests.exceptions.ConnectionError Falls keine Verbindung aufgebaut werden kann
'''
def fetchAPIGames() -> Spiel:
	try:
		gamesRequest = requests.get(f"{API_SERVER_DOMAIN}/game", verify=False)#Lese lisste aller Spiele aus
		games = (gamesRequest.text).strip() #Aufräumen des Response
		if games == "null":
			logger.warning('Es konnten keine Spiele gefeched werden, da bisher keine erstellt wurden')
			return None
		else:
			spieleJSON:json = json.loads(gamesRequest.text)
			spiele = [] #Speichert alle Spiele als Spiel objekte in Liste

			for spiel in spieleJSON:
				spiele.append(createSpiel(spiel))
			return spiele #Gebe Liste aller Spiele zurück
	except requests.exceptions.ConnectionError:
		logger.critical('Es Konnte keine Verbindung zur API aufgebaut werden!')
		return None



'''
Hilfsmethode. Sendet einen wurf mit gegebenen Werten an die API. Und aktualisiert bei Erfolg den aktuellen Spieler
@param uid. Die UID des Spiels an welches der Wurf übermittlet werden soll
@param modifier. Der Wurf Modifier
@param value. Der Wert des Wurfs 
@return der Status Code des Requests, sowie die Textmeldung/json im Response
@return None, falls eine Verbindung nicht möglich war
'''
def pushThrowToAPI(uid:int, modifier: int, value: int) -> [int, json]:
	try:
		reqURL = f"{API_SERVER_DOMAIN}/game/{str(uid)}/throw/{str(value)}/{str(modifier)}"
		req = requests.post(reqURL, verify=False)
		return [req.status_code, json.loads(req.text)]
	except requests.exceptions.ConnectionError:
		logger.critical(f'Es Konnte keine Verbindung zur API aufgebaut werden. Der wurf: {modifier},{value} konnte nicht übertragen werden')
		return None
	except json.JSONDecodeError:
		return [req.status_code, None]
	return

#---------- LOKALE Getter/Setter-------------------


'''
Gibt die zulezt gespeicherten Spielinformationen
@Die neusten Spielinformationen
'''
def getGame() -> Spiel:
	global SPIEL, SPIEL_LOCK
	SPIEL_LOCK.acquire()
	temp:Spiel = SPIEL
	SPIEL_LOCK.release()
	return temp


'''
Sezt die neusten Spielinformationen
@Die infos des neusten Spiels
'''
def setGame(spielUpdate:Spiel) -> Spiel:
	global SPIEL, SPIEL_LOCK
	SPIEL_LOCK.acquire()
	SPIEL = spielUpdate
	SPIEL_LOCK.release()
	return








'''
Gibt den aktuellen Gespeicherten Lokalen Spieler zurück
@return Das Spielerobjekt des lokalen Spielers
@return None wenn noch kein lokaler Spieler ermittelt wurde
'''
def getPlayer() -> Spieler:
	global LOKAL_PLAYER, LOKAL_PLAYER_LOCK
	LOKAL_PLAYER_LOCK.acquire()
	player = LOKAL_PLAYER
	LOKAL_PLAYER_LOCK.release()
	return player


'''
Setzt den lokalen Player des aktuellen Spiels
@param Spieler player, der neu zu setzende Wert
'''
def setPlayer(player: Spieler):
	global LOKAL_PLAYER, LOKAL_PLAYER_LOCK
	LOKAL_PLAYER_LOCK.acquire()
	LOKAL_PLAYER = player
	LOKAL_PLAYER_LOCK.release()
	if player != None:
		logger.debug(f"Neuer Lokaler Spieler gesezt: UID:{player.uid}, Name:{player.name}")
	else:
		logger.debug(f"Lokaler Spieler auf None gesezt ")
	return 


'''
Gibt den vorherigen Gespeicherten STATE des laufenden SPIELS für lokal zurück
@return str Den vorherigen lokalen state des laufenden Spiels
'''
def getPreviousState() -> str:
	global PREVIOUS_STATE, PREVIOUS_STATE_LOCK
	PREVIOUS_STATE_LOCK.acquire()
	state = PREVIOUS_STATE
	PREVIOUS_STATE_LOCK.release()
	return state


'''
Setzt den lokalen vorherigen State des aktuellen Spiels 
@param str state, der neu zu setzende Wert
'''
def setPreviousState(state: str):
	global PREVIOUS_STATE, PREVIOUS_STATE_LOCK
	PREVIOUS_STATE_LOCK.acquire()
	PREVIOUS_STATE = state
	PREVIOUS_STATE_LOCK.release()
	logger.debug(f"Vorherigen Zustand gewechselt")
	return 


'''
Gibt den aktuellen Gespeicherten STATE des laufenden SPIELS für lokal zurück
@return str Den aktuellen lokalen state des laufenden Spiels
'''
def getState() -> str:
	global CURRENT_STATE, CURRENT_STATE_LOCK
	CURRENT_STATE_LOCK.acquire()
	state = CURRENT_STATE
	CURRENT_STATE_LOCK.release()
	return state


'''
Setzt den lokalen State des aktuellen Spiels 
@param str state, der neu zu setzende Wert
'''
def setState(state: str):
	global CURRENT_STATE, CURRENT_STATE_LOCK, PREVIOUS_STATE, PREVIOUS_STATE_LOCK
	CURRENT_STATE_LOCK.acquire()
	temp = CURRENT_STATE
	CURRENT_STATE = state
	CURRENT_STATE_LOCK.release()
	PREVIOUS_STATE_LOCK.acquire()
	PREVIOUS_STATE = temp
	PREVIOUS_STATE_LOCK.release()
	if state == 'UEBERTRITT' or state == 'OTHER_PLAYER': #Spieler darf NICHT WERFEN
		showNotReady()
	elif state == 'INIT' or state == 'THROW_1' or state == 'THROW_2' or state == 'THROW_3':#Spieler darf Werfen
		showReady() 
	logger.debug(f"Zustandswechsel: Vorheriger Zustand: {temp}, neuer Zustand: {state}")
	return 


'''
Gibt die Gespeicherte UID des laufenden SPIELS zurück
@return int Die UID des laufenden Spiels
@return None Falls aktuell kein SPiel läuft, oder andere Probleme vorliegen
'''
def getUID() -> int:
	global LOCAL_GAME_UID
	return LOCAL_GAME_UID


'''
Setzt die UID des aktuellen Spiels 
@param int uid, der neu zu setzende Wert
'''
def setUID(uid: int):
	global LOCAL_GAME_UID
	LOCAL_GAME_UID = uid
	logger.debug(f"Neue UID gesezt: {uid}")
	return


'''
Gibt die Gespeicherte UID des Spielers zurück
@return int Die UID des lokalen Spielers
@return None Falls aktuell nocj kein Spieler festgelegt wurde
'''
def getLocalPlayerUID() -> int:
	global LOCAL_PLAYER_UID
	return LOCAL_PLAYER_UID


'''
Setzt die UID des lokalen Spielers
@param int uid, der neu zu setzende Wert
'''
def setLocalPlayerUID(uid: int):
	global LOCAL_PLAYER_UID
	LOCAL_PLAYER_UID = uid
	logger.debug(f"Neue Spieler-UID gesezt: {uid}")
	return


#-----------------------------

'''
Prüft ob eine Serielle Verbindung zum Arduino aufgebaut werden kann
@return True, wenn ja, False wenn nein
'''
def checkArduinoConnection() -> bool:
	global serial_conn
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


'''
Erzeugt aus einem Spiel objekt ein Spieler objekt anhand der ID aka 0 oder 1 (NICHT die Spieler UID)
@param spiel Das Spiel aus dem der Spieler erzuegt werden soll
@return Spieler das Spielerobjekt
'''
def createPlayer(spiel: Spiel, arrayID:int) -> Spieler:
	player:json = spiel.player[arrayID]
	uid:int = int(player.get('UID'))
	name:str = str(player.get('Name')) 
	nickname:str = str(player.get('Nickname')) 
	image:str = str(player.get('Image'))  
	throwRounds:json =  player.get('ThrowRounds')
	totalThrowCount:int = int(player.get('TotalThrowCount')) 
	score:json = player.get('Score')
	lastThrows:json = player.get('LastThrows') 
	throwSum:int = int(player.get('ThrowSum'))  
	average:int = int(player.get('Average'))  
	spieler:Spieler = Spieler(uid,name,nickname,image,throwRounds,totalThrowCount,score,lastThrows,throwSum,average)
	#logger.debug(f"Der Spieler({spieler.name}) des übergegebenen Spiels({spiel.uid}) wurde erfolgreich erzeugt")
	return spieler



'''
Erzeugt aus einem Spiel objekt ein Spieler objekt des Akiven Spielers
@param spiel Das Spiel aus dem der Aktive Spieler erzeugt werden soll
@return Spieler das Spielerobjekt
'''
def createAktiveSpieler(spiel: Spiel) -> Spieler:
	aktivNummer:int = int(spiel.ActivePlayer)
	return createPlayer(spiel, aktivNummer)
	



#-----------------------------


'''
Gibt von einem Spieler Objekt den aktuellen Restscore zurück
@return Der aktuelle Restscore des Spielers als Integer
'''
def getPlayerScore(player: Spieler) -> int:
	return int((player.score).get('Score'))


#-----------------------------

'''
Hilfsmethode
Gibt basierend auf einen Eingabestate Wurfstate den nächsten aus
@return der nächste Wurfstate als string
@return None, wenn der gegebene Eingabestate kein wurfstate war
'''
def getNextThrowState(wurfState:str) -> str:
	if wurfState == 'THROW_1':
		return 'THROW_2'
	if wurfState == 'THROW_2':
		return 'THROW_3'

	if wurfState == 'THROW_3':
		return 'OTHER_PLAYER'
	return None #Kein gültiger eingangs Status -> None


'''
Sendet einen Wurf an die API
@param modifier 1==Singel, 2==double, 3==Tripple. Wird als Zahl übergeben
@param value Der Zahlenwert als String
'''
def sendThrow(modifier: int, value: int):
	state:str = getState() #Holt sich den aktuellen Gamestate
	if state == 'INIT':#passiert nix
		logger.warning("Der Wurf wird verworfen, da noch keinem Spiel beigetreten wurde")
		return

	if state == 'THROW_1' or state == 'THROW_2' or state == 'THROW_3':
		uid:int = getUID()
		statusCode, jsonResponse = pushThrowToAPI(uid, modifier, value)#Schickt den Wurf an die API		
		if statusCode != None: #Keine Verbindungsprobleme, bei Problemen wird Fehler woanders ausgegeben
			if statusCode == 200: #Keine Probleme, Übertragung hat funktioniert
				newState:str = getNextThrowState(state) #Placeholder
				if newState == None:#Tritt nur ein wenn ein ungültiger State vorlag (kann eigentlich nicht hier eintreten, außer race condition)
					return
				if newState == 'OTHER_PLAYER':
					if not requestPlayerChange():#Führe Spielerwechsel aus: Wenn aus irgendnem grund nicht möglich
						return #Keine Veränderung vornehmen Fehler wird schon in requestPlayerChange() ausgegeben

				setState(newState) #Neuen State entsprechend setzen
				spielUpdate:Spiel = createSpiel(jsonResponse)#Json Response enthielt die neuen geänderten Daten vom Spiel
				setGame(spielUpdate)#Aktualisiert das lokale Spiel
				setPlayer(createAktiveSpieler(spielUpdate))#Aktualisiert das lokale Spielerobjekt
				logger.info(f'({getPlayer().name}) - Wurf: {modifier},{value} - Neuer Score: {getPlayerScore(getPlayer())}')
				return

			elif statusCode == 400:#Entweder hatte der Spieler schon 3 Würfe, oder er hat zu wenig Restpunkte für den Wurf-> Fehlurf
				localPlayer:Spieler = getPlayer()
				score:int = getPlayerScore(localPlayer)
				wurf:int = int(modifier*value)
				print(wurf)
				if score < wurf: #Spieler hat nichtmehr genug punkte für den Wurf
					newState:str = getNextThrowState(state) #Placeholder
					if newState == None:#Tritt nur ein wenn ein ungültiger State vorlag (kann eigentlich nicht hier eintreten, außer race condition)
						return
					if newState == 'OTHER_PLAYER':
						if not requestPlayerChange():#Führe Spielerwechsel aus: Wenn aus irgendnem grund nicht möglich
							return #Keine Veränderung vornehmen Fehler wird schon in requestPlayerChange() ausgegeben
					setState(newState) #Neuen State entsprechend setzen
					if jsonResponse != None:
						spielUpdate:Spiel = createSpiel(jsonResponse)#Json Response enthielt die neuen geänderten Daten vom Spiel
						setGame(spielUpdate)#Aktualisiert das lokale Spiel
					logger.info(f"{localPlayer.name} - Ihr Rest-Score({score}) ist zu niedrig für ihren Wurf({wurf}). Werte Wurf als Fehlwurf")
					return
				else: #Spieler hatte scheinabr schon 3 Würfe -> Spielerwechsel anfragen + state setzen (um sync issue zu beheben)
					if not requestPlayerChange():#Führe Spielerwechsel aus: Wenn aus irgendnem grund nicht möglich
						return #Keine Veränderung vornehmen Fehler wird schon in requestPlayerChange() ausgegeben
					setState('OTHER_PLAYER') #Neuen State entsprechend setzen
					logger.info(f'Sie hatten bereits 3 Würfe. Wechsel Spieler')
					return
			elif wurfStatusCode == 404: #Dürfte auch nicht eintreten, außer das Spiel wurde während des Spielablaufs gelöscht
				logger.critical(f"{localPlayer.name} - Ihr Wurf: {modifier},{value}, konnte nicht übertragen werden, da das Spiel mit der UID: {uid}, nicht gefunden werden konnte. (Wurde vermutlich gelöscht/beendet)")
				return
			else: #Unbekannter Fehler -> Ausgeben
				logger.critical(f"Beim Übertragen des Wurfs ist ein unbekannter Fehler aufgetreten. Response Code: {wurfStatusCode}:{json.dumps(jsonResponse)}")
				return

		if state == 'OTHER_PLAYER':
			logger.warning(f"Es wurde ein Wurf festgestellt, aber der andere Spieler ist dran. Verwerfe Wurf")
			return


		if state == 'UEBERTRITT':
			logger.warning(f"Es wurde ein Wurf festgestellt, da sie aber übertreten haben, wird dieser verworfen")
			return

		if state == 'WIN':
			logger.warning(f"Es wurde ein Wurf festgestellt. Aber das Spiel ist bereits abgeschlossen. Verwerfe Wurf")
			return


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
Interpretiert eine erhaltene Serial Nachricht vom Arduino.
Und behandelt die erhaltenen Daten entsprechend.

@param arduinoMsg die auszuwertende Nachricht
'''
def computeArduinoMsg(arduinoMsg: str):
	modifier = value =  -1 #Init beide Werte mit nem Placeholder Wert
	nachrichtValidity:[bool,bool] = checkArduinoMsgValidity(arduinoMsg)
	if(nachrichtValidity[0] == True):# Es wird nur auf valide Nachrichten reagiert
		if(nachrichtValidity[1] == True):# Gültige Zahlen erkannt
			modifier = int(arduinoMsg[0])
			value = int(arduinoMsg[1:3])
		else:#Fehlwurf irgendeiner Art wurde erkannt
			modifier = value = 0
		uid:int = getUID()
		sendThrow(modifier, value)
		return




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
				computeArduinoMsg(arduinoMsg)
	except serial.serialutil.SerialException:
		logger.critical("Die Verbindung zum Arduino ist abgebrochen")
	return


#---------------------------------


'''
Erhält ein Spiel, und prüft ob sich der Interne Zustand, vom aktuellen unterscheidet. Und wenn ja ändert entsprechend (z.B. durch Frontend eingaben)
@param latestGame das Spiel gegen welches geprüft werden soll 
'''
def checkGameStateChanges(latestGame: Spiel):

	# Prüfe ob spiel vorbei ist
	if latestGame.GameState == 'WON':# Spiel wurde beendet
		p1:Spieler = createPlayer(latestGame, 0)
		setState('WIN')
		sieger:Spieler = p1
		
		if getPlayerScore(p1) > 0:#Spieler 2 hat gewonnen
			sieger = createPlayer(latestGame, 1)
		if sieger.uid == getLocalPlayerUID(): #Wir haben gewonnen
			showWin() #Führe Die Sieges Methode aus
		else:#Gegner hat gewonnen
			showLoose()#Führe Die Niederlage Methode aus
		return

	curState:str = getState()
	curGame:Spiel = getGame()
	curUID:int = getUID()

	if(latestGame != None and curState != 'WIN' and curState != 'INIT'):#Wenn das Spiel beendet worde machts keinen Sinn weiter auf Unterschiede zu prüfen, selbes gilt für wenns noch nicht gestarted wurde
		calcedGamestate: int = calcGameState(latestGame, getLocalPlayerUID())

		if latestGame.GameState == 'NEXTPLAYER' or latestGame.GameState == 'BUSTCONDITION' or latestGame.GameState == 'BUST':# and calcedGamestate == 'OTHER_PLAYER' and calcedGamestate == curState: #Spielerwechsel nach API erforderlich
			requestPlayerChange()
			return

		if(calcedGamestate != curState):#Irgendeine Diskrepanz liegt vor
			logger.warning(f"Diskrepanz Erkannt: Berechneter Zustand: {calcedGamestate}. Akttueller Zustand: {curState}. Nehme Änderun vor")
			setState(calcedGamestate)
			return
		else:
			return

		#------------------ Elementar fehler behoben (aka resynced) --------------


		if curState == 'UEBERTRITT': 
			if localPlayer != None:#Sollte eigentlich immer der Fall sein
				if aktPlayer.uid == localPlayer.uid: #Aktiver Spieler sind wir (aber wir haben übertreten)
					if getPreviousState() == 'OTHER_PLAYER': #Anderer Spieler war vorher dran, aber ist nun fertig und wir sind noch im übertritt
						setPreviousState('THROW_1')
						logger.info(f'Der Andere Spieler ist fertig. Wenn Übertritt vorbei, können sie Werfen')
						return
					else: #Wir haben übertreten aber waren eh schon dran -> keine Änderungen nötig
						return
				else: #Wir sind nicht der Aktive Spieler und haben übertreten -> egal
					return
			else: #Wir haben Übertreten Wissen aber nichtmal wer wir sind -> Egal
				return



		#if curState == 'THROW_1' or curState == 'THROW_2' or curState == 'THROW_3': #Wir sind dran und können Werfen
			#rundenWuerfe:int = len(aktPlayer.lastThrows) #Die anzahl an bisherigen Würfen des Aktiven Spielrs für die aktuelle Runde
			#newState = None
			#match rundenWuerfe:
				#case 0: 
					#newState = 'THROW_1'
				#case 1: 
					#newState = 'THROW_2'
				#case 2: 
					#newState = 'THROW_3'
				#case 3: #Wir hatten alle Würfe, haben aber noch nicht gewechselt
					#newState = 'OTHER_PLAYER'
			#if newState != curState: #Wenn eine Diskrpanz zwischen den Gespeicherten Würfen und den Loaklem Wurfstate vorliegt
				#setState(newState)#Ändere den Zustand
				#logger.warning(f"Externes Update: Diskrepanz bei den Würfen festgestellt: {newState}. Zustand Vorher: {curState}.")
			#return;
#
#
		#if curState == 'OTHER_PLAYER':
			#if aktPlayer.uid == localPlayer.uid: #Aktiver Spieler sind wieder wir (aka anderer Spieler ist fertig) -> Spielerwechsel hat stattgefunden
				#setState('THROW_1')#Wechsel Zustand
				#logger.info(f"Der andere Spieler ist fertig. Nun bitte werfen")
				#return
			#else: #Der andere Spieler ist noch nicht fertig -> warten
				#return




#-----------------------------


'''
Zeigt Regelmässig den aktuellen Lokalen Stand des Spiels an. Insofern wir nicht im 'NG' oder 'INIT' sind
'''
def showGame():
	global SHOW_GAME_INTERVALL
	while True:
		currentState:str = getState()
		if currentState != 'NG' and currentState != 'INIT':
			player:Player = getPlayer()
			uid:int = getUID()
			logger.info(f'Spiel: {uid} | Zustand: {currentState} - Lokaler Spieler: {player.name}. Runde: {player.totalThrowCount}. Score: {getPlayerScore(player)}. Gesammtwurfzahl: {player.totalThrowCount}. Average: {player.average}')			 
		time.sleep(SHOW_GAME_INTERVALL)
	return



'''
Prüft automatisch alle X Sekunden, ob es für das aktuelle Spiel (aka aktuelle UID),
updates gibt. (z.b. durchs Frontend hervorgerufen)

Wenn wir der aktuelle Spieler sind, prüft alle CHECK_GAME_UPDATE_INTERVAL_MAX Sekunden
Wenn State==Init, oder der andere Spieler dran -> CHECK_GAME_UPDATE_INTERVAL_MIN sekunden prüfen
'''
def fetchGameUpdates():
	global CHECK_GAME_UPDATE_INTERVAL_MAX, CHECK_GAME_UPDATE_INTERVAL_MIN
	updateInterval:int = 1
	while True:
		curState:str = getState()
		prevState:str = getPreviousState()
		if curState == 'OTHER_PLAYER' or (curState == 'UEBERTRITT' and prevState == 'OTHER_PLAYER'): #Wenn der andere Spieler dran ist besonders oft Prüfen, um mitzubekommen wann wir dran sind
			updateInterval = CHECK_GAME_UPDATE_INTERVAL_MIN
		else:
			updateInterval = CHECK_GAME_UPDATE_INTERVAL_MAX
		newestUpdate:Spiel = fetchUIDGame(getUID())
		if newestUpdate != None:
			checkGameStateChanges(newestUpdate) #Prüfe auf neuerungen und wende an falls nötig
			setGame(newestUpdate) #Update das lokale Spiel entsprechend mit den neusten Daten
		time.sleep(updateInterval)
	return



#-----------------------------

'''
Gibt basierend auf einem Spiel und einer user Id
den Sinvollsten gamestate für den Nutzer zurück
@return State der Passenste Zustand für den Nutzer
@return None, wenn der Nutzer nicht im Spiel ist
'''
def calcGameState(spiel:Spiel, uID:int):
	#INIT und UEBERTRITT sind nicht bestimmbar (macht aber auch keinen Sinn hier)
	if spiel.GameState == 'WON':# Spiel wurde beendet
		return 'WIN'
	spieler:Spieler = getPlayerUID(spiel, uID)
	aktSpieler:Spieler = createAktiveSpieler(spiel)

	if spieler != None:
		rundenWuerfe:int = len(aktSpieler.lastThrows) #Die anzahl an bisherigen Würfen des Aktiven Spielers für die aktuelle Runde
		if aktSpieler.uid == spieler.uid:#Der Spieler ist der aktive Spieler
			match rundenWuerfe:
				case 0: 
					return 'THROW_1'
				case 1: 
					return 'THROW_2'
				case 2: 
					return 'THROW_3'
			if spiel.GameState != 'NEXTPLAYER':# Wir sind noch nicht im 3ten wurf und aktiv, Aber haben 3 Würfe eingetragen -> wurden noch nicht gewiped aka gerade erst akt geworden
				return 'THROW_1'
			else:#Speielrwechsel erforderlich
				return 'OTHER_PLAYER' 
		else:#Spieler ist inaktiver Spieler
			if spiel.GameState == 'NEXTPLAYER': #Anderer Spieler ist fertig
				return 'THROW_1'
			else:
				return 'OTHER_PLAYER';
	else:
		return None




'''
Gibt von einem Gegebene Spiel das Spielerobjekt mit gegebener UID zurück
@param game Das Spiel in welchem nach dem Spieler gescuht werden soll
@param playerUid die UID des Spielers
@return das Spielerobjekt
@return None wenn der Spieler mit der UID im Spiel nicht exestiert
'''
def getPlayerUID(game:Spiel, playerUID:int) -> Spieler:
	if game != None and playerUID != None:
		p1:Spieler = createPlayer(game, 0)
		p2:Spieler = createPlayer(game, 1)
		if p1.uid == playerUID:
			return p1
		elif p2.uid == playerUID:
			return p2

	return None #Wenn kein gültiges Format, oder spielerUid nicht im Spiel

'''
Gibt auf dem LCD eine liste der aktuellen Spiele aus, von denen der Nutzer wählen kann
Gibt danach die beide nSpieler aus, von denen er sich wählt
Sezt die beiden gloablen variablen entsprechend, und returned -> return lässt das Program starten
'''
def userInit():
	if checkApiConnection():
		games = None
		
		while games == None:
			games = fetchAPIGames()
			time.sleep(1)
		spieleListe = [] #Liste aus Strings

		for i in range(len(games)):
			spieleListe.append(f"{i+1}. UID: {games[i].uid}")

		uid_auswahl:int = lcdUserListSelect(spieleListe)
		uid = games[uid_auswahl].uid
		logger.info(f"Übers Display wurde Spiel: {uid} gewählt")


		setUID(uid)
		curGame:Spiel = fetchUIDGame(getUID())
		p1:Spieler = createPlayer(curGame, 0)
		p2:Spieler = createPlayer(curGame, 1)

		spieler_liste = [f"Spieler UID: {p1.uid}: {p1.name}", f"Spieler UID: {p2.uid}: {p2.name}"]
		spieler_auswahl:int = lcdUserListSelect(spieler_liste)
		pUID = p1.uid if spieler_auswahl == 0 else p2.uid
		logger.info(f"Übers Display wurde Spieler: {pUID} gewählt")
		
		state:str = calcGameState(curGame, pUID)
		

		curPlayer: Spieler = getPlayerUID(curGame, pUID)

		setGame(curGame)
		setLocalPlayerUID(pUID)
		setPlayer(curPlayer)
		setState(state)

	#else:
		#os._exit() #Beende erstmal wenn die API nicht erreicht werden kann
	
	'''
	#TODO:
		Implement, return aktuell direkt nach userinput von der console, wird später über lcd und buttons gemacht
	'''


	return


'''
Beendet alle verbindungen und Threads
'''
def stopSystem():
	'''
	#TODO:
		Implement, returend aktuell sofort
	'''

	return

'''
Setzt das System auf/zurück
'''
def startSystem():
	global serial_conn
	logger.info('Starte OnOffDart-Service')
	serial_conn.baudrate = BAUD_RATE
	serial_conn.port = ARDUINO_PORT
	serial.timeout = SERIAL_TIMEOUT
	if checkConnectionsSetup(): #All Endpunkte sind erreichbar
		curGameUpdateCheckker_Thread = threading.Thread(target=fetchGameUpdates)#Prüft ob das aktuelle Spiel updates hat
		curGameUpdateCheckker_Thread.daemon = True
		curGameUpdateCheckker_Thread.start()

		showGame_Thread = threading.Thread(target=showGame)#Gibt Regelmässig aktuelle Werte fürs Spiel aus
		showGame_Thread.daemon = True
		showGame_Thread.start()

		arduCom_Thread = threading.Thread(target=arduinoSerialReceiver)
		arduCom_Thread.daemon = True
		arduCom_Thread.start()
		while True:
				time.sleep(THREAD_CHECK_INTERVAL)
				if not arduCom_Thread.is_alive(): #Thread ist fertig/abgestürzt
					serial_conn.close() #Alte Serielle Verbindung beenden
					checkArduinoConnection()
					arduCom_Thread = threading.Thread(target=arduinoSerialReceiver)
					arduCom_Thread.daemon = True
					arduCom_Thread.start()
		else:
			logger.critical("Es gab Probleme bei einer Verbindung, bitte Prüfen sie die entsprechende Komponente. Das Program started in 5 Sekunden neu und versucht es erneut")
		serial_conn.close() #Alte Serielle Verbindung beenden
		time.sleep(5)
	return


def main():
	userInit() #Warted darauf, das der Nutzer die nötigen eingaben getätigt hat
	startSystem()
	return



main()