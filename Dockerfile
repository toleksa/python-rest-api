# Dockerfile

FROM python:3.10.2-slim-bullseye
RUN pip install flask
RUN ln -sf /usr/share/zoneinfo/Europe/Zurich /etc/localtime

EXPOSE 5000
STOPSIGNAL SIGTERM

WORKDIR /app
COPY rest.py start.sh .
CMD /app/start.sh

