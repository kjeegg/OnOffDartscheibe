#!/bin/bash

sudo apt install python3-pip;
sudo apt remove python3-rpi.gpio;
pip3 install rpi-lgpio --break-system-packages;
pip3 install evdev --break-system-packages;
sudo apt install python3-pil;
sudo apt-get install python3-numpy;
pip3 install spidev --break-system-packages;
sudo apt-get remove --purge python3-serial;
sudo apt-get install python3-serial;