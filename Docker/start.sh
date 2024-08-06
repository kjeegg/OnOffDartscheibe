#!/bin/bash

service apache2 start

API_IP=0.0.0.0 API_PORT=8000 DEBUG=TRUE nohup /app/dascr-board/dist/linux_amd64/dascr-board > /app/dascr.log 2>&1 &


tail -f /var/log/apache2/access.log