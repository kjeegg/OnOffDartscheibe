Hier landet das Python Program, welches auf dem Raspberry pi läuft, und folgende funktionen bereitstellt.
- Kommunikation zwischen Arduino und Raspberry pi
- Auswertung der Onboard Kamera des Pis. Aka Lininen erkennung + entsprechende weiterleitung ans Backend
- Weiterleitung des Onboard Kamera Feeds ans Backend 
- Steuerung der LEDs basierend auf aktuelle Ereignisse etc.

Aktuelle Todos:
	- [ ] Arduino-Pi Schnittstelle
		- [ ] Auswertung der Arduino Nachrichten + versnad and API
		- [ ] Übermittlung nötiger Steuerbefehle an den Arduino
	- [ ] LED Steuerung
	- [ ] Camera Linien erkennung und verarbeitung
	- [ ] Camera Feed wird an Server weitergesendet