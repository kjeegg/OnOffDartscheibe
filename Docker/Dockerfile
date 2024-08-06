FROM dslim/docker-slim

RUN apt-get update && \
    apt-get install -y apache2 php python3 git build-essential gcc make sqlite3 golang python3-requests python3-fake-factory   && \
    apt-get clean

COPY ./Frontend /var/www/html


WORKDIR /app
RUN git clone https://github.com/dascr/dascr-board

COPY ./env /app/dascr-board/.env
COPY ./env /app/dascr-board/frontend/.env

WORKDIR /app/dascr-board

RUN make build-linux_64

EXPOSE 80
EXPOSE 8000

RUN a2enmod php8.2

COPY ./start.sh /app/start.sh

RUN chmod +x /app/start.sh


RUN echo "ServerName localhost" >> /etc/apache2/apache2.conf


#&& API_IP=0.0.0.0 API_PORT=8000 DEBUG=TRUE /app/dascr-board/dist/linux_64/
CMD ["/app/start.sh"]