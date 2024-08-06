#!/bin/bash
sudo apt install python3-pip;
sudo apt install python3-pil;
sudo apt install python3-numpy;
sudo apt-get install python3-serial
pip3 install rpi-lgpio --break-system-packages;
pip3 install evdev --break-system-packages;
pip3 install spidev --break-system-packages;