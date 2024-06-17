import serial
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import json
import logging
import threading
from threading import Lock
import time

ARDUINO_PORT = "COM8" #Der Port an welchem Der Arduino via USB angeschlossen ist
BAUD_RATE = 9600 #Die Baud Rate für die Arduino-USB-Serial Verbindnung
SERIAL_TIMEOUT = 3#Der Maximal zulässige Tiemout für die Serielle Verbindung

API_SERVER_DOMAIN = "http://localhost:8000/api"#Die Domain des API-Servers

THREAD_CHECK_INTERVAL = 5 # Prüfe alle X Sekunden ob noch alle Threads laufen oder iwo probleme aufgetreten sind, versuche bei Problemen neu zu starten


'''
Das Interval wann für das aktuell laufende Spiel nach updates gesucht werden soll.
MAX = Die Obergrenze wenn das lokale Spiel dran ist.
MIN = Wenn der andere Spieler dran ist, oder wir im INIT sind
'''
CHECK_GAME_UPDATE_INTERVAL_MAX = 5
CHECK_GAME_UPDATE_INTERVAL_MIN = 2

SHOW_GAME_INTERVALL = 3 #Das intervall in dem der Aktuelle Spielzustand auf der Konsole angezeigt werden soll

CHECK_GLOBAL_GAME_INTERVAL = 10 #Prüft alle X Sekunden ob es ein neues Spiel gibt



#-----------------------------
'''
NG = No Game -> Es wurde noch keine UID fürs aktuelle Spiel ermittelt
INIT = Es wurde ne UID ermittelt aber der aktuelle Spieler für die aktuelle Scheibe ist noch nicht ermittelt
THROW_1 - 3 =  Verschiedene Würfe
OTHER_PLAYER = Der andere Spieler ist am Zug
UEBERTRITT = Es wurde ein lokaler übertritt festgestellt

'''
PREVIOUS_STATE:str = 'NG' #Der Vorherige Zustand des Automaten (bei start NG) (für zustände+übergaänge siehe Zustandsdiagram in Dokumentation)
PREVIOUS_STATE_LOCK = Lock()
CURRENT_STATE:str = 'NG' #Der Aktuelle Zustand des Automaten (bei start NG) (für zustände+übergaänge siehe Zustandsdiagram in Dokumentation)
CURRENT_STATE_LOCK = Lock()

CURRENT_GAME_UID:int = None #Speichert die UID des aktuell gespielten Spiels
CURRENT_GAME_UID_LOCK = Lock()

LOKAL_PLAYER = None #Repräsentiert den lokalen Spieler (als Spieler objekt)
LOKAL_PLAYER_LOCK = Lock()

PREVIOUS_SPIEL = None#Speichert den lezten Spiel Update Fetch ein
PREVIOUS_SPIEL_LOCK = Lock()


serial_conn = serial.Serial() #Das Objekt für die Serielle Verbindung (wird beim Verbidnugnscheck initialisiert)

# Create a custom logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)#Logger loggt erstmal alles

# Create handlers
consoleLogHandler = logging.StreamHandler()
consoleLogHandler.setLevel(logging.INFO)#Auf der console wird maximal INFO lvl ausgegeben

logFileHandler = logging.FileHandler('1.log')
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
Versucht ein gefundenes Spiel mit ungültiger UID zu löschen
'''
def deleteBadUID(uid):
	try:
		delete = requests.delete(f"{API_SERVER_DOMAIN}/game/{str(uid)}", verify=False)
	except requests.exceptions.ConnectionError:
		logger.critical('Es Konnte keine Verbindung zur API aufgebaut werden!')
	return


'''
Gibt das aktuelle Spiel zurück in dem es aus der liste aller Spieler das mit höchster uid bestimmt 
Wenn eine ungültige UID in den Daten gefunden wird, wird diese Ignoriert

