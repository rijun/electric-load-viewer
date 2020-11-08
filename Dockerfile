# docker run -p 80:80 -v "$(pwd)"/itp.db:/app/itp.db --rm elv

FROM ubuntu:latest

RUN apt update && apt install -y python3 python3-pip python3-venv

COPY requirements.txt /app/

WORKDIR /app

RUN pip3 install -r requirements.txt

COPY elv elv
COPY dlp dlp
COPY wsgi.py uwsgi.ini ./

ENV DOCKER_CONTAINER="TRUE"

RUN groupadd -r pi && useradd --no-log-init -r -g pi pi

CMD ["uwsgi", "uwsgi.ini"]
