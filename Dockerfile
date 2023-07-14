# Dockerfile

FROM python:3.11.5-alpine3.18 
COPY app/requirements.txt /requirements.txt
RUN apk add --no-cache --virtual build-deps build-base \
    && apk add --no-cache mariadb-connector-c-dev \
    && pip install -r /requirements.txt \
    && apk del build-deps
RUN ln -sf /usr/share/zoneinfo/Europe/Zurich /etc/localtime

EXPOSE 5000
STOPSIGNAL SIGTERM

WORKDIR /app
COPY app/app.py app/start.sh ./
CMD /app/start.sh