@param gamesJSON eine gamesJSON welche alle Spiele enthält 
@return json Die json des aktuell laufenden Spiels. None, falls keine gültige UID gefunden wurde. -1 Wenn eine UID gelöscht wurde (-> nochmal request stellen)
'''
def fetchCurrentGameJson(gamesJSON: json) -> json:
	max_uid = max_index = curUID = -1#Die höchste gefundene UID & zugeöriger INDEX
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
		logger.warning(f"Ungültige UID in den Daten gefunden: {curUID}. Versuche diese zu Löschen, und nochmal nach einer gültigen ID zu suchen")
		deleteBadUID(curUID)
		return -1


	return gamesJSON[max_index].get('GameObject').get('Base') if max_index>-1 else None


'''
Fetched einmal alle Spiele von der API
@return spiele json, oder None (falls keine exestieren oder der Verbindugnsaufbau gescheitert ist)
@throws requests.exceptions.ConnectionError Falls keine Verbindung aufgebaut werden kann
'''
def fetchAPIGames() -> json:
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
Ermittelt das aktuellste laufende Spiel.
@return Das Spiel Objekt des aktuellsten laufenden Spiels
@return None, bei Verbdingungsproblemen, oder falls noch kein Spiel exestiert
'''
def fetchCurrentGame() -> Spiel:
	js = fetchAPIGames() #Feche einmal alle Spiele als JSON von der API
	if(js != None):
		curGameJSON = fetchCurrentGameJson(js)#Ermittle die JSON des aktuellen Spiels
		while(curGameJSON == -1):#Wenn ne ungültige uid gefunden und gelöscht wurde nochmal anfragen
			curGameJSON = fetchCurrentGameJson(fetchAPIGames())

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


'''
Ermittelt die UID des aktuellsten Spiels
@return UID als Integer
@return None bei Problemen
'''
def fetchCurrentGamesUID() -> int:
	aktuellesSpiel = fetchCurrentGame()
	if(aktuellesSpiel != None):
		return int(aktuellesSpiel.uid)
	else:
		return None

'''
Hilfsmethode. Sendet einen wurf mit gegebenen Werten an die API. Und aktualisiert bei Erfolg den aktuellen Spieler
@param uid. Die UID des Spiels an welches der Wurf übermittlet werden soll
@param modifier. Der Wurf Modifier
@param value. Der Wert des Wurfs 
@return der Status Code des Requests
@return None, falls eine Verbindung nicht möglich war
'''
def pushThrowToAPI(uid:int, modifier: int, value: int) -> int:
	try:
		reqURL = f"{API_SERVER_DOMAIN}/game/{str(uid)}/throw/{str(value)}/{str(modifier)}"
		req = requests.post(reqURL, verify=False)
		#if req.status_code == 200:#Erfolgreich übertragen + wird nur ausgeführt wenn ich auch wirklich werfen durfte
		#	gameResponse:json = json.loads(req.text)
		#	spiel:Spiel = createSpiel(gameResponse)
		#	player:Spieler = createAktiveSpieler(spiel)
		#	setPlayer(player)
		return req.status_code
	except requests.exceptions.ConnectionError:
		logger.critical(f'Es Konnte keine Verbindung zur API aufgebaut werden. Der wurf: {modifier},{value} konnte nicht übertragen werden')
		return None
	return

#---------- LOKALE Getter/Setter-------------------



'''
Gibt die Spielinformationen vom lezten Fetch zurück
@Das Spiel aus dem lezten Fetch
'''
def getPreviousGame() -> Spiel:
	global PREVIOUS_SPIEL, PREVIOUS_SPIEL_LOCK
	PREVIOUS_SPIEL_LOCK.acquire()
	prevspiel:Spiel = PREVIOUS_SPIEL
	PREVIOUS_SPIEL_LOCK.release()
	return prevspiel


'''
Gibt die Spielinformationen vom lezten Fetch zurück
@Das Spiel aus dem lezten Fetch
'''
def setPreviousGame(prevSpiel:Spiel) -> Spiel:
	global PREVIOUS_SPIEL, PREVIOUS_SPIEL_LOCK
	PREVIOUS_SPIEL_LOCK.acquire()
	PREVIOUS_SPIEL = prevSpiel
	PREVIOUS_SPIEL_LOCK.release()
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
	global CURRENT_GAME_UID, CURRENT_GAME_UID_LOCK
	CURRENT_GAME_UID_LOCK.acquire()
	uid = CURRENT_GAME_UID
	CURRENT_GAME_UID_LOCK.release()
	return uid


