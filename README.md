Der Unten gennante Teil ist nur nötig, falls das Gesammte Setup neu aufgesezt werden soll. 
Wenn schon ein das Vollständige Setup exestiert (Wie z.B: bei der Abschlusspräsentation), muss nur ein Teil Angepasst werden:
1) Das Gesammtsetup für "Auf dem PC" von Unten, bis vors Bespielen der SD Karten (ab da nichtmehr).
2) Auf den PIs (einfach Bildschirm und Tastatur anschließen):
2.1) In das Eigene Wlan einloggen
2.2) In der OnOffDart_v4.py (sollte sich auf dem Desktop in einem Unterverzeichniss befinden). Die API Domain in der Datei wie unten Beschrieben auf die IP des PCs ändern.
3) Da hier der automatische Service nicht installiert ist, muss das Program manuell gestarted werden mit "python3 OnOffDart_v4.py"




----------------------------------------------------------------------------------------------------------------------------


Das folgende Lokale Setup ist prinzipiell nicht für den Zugriff aus dem Internet gedacht!. Es Handelt sich um ein möglichst simples lokales Setup, zum testen/nutzen im einem lokalen/Privaten Netzwerk.

**<ins>Vorraussetzung:</ins>**

- PC (Windows 10+) + SD-Karten Adapter
- 2x Raspberry Pi's (jeweils 1x Pro Dartscheibe) + SD-Karten + (evtl USB Stick)
- Einen Wifi AP als lokales Netzwerk. Alternativ ein Ethernet LAN, in welchem man Kontrolle über den DHCP hat, und alle Endgeräte zueinander erreichbar sind
- Zugang zum Internet für alle Endgeräte (z.B. via dem AP für Updates + initiale Installation)



**<ins>Setup:</ins>**
**<ins>Allgemein:</ins>**

Die Idee beim nachfolgenden Setup ist folgende:
Nutze einen Wifi AP (z.B. Hotspot eines Mobilen Endgeräts (z.B. Smartphone)), zur Installation/dem Setup aller Komponenten. Danach kann das durch den AP gegebene Netzwerk zur lokalen Kommunikation der einzelnen Endkomponenten (Server, Dartscheiben, Endgeräte die aufs Webinterface zugreifen), genuzt werden.

Um das Setup möglichst zu vereinfachen nutzen wir hier nicht das Ansible Playbook, des vollständigen, externen Setups, sondern ein einfachse Bash Script zum aufsetzen der Raspberry Pis.
Der Eigentliche Server (für Frontend + Backend) wird auf dem aufsezen Windows PC, als Docker Container, zum laufen gebracht. 
Beim Lokalen Setup, benötigt man im Gegensatz zum vollständigen Setup, keinen Proxy Server (Nginx), sowie auch keine Domain + CDN. 
Wichtig ist hier jedoch die Erreichbarkeit aller Endkomponenten im lokalen Netzwerk (Daher die Nutzung eines privaten APs, überwelchen  man  die volle Kontrolle haben sollte). 



**<ins>Auf dem PC:</ins>**

