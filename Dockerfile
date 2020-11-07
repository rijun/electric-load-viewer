FROM ubuntu:latest

RUN apt update && apt install -y python3 python3-pip python3-venv

COPY requirements.txt /app/

WORKDIR /app

RUN pip3 install -r requirements.txt

COPY elv elv
COPY dlp dlp
COPY wsgi.py uwsgi.ini ./

ENV DOCKER_CONTAINER="TRUE"

CMD ["uwsgi", "uwsgi.ini"]