'''
Setzt die UID des aktuellen Spiels 
@param int uid, der neu zu setzende Wert
'''
def setUID(uid: int):
	global CURRENT_GAME_UID, CURRENT_GAME_UID_LOCK
	CURRENT_GAME_UID_LOCK.acquire()
	CURRENT_GAME_UID = uid
	CURRENT_GAME_UID_LOCK.release()
	logger.debug(f"Neue UID gesezt: {uid}")
	return


'''
Aktualisiert den Score des Spielers lokal (nur für ausgabe wichtig)
'''
def updatePlayerScore(score: int):
	global LOKAL_PLAYER, LOKAL_PLAYER_LOCK
	LOKAL_PLAYER_LOCK.acquire()
	if LOKAL_PLAYER != None:
		LOKAL_PLAYER.score['Score'] = score
	LOKAL_PLAYER_LOCK.release()
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
@param spiel Das Spiel aus dem der Aktive Spielerr erzuegt werden soll
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
Sendet einen Wurf an die API
@param modifier 1==Singel, 2==double, 3==Tripple. Wird als Zahl übergeben
@param value Der Zahlenwert als String
'''
def sendThrow(modifier: int, value: int):
	state:str = getState() #Holt sich den aktuellen Gamestate
	if state == 'NG': #Wir wissen noch nicht in welchem Spiel wir überhaupt sind
		logger.critical("Ein gültiger Wurf wurde festgestellt, konnte aber nicht übertragen werden, da für das aktuelle Spiel noch keine UID ermittelt werden konnte")
		return
	else: #Wir wissen in welchem Spiel wir sind aka, wir haben auch ne gültige uid
		uid:int = getUID()
		aktuellesSpiel:Spiel = fetchUIDGame(uid)
		aktivePlayerArrID:int = aktuellesSpiel.ActivePlayer#Speichert die Array ID des aktiv Players
		aktivePlayer:Spieler = createAktiveSpieler(aktuellesSpiel)
		if state == 'INIT':
			if aktuellesSpiel.ThrowRound == 1: #Runde 1 aka Spiel erste Runde
				if aktivePlayer.totalThrowCount == 0: #Es wurde noch nicht geworfen -> Wir sind der erste
					statusCode:int = pushThrowToAPI(uid, modifier, value)
					if statusCode != None:
						if statusCode == 200: #Keine Probleme, Übertragung hat funktioniert
							setPlayer(aktivePlayer) #-> Wir sind nun der Aktive Spieler
							setState('THROW_2')
							oldScore:int = getPlayerScore(aktivePlayer)
							updatePlayerScore(oldScore - (modifier*value))
							logger.info(f"Ihr erster Wurf wurde erfolgreich übertragen. Sie sind jetzt Spieler: {aktivePlayer.name}, mit UID: {aktivePlayer.uid}")
							return
						elif statusCode == 400: #Dürfte hier nicht errreicht werden können (kann nur heißen das der Spieler aus irgendnem grund schon 3 Würfe hatte -> scheinabr ein großes synchronisations problem)
							logger.error(f'Ihr Wurf konnte nicht übertragen werden. State: {state}, ResponseCode: {statusCode}')
							return
						elif statusCode == 404: #Dürfte auch nicht eintreten, außer in der API ist was kapuut oder synch. issue
							logger.critical(f"Ihr erster Wurf: {modifier},{value}, konnte nicht übertragen werden, da das Spiel mit der UID: {uid}, nicht gefunden werden konnte")
							return
						else: #Unbekannter Fehler -> Ausgeben
							logger.critical(f"Beim Übertragen des Wurfs ist ein unbekannter Fehler aufgetreten. Response Code: {statusCode}")
							return
					else: #Nichts ändern, Fehlermeldung wurde bereits woanders (pushThrowToAPI()) ausgegeben
						return
				else: #Der andere Spieler hat schon geworfen -> Ungültiger wurf
					setState('OTHER_PLAYER')
					localPlayerArrID:int = 1 if aktivePlayerArrID==0 else 0#Die Eigene Id ist die entgegengesezte des Aktiven Spielers
					setPlayer(createPlayer(aktuellesSpiel, ))
					logger.info(f"Der andere Spieler hat zu erst geworfen. Ihr Wurf wird verworfen. Lokaler Spieler: ID{p2.uid}, Name:{p2.name}")
					return
			else: #Wir befinden uns in einer Höheren Spielrunde (aber INIT State) -> wir sind nem Spiel nachgejoined
				'''

				TODO:
					Implement


				'''
				logger.critical("ACHTUNG DAS SPIEL WURD IN EINER HÖHEREN SPIELRUNDE BEGONNEN. DIES IST AKTUELL NOCH NICHT UMGESEZT")
				return
						


		if state == 'THROW_1' or state == 'THROW_2' or state == 'THROW_3':
			statusCode:int = pushThrowToAPI(uid, modifier, value)
			if statusCode != None:
				if statusCode == 200: #Keine Probleme, Übertragung hat funktioniert
					newState = None #Placeholder
					if state == 'THROW_1':
						newState = 'THROW_2'
					elif state == 'THROW_2':
						newState = 'THROW_3'
					else: #Das war der 3te Wurf -> Spielerwechsel
						if requestPlayerChange(): #Spielerwechsel Erfolgreich -> Änderung kann übernommen werden
							newState = 'OTHER_PLAYER'
						else: #Spielerwechsel aus irgendnem grund nicht möglich
							return #Keine Veränderung vornehmen, scheinbar nen sync issue
					setState(newState) #Neuen State entsprechend setzen
					oldScore:int = getPlayerScore(aktivePlayer)
					updatePlayerScore(oldScore - (modifier*value))
					logger.info(f'({getPlayer().name}) - Wurf: {modifier},{value}')
					return

				elif statusCode == 400:#Entweder hatte der Spieler schon 3 Würfe, oder er hat zu wenig Restpunkte für den Wurf-> Fehlurf
					localPlayer:Spieler = getPlayer()
					score:int = getPlayerScore(localPlayer)
					wurf:int = int(modifier*value)
					if score < wurf: #Spieler hat nichtmehr genug punkte für den Wurf
						if state == 'THROW_1':
							newState = 'THROW_2'
						elif state == 'THROW_2':
							newState = 'THROW_3'
						else: #Das war der 3te Wurf -> Spielerwechsel
							if requestPlayerChange(): #Spielerwechsel Erfolgreich -> Änderung kann übernommen werden
								newState = 'OTHER_PLAYER'
							else: #Spielerwechsel aus irgendnem grund nicht möglich
								return #Keine Veränderung vornehmen, scheinbar nen sync issue
						setState(newState) #Neuen State entsprechend setzen
						logger.info(f"{player.name} - Ihr Rest-Score({score}) ist zu niedrig für ihren Wurf({wurf}). Werte Wurf als Fehlwurf")
						return
					else: #Spieler hatte scheinabr schon 3 Würfe -> Spielerwechsel anfragen + state setzen (um sync issue zu beheben)
						if requestPlayerChange(): #Spielerwechsel Erfolgreich -> Änderung kann übernommen werden
							setState('OTHER_PLAYER') #Neuen State entsprechend setzen
							return
						else: #Spielerwechsel aus irgendnem grund nicht möglich
							return #Keine Veränderung vornehmen, scheinbar nen sync issue
				
				elif wurfStatusCode == 404: #Dürfte auch nicht eintreten, außer in der API ist was kapput oder sync. issue
					logger.critical(f"{localPlayer.name} - Ihr Wurf: {modifier},{value}, konnte nicht übertragen werden, da das Spiel mit der UID: {uid}, nicht gefunden werden konnte")
					return
				else: #Unbekannter Fehler -> Ausgeben
					logger.critical(f"Beim Übertragen des Wurfs ist ein unbekannter Fehler aufgetreten. Response Code: {wurfStatusCode}")
					return
			else: #Nichts ändern, Fehlermeldung wurde bereits woanders (pushThrowToAPI()) ausgegeben
				return



		if state == 'OTHER_PLAYER':
			logger.warning(f"Es wurde ein Wurf festgestellt, aber der andere Spieler ist dran. Verwerfe Wurf")
			return



		if state == 'UEBERTRITT':
			logger.warning(f"Es wurde ein Wurf festgestellt, aber der andere Spieler ist dran. Verwerfe Wurf")
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
Erhält ein Spiel, und prüft ob sich der Interne Zustand, vom aktuellen unterscheidet. Und wenn ja ändert entsprechend
@param latesGame das Spiel gegen welches geprüft werden soll 
'''
def checkGameStateChanges(latestGame: Spiel):
	curState:str = getState()
	curUid:int = getUID()
	if(latestGame != None):
		if int(latestGame.uid) != curUid: #SpielUid hat sich geändert -> Neues Spiel wurde erstellt
			setUID(int(latestGame.uid)) #Setze die UID neu
			setState('INIT')
			setPlayer(None)#Aktueller lokaler Spieler unbekannt
			setPreviousGame(None)
			logger.critical(f"Der Gamestatechange hat ein neues Spieler erkannt. Setze aktuelles zurück, und wechsel Spiel")
			return


		#Prüfe ob die zurückgegebenen Daten den aktuellen Zustand korrelieren
		#Prüfen ob der aktuelle Wurf passt, 
		#prüfen ob nicht doch anderer Spieler dran ist
		aktPlayer:Spieler = createAktiveSpieler(latestGame) #Bestimmt den aktuellen Spieler des letzten fetches
		aktivSpielerArrID:int = latestGame.ActivePlayer
		localPlayer:Spieler = getPlayer() #Bestimmte den lokalen Spieler
		if localPlayer != None: #Lokaler Spieler wurde bereits identifiziert
			if aktPlayer.uid != localPlayer.uid:#Der Aktuelle Spieler ist nicht der Aktive
				if curState == 'THROW_1' or curState == 'THROW_2' or curState == 'THROW_3': #ABER Der lokale Spieler ist in neinem Nicht gültigen lokalen Spielzustand
					setState('OTHER_PLAYER')#Ändere den Zustand
					logger.warning(f"ZUSTANDS Fehler festgestellt! Aktiver Spieler({aktPlayer.uid}) sind nicht wir({localPlayer.uid}), ändere Lokalen Zustand. Zustand Vorher: {curState}.")
					return
			else: #Lokaler Spieler ist Aktiver Spieler
				if curState == 'OTHER_PLAYER':#Aber wir befinden uns im Flaschen Zustand
					newState = curState
					rundenWuerfe:int = len(aktPlayer.lastThrows)
					if rundenWuerfe == 0:
						newState = 'THROW_1'
					elif rundenWuerfe == 1:
						newState = 'THROW_2'
					elif rundenWuerfe == 2:
						newState = 'THROW_3'
					else: #Anderer Spieler muss abgegeben haben (eigene Würfe wurden noch nicht zurückgesezt) -> kann nur erst wurf sein
						#Prüfen ob anderer Spieler abgegeben hat
						newState = 'THROW_1'
					setState(newState)#Ändere den Zustand
					logger.warning(f"ZUSTANDS Fehler festgestellt! Wir sind der aktive Spieler, ändere Lokalen Zustand in: {newState}. Zustand Vorher: {curState}.")
					return

		#------------------ Elementar fehler behoben (aka resynced) --------------

		if curState == 'INIT':
			#Init -> Throw Round==1, len(player)==2, player[0].TotalThrowCount == 0, player[1].TotalThrowCount == 0
			if latestGame.ThrowRound == 1: #Runde 1 aka Spiel erste Runde
				if aktPlayer.totalThrowCount == 0:#Kein Spieler hat bisher geworfen -> warten
					return#Lokaler Spieler kann noch nicht bestimmt werden
				else: #Aktive Spieler hat bereits würfe gemacht
					if localPlayer != None: #Der Lokale Spieler wurde bereits bestimmt
						return#Keine Änderung Nötig
					else: #Der lokale Spieler wurde nicht bestimmt, aber aktiv hat würfe -> wir sind der ander Spieler
						localArrID:int = 1 if aktivSpielerArrID==0 else 0#Ist das Gegenteil der Akt. Spieler ID
						localPlayer = createPlayer(latestGame, localArrID)
						setPlayer(localPlayer)
						setState('OTHER_PLAYER')
						logger.info(f"Der andere Spieler hat zu erst geworfen. Lokaler Spieler: ID{localPlayer.uid}, Name:{localPlayer.name}")
						return
			else: #Wir sind bereits in einer höheren Runde (aber immer noch Init aka nachgejoined)
				'''

					TODO: Implement



				'''
				logger.critical("WIR SIND IN EINER HÖHEREN RUNDE NACHGEJOINED. DIES KANN AKTUELL NOCH NICHT BEHANDELT WERDEN")
				return



		if curState == 'UEBERTRITT': 
			if localPlayer != None:
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



		if curState == 'THROW_1' or curState == 'THROW_2' or curState == 'THROW_3': #Wir sind dran und warten auf Wurf
			return;



		if curState == 'OTHER_PLAYER':
			if localPlayer != None:
				if aktPlayer.uid == localPlayer.uid: #Aktiver Spieler sind wieder wir (aka anderer Spieler ist fertig)
					setState('THROW_1')#Wechsel Zustand
					logger.info(f"Der andere Spieler ist fertig. Nun bitte werfen")
					return
				else: #Der andere Spieler ist noch nicht fertig -> warten
					return
			else:#Wir wissen nichtmal wer wir sind, wissen aber aus irgendnem grund, das der andere Dran sit (darf nicht passieren)
				logger.warning("Der Andere Spieler sit dran, aber lokaler Spieler konnte nicht bestimmt werden [SOLLTE SO NICHT EINTRETTEN KÖNNEN]")
				return

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
Prüft periodisch (CHECK_GLOBAL_GAME_INTERVAL) was das Spiel mit höchster UID (neustes aktives Spiel) ist,
und sezt fall neu die loakle uid + player sowie den gamestate entsprechend (wird dann von )
'''
def checkForNewGame():
	global CHECK_GLOBAL_GAME_INTERVAL
	while True:
		fetchedUID = fetchCurrentGamesUID()
		fetchedUID:int = int(fetchedUID) if fetchedUID is not None else None
		if fetchedUID != None:
			if fetchedUID != getUID(): #neues spiel wurde erstellt (vermutlich)
				setUID(fetchedUID)
				setPlayer(None)
				setState('INIT')
				setPreviousGame(None)
		time.sleep(CHECK_GLOBAL_GAME_INTERVAL)
	return





'''
Prüft automatisch alle X Sekunden, ob es für das aktuelle Spiel (aka aktuelle UID),
updates gibt.

