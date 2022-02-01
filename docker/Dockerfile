# Dockerfile

FROM python:3.10.2-slim-bullseye
RUN apt-get update
RUN apt-get install -y libmariadb-dev gcc
RUN /usr/local/bin/python -m pip install --upgrade pip
RUN pip install flask mariadb
RUN ln -sf /usr/share/zoneinfo/Europe/Zurich /etc/localtime

EXPOSE 5000
STOPSIGNAL SIGTERM

WORKDIR /app
COPY app/rest.py app/start.sh ./
CMD /app/start.sh

