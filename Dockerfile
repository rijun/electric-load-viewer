FROM tiangolo/meinheld-gunicorn-flask:python3.8

WORKDIR /app

COPY wsgi.py requirements.txt /app/

RUN python3 -m pip install -r requirements.txt

COPY elv elv
COPY dlp dlp

ENV APP_MODULE="wsgi:server"
ENV DOCKER_CONTAINER="TRUE"