Wenn wir der aktuelle Spieler sind, prüft alle CHECK_GAME_UPDATE_INTERVAL_MAX Sekunden
Wenn State==Init, oder der andere Spieler dran -> CHECK_GAME_UPDATE_INTERVAL_MIN sekunden prüfen
'''
def fetchGameUpdates():
	global CHECK_GAME_UPDATE_INTERVAL_MAX, CHECK_GAME_UPDATE_INTERVAL_MIN
	updateInterval:int = 1
	while True:
		curState:str = getState()
		if(curState != 'NG'):
			if curState == 'INIT' or curState == 'OTHER_PLAYER' or curState == 'UEBERTRITT':
				updateInterval = CHECK_GAME_UPDATE_INTERVAL_MIN
			else:
				updateInterval = CHECK_GAME_UPDATE_INTERVAL_MAX
			uid = getUID()

			if uid != None:	
				spiel_update:Spiel = fetchUIDGame(uid)
				checkGameStateChanges(spiel_update) #Prüfe auf neuerungen und wende an falls nötig
				setPreviousGame(spiel_update) #Setze das vorherige Spiel entsprechend
		else: #Es wurde noch keine UID ermittelt, aka kann auch nicht das Spiel prüfen
			updateInterval = CHECK_GAME_UPDATE_INTERVAL_MIN
			logger.warning("Es kann noch kein Spiel update gefetched werden, da noch keine UID fürs aktuelle Spiel ermittelt wurde")

		time.sleep(updateInterval)
	return



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

			#TODO implementiere Neustartmechanismus wenn api verbindung abbricht
			newGameChecker_Thread = threading.Thread(target=checkForNewGame)#Prüft ob ein neues Spiel erstellt wurde
			newGameChecker_Thread.start()
			curGameUpdateCheckker_Thread = threading.Thread(target=fetchGameUpdates)#Prüft ob das aktuelle Spiel updates hat
			curGameUpdateCheckker_Thread.start()

			showGame_Thread = threading.Thread(target=showGame)#Gibt Regelmässig aktuelle Werte fürs Spiel aus
			showGame_Thread.start()
		

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
	return



main()