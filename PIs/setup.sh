#!/bin/bash
#updates
sudo apt update;
sudo apt upgrade -y;
sudo apt autoremove -y;
#Packete installieren
sudo apt install python3 python3-pip python3-pil python3-numpy build-essential git scons make python3-serial libopencv-dev python3-opencv -y;
#Nutzer Zugang zu Serieller Schnittstelle geben
sudo usermod -aG dialout pi;
#Python Pakete installieren
sudo pip3 install rpi_ws281x rpi-lgpio evdev spidev adafruit-circuitpython-neopixel-spi --break-system-packages;
#Dateien an ihre Vorbestimmten Orte unterbringen
sudo cp -r ./Dateien/Python/* ~/;
sudo cp ./Dateien/raspy-dascr.service /etc/systemd/system/;
#Service AUfsetzten
sudo systemctl daemon-reload;
sudo systemctl enable raspy-dascr.service;
sudo systemctl start raspy-dascr.service;
sudo reboot now;