Da wir für den Server Docker nutzen, müssen wir dieses zuerst auf unserem System installieren. Hiefür einfach den Installationsaleitungen auf der Offiziellen Seite folgen (https://www.docker.com/products/docker-desktop/).
Nach erfolgreicher installation, können wir die Commandline (cmd) nutzen, um den Container einmal zu bauen. Hierfür öffnen wir die CMD, und bewegen uns im heruntergeladenen Verzeichniss ins Unterverzeichniss "./Docker".
Nun können wir in der CMD einfach "docker compose build" eingeben. Hierdurch wird die im Verzeichniss liegende "compose.yaml" genuzt, um den Container zu bauen. (ACHTUNG! Der Vorgang kann beim ersten mal je nach Internet und System recht lange dauern).
Wenn der Process abgeschlossen ist, können wir "docker compose up -d" eingeben, um den gebaaten Container zu starten.
Hiernach kann die Console wieder geschlossen werden. (Ein zuküntiges starten/stoppen des Containers ist auch direkt in Docker Desktop möglich. Hier kann auch der Status des Containers eingesehen werden)

Um entwaige Änderungen/Aktualisierungen im Frontend um zu setzen, können einfach im Frontend Ordner unter "./Docker/Frontend" die Änderungen vorgenommen werden. (Diese werden sofort im laufenden Container übernommen. Achtung Anpassungen vom anderen Setup müssen unter umständen erst lokal angepasst werden, aka domains, ssl etc.)

Um zu testen ob der Container korrekt läuft, kann im lokalen Browser auf dem PC, einfach "http://localhost" aufgerufen werden (bzw http://localhost:8000/api für die api)

Um die Verbindung von anderen Geräten zu zu lassen, müssen wir noch in der Firewall die entsprechenden Ports (80 und 8000) für eingehende Verbindungen öffnen. Hierzu bitte einfach googeln, wie dies unter dem aktuell genuzten System funktioniert (z.B. bei Windows in der Windows Defender Firewall).
Wenn dies korrekt umgesetzt wurde, kann versucht werden, von anderen Geräten im SELBEN Netzwerk auf die Seite zuzugreifen. Hiefür einfach im entsprechenden Browser die private ipv4 Addresse des PCs eingeben aka z.B. wenn der Rechner z.B. 192.168.1.5 ist dann "http://192.168.1.5" (bzw http://192.168.1.5:8000/api für die API). Wenn dies funktioniert, wurde hier alles korrekt konfiguriert.
(Die IP des Systems kann entweder im Router nachgesehen werden, oder z.B. unter Windows in der CMD mit dem Befehl "ipconfig")

Um nun die SD Karte für die Raspberry PIs zu bespielen, wie folgt vorgehen: 
1) Sich den "Raspberry Pi Imager" von der Offiziellen Seiter herunterladen und installieren (https://www.raspberrypi.com/software/)
2) Die für den jeweiligen Pi genuzte SD Karte an den PC anschließen.
3.1) Den "Raspberry Pi Imager" öffnen und als Device "Raspberry pi 5" wählen
3.2) Als OS unter "Raspberry Pi OS (64Bit)" wählen.
3.3) Die SD Karte als Ziel wählen
3.4) Bei der Frage nach Einstellungen wie folgt vorgehen:
3.4.1) Fürs Wlan die ensprechenden login Informationen des Geteilten APs nutzen
3.4.2) Für den Login SSH aktivieren und als Nutzernamen pi wählen. Als Passwort irgendetwas gut merkbares (im Rahmen geltender Passwortrichtlinien!)
3.5) Nun einfach die Einstellungen übernehmen und die SD Karte bespielen, und wieder in den Pi einsetzen, sowie selbigen starten (Strom anschließen)
3.6) Selbiges für den anderen Pi wiederholen


Nun gibt es mehere Wege weiter vor zu gehen. Entweder Remote via SSH/VNC Verbindung zu den PIs, oder alternativ direkt an den Pis selber. Hiefür ist aber ein Angschlossender Bildschirm sowie Tastatur und Maus von nöten. Im folgenden gehe ich nur auf das Setup direkt auf den Pis ein.
Hierfür muss zuerst einmal der Ordner "./PIs" auf einen USB-Stick übertragen werden.



**<ins>Auf den Pis:</ins>**

Nach dem ersten start, falls nötig einloggen. 
Nun den USB Stick anschließen, und den Ordner auf den Desktop ziehen.
Bevor wir das Setup starten können, müssen wir noch kurz eine kleine Änderung vornehmen. Hiefür in dem Ordner die Folgende Datei in einem Texteditor öffnen "./PIs/Dateien/Python/OnOffDart_v4.py", in selbiger nach der Zeile "API_SERVER_DOMAIN:str = "https://api.onoff-dart.de/api" suchen. Hier dann das "https://api.onoff-dart.de/api" bitte wie folgt ersetzen: "http://<HIER BITTE DIE IP ADDRESSE DES PCs>:8000/api" (Wichtig: keine <>, das ":8000" "muss dahin, und das http statt dem https)

Nun müssen wir noch SPI (für das LCD) aktivieren. Hierzu im Terminal einmal "sudo raspi-config" eingeben, und unter 
"3 Interface Options" -> "I4 SPI" -> "YES" -> "FINISH" um SPI zu aktivieren.
Wenn dies gemacht wurde, einfach ein Terminal im Ordner (./PIs) öffnen, und das Setup script mit sudo ausführen aka: "sudo setup.sh" (falls es hier sofort ne Fehlermeldung bzgl ausführbarkeit gibt vorher nochmal kurz ein "sudo chmod +x ./setup.sh" ausführen)
Im Idealfall sollte, wenn das Script Fehlerfrei durchgelaufen ist (der Pi started dabei einmal am ende neu), nun alles eingerichtet sein, und auf dem LCDs ein Spielauswahl erscheinen.
(Das Program dürfte nach jedem neustart des Pis gleich mitstarten, aktuell ist es noch von nöten, um ein Spiel an der Scheibe zu verlassen, (aka Spielwechsel), den Pi neuzustarten (einfach powercyclen)).




**<ins>Für Zukünftige Spiele:</ins>**

Es ist nurnoch nötig den Docker Container zu starten, und alle Geräte im selben Netzwerk unter zu bringen (bei veränderter IP Addresse des PCs, ist es nötig diese natürlich auf den PIs wieder an zu passen (in der Python Datei, diese liegt aber nun unter ~/OnOffDart_v4.py)).
Das Einschalten der Stromverbindung für die Dartscheibe sollte die Pis automatisch starten lassen.