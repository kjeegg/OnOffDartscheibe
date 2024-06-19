Hier landet das Python Program, welches auf dem Raspberry pi läuft, und folgende funktionen bereitstellt.
- Kommunikation zwischen Arduino und Raspberry pi
- Auswertung der Onboard Kamera des Pis. Aka Lininen erkennung + entsprechende weiterleitung ans Backend
- Weiterleitung des Onboard Kamera Feeds ans Backend 
- Steuerung der LEDs basierend auf aktuelle Ereignisse etc.


Ergänzung zur Arduino/Api Schnittstelle:
Das Program hier soll  die Daten vom Arduino entgegen nehmen, und an die API senden. 
Damit die Zustände Zwischen der Api und dem Pi Synchronisiert werden können, müssen aber einige hilfsfunktionen
implementiert werden, die den Aktuellen Gamestate von der API abfragen, convertieren, und dann intern nutzen.
Da wir in der aktuellen version nur von einem einzigen Spiel ausgehen (und nicht von meheren 
parralell gespielten, kann der einfachheit halber immer das neuste erstellte Spiel, als das aktuelle an genommen werden)
Das Program fragt zyklisch (z.B. alle 3 Sekunden) den aktuellen Gamestate ab.

UPDATE (02.06.2024): Da jezt im Frontend die UIDs nurnoch fest mit inkrementierenden Zähler erstellt werde,
kann einfach ausgelesen werden, welche UID der gefundenen Spiele den höchsten Zählr hat, um fest zu stellen, 
welches das aktuelle aktive Spiel ist


UPDATE (03.06.2024): Ein Fehlwurf wird erstmal als ein Wurf mit 0 Punkten behandelt

UPDATE (16.06.2024): Der Spielerwechsel findet nun an anderer Stelle automatisch statt

UPDATE (17.06.2024): Der Spielerwechsel findet doch wieder hier statt + implementation des ganzen als Statemachine

UPDATE (19.06.2024): Der Pi erhält ein externes LCD sowie Eingabemöglichkeit, um zu spielstart ein exestierendes Spiel,
sowie einen Spieler auswählen zu können. 


Aktuelle Todos:
- [x] Arduino-Pi Schnittstelle
  - [x] Auswertung der Arduino Nachrichten
  - [x] Bestimmung des jeweiligen Gamestates und berechnung des nächsten basierend auf empfangenden Daten
  - [x] Gamestate updates an die API senden
  - [x] Gamestate Updates von der API abfragen
- [ ] Einen Permanenten Connection Check Mechanismus/Daemon integrieren, welcher auch Neustarten + Pausieren kann wenn Verbindungen unterbrochen wurden
- [x] ALLE Zustände vollständig korrekt implementiert
- [ ] LCD Implementaion
- [ ] Externe Eingabe implementation
- [ ] Implementieren eines wechselmechanismus aka ob das Spiel lokal zu verlasssen, und wieder einem anderen beitreten zu können (ohne das Program neustarten zu müssen) 

- [ ] LED Steuerung
- [ ] Camera Linien erkennung und verarbeitung
- [ ] Camera Feed wird an Server weitergesendet



"Optionale" Todos:
- [X] Einen Anständigen Loggings Mechanismus einbauen
- [ ] Den ganzen Code Refactoren und Objektorientiert neu schreiben
- [ ] Ein besseres Exception Handling implementieren
  