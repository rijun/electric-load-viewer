# docker run -p 80:80 -v "$(pwd)"/itp.db:/app/itp.db --rm -d elv

FROM ubuntu:latest

WORKDIR /app

COPY requirements.txt /app/

RUN apt update && apt install -y \
    python3 \
    python3-pip \
    python3-venv \
&& python3 -m venv venv \
&& venv/bin/pip3 install -r requirements.txt

COPY elv elv
COPY dlp dlp
COPY wsgi.py uwsgi.ini ./

ENV DOCKER_CONTAINER="TRUE"

RUN groupadd -r pi && useradd --no-log-init -r -g pi pi

CMD ["venv/bin/uwsgi", "uwsgi.ini"]
