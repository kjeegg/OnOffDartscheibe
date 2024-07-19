import requests
import json
from faker import Faker
import random
from requests.packages.urllib3.exceptions import InsecureRequestWarning

api_url = f"http://localhost:8000"

requests.packages.urllib3.disable_warnings(InsecureRequestWarning) #Schaltet TLS warnungen aus




#--------------------------------------------------------------------------------------

def createPlayer(name, nick):
	daten = {
	  "name": name,
	  "nickname": nick
	}
	daten = json.dumps(daten)
	response = requests.post(f"{api_url}/api/player", data=daten, headers={'Content-Type': 'application/json'}, verify=False)
	return [response.status_code, response.text]


def deletePlayer(id):
	response = (requests.delete(f"{api_url}/api/player/{id}", verify=False))
	return [response.status_code, response.text]

def getPlayers():
	response = (requests.get(f"{api_url}/api/player", verify=False))
	return [response.status_code, response.text]


#--------------------------------------------------------------------------------------

def getGames():
	response = (requests.get(f"{api_url}/api/game/", verify=False))
	return [response.status_code, response.text]

def deleteGame(uid):
	response = (requests.delete(f"{api_url}/api/game/{uid}", verify=False))
	return [response.status_code, response.text]

def getGame(id):
	response = (requests.get(f"{api_url}/api/game/{id}", verify=False))
	return [response.status_code, response.text]

def createGame(id, uid, player1_id, player2_id):
	daten = {
    "uid": uid,
    "player": [player1_id,player2_id],
    "game": "x01",
    "variant": "501",
    "in": "straight",
    "out": "double",
    "sound": True,
    "podium": False,
    "autoswitch": False,
    "cricketrandom": False,
    "cricketghost": False
	}	
	daten = json.dumps(daten)
	response = requests.post(f"{api_url}/api/game/{id}", data=daten, headers={'Content-Type': 'application/json'}, verify=False)
	return [response.status_code, response.text]

def sendThrow(uid, number, modifier):
	response = (requests.post(f"{api_url}/api/game/{uid}/throw/{number}/{modifier}",verify=False))
	return [response.status_code, response.text]

def switchPlayer(uid):
	response = requests.post(f"{api_url}/api/game/{uid}/nextPlayer", verify=False)
	return [response.status_code, response.text]
#--------------------------------------------------------------------------------------	

def main():

	fake = Faker()

	#Erstelle 20 random Spieler
	namen = [fake.first_name() for _ in range(20)]
	nicknames = [fake.name() for _ in range(20)]
	for i in range(len(namen)):
		print(createPlayer(namen[i], nicknames[i]))

	#Erzeuge 10 Spiele
	for i in range(10):
		player1 = random.randint(0, 19)
		print(createGame(i, f'{i}', player1, (player1+1)))
	

	#Erzeuge für alle Spiele eine Anzahl an runden
	games = (requests.get(f"{api_url}/api/game", verify=False)).json()
	for i in range(len(games)): #iteriere über spiele
		uid = games[i]['uid']
		rundenzahl = random.randint(0, 10)#Erzeuge zwischen 0 und 10 runden
		for runde in range(rundenzahl):
			wert = random.randint(0, 20)#Erzeugen wert zwischen 0 und 20
			modifier = random.randint(1, 3)#Erzeuge wert zwischen 1 und 3
			print(sendThrow(uid, wert, modifier))
			switchPlayer(uid)#spielerwechsel
			
main()


