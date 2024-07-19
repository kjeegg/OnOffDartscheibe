Hier liegt die aktuellste Verrsion des Setups des Projekts via Ansible.

Die Software-Seite des Projektes kann mehr oder weniger Vollständig via Ansible aufgesezt werden. Hierfür Gibt es aber einige Vrorrausetzungen:
1) Ein System Mit Ansible installiert (Die Installation wird hier nicht behandelt)
2) Das Zielsystem (Server), sowie der Pi sind via SSH erreichbar, und haben die Publickeys des aufsezenden Systems authorisiert. (Aka Passwordless Login via SSH ist möglich)
3) Das Hier genuzte Setup nimmt an, das der Zielserver im Internet liegt, und man eine Domain besizt sowie ein CDN (hier beispielweise Cloudflare), welches für die Ende zu Ende Verschlüsselung zwischen Client und Server genuzt wird. Für diese Ende zu Ende Verschlüsselung werden die Public/Private Keys benötigt. Selbige müssen in das Entsprechende Verzeichniss ./Ansible/Dateien/Nginx/cloudflare.\*. Die 2 sich derzeit dort befindenen Keys sind nur Selfsigned, und müssen ensprechend mit den eigenen Ausgetauscht werden. Wie man an die Keys, eine entsprächende Domain, sowie nen Server kommt, kann man sich einfach erGoogeln/Anlesen sowie Cloudflare Konfiguriert werden muss auf die eigene Domain weiter zu leiten etc., dies wird hier nicht weiter behandelt und als gegeben Vorrausgesezt. (Ein lokales Setup ohne CDN etc ist natürlich auch möglich mit eigenene slefsigned Keys, hiefür müssen dann aber natürlich Ips/DNS Namen selber angepasst werden (Kann man sich auch selbst anlesen)

Bevor das ganze aufgesezt werden kann, müssen noch ein paar lokale Änderungen vorgenommen werden, damit das ganze funktioniert:
1) Wie Schon Beschrieben unter ./Ansible/Dateien/Nginx/cloudflare.\* die beiden Keys anpassen
2) Unter ./Ansible/Dateien/Nginx/nginx.conf die eigene Domaine eintragen ("dascr.local" & "api.dascr.local"), sowie den api_access_key ändern. Dieser wird zur Authentifizierung des Pis an der API benuzt.
3) Unter ./Ansible/Dateien/Pi/Files/OnOffDart_v4.py alle nötigen Variablen anpassen (ARDUINO_PORT, API_SERVER_DOMAIN, API_ACCESS_KEY)
4) In der ./Ansible/inventory.yaml Bitte bei Server die IP anpassen, selbiges gilt unter Raspi für die Ip des Rasspberry Pi. Auch wichtig bei Server unter "dascrPlatformMake" die Richtige Architektur aus zu wählen (hierzu bitte mehr im offiziellen Dascr-Github nachlesen https://github.com/dascr/dascr-board unter "Building the backend")
5) In der ./Ansible/ansible.cfg unter invenotry den Pfad zur inventory.yaml, uner private key, selbiges für den auf dem pi/server hinterlegte n ssh key eintragen.

Wenn alle Änderungen vorgenommen wurden, kann das Setup mit ./runAnsible.sh ausgeführt werden. Der Pi dürfte am ende des Setups einmal neustarten. Danach sollte auf dem Angeschlossenden Display die Liste der Vorhanden Spiel auftauchen und Auswählbar sein.
Falls dies nicht ist folgende Lösungen:
1) Es kann sein das die Permissions auf dem Server von /home/dascr/Dascr_Backend/dascr.dbnicht richtige gesezt werden. Hier bitte sicher gehen, das für alle relevanten Nutzer die Datenbank les/schreibar ist
2) Damit das ganze funktioniert, muss auf dem Server MINDESTENS ein Spiel via Frontend gestarted werden