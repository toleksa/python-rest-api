# Dockerfile

FROM python:3.10.2-slim-bullseye
RUN apt-get update \
    && apt-get install -y libmariadb-dev gcc \
    && /usr/local/bin/python -m pip install --upgrade pip \
    && pip install flask=2.2.2 mariadb==1.0.11 \
    && apt-get remove -y gcc \
    && apt-get autoremove -y \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*
RUN ln -sf /usr/share/zoneinfo/Europe/Zurich /etc/localtime

EXPOSE 5000
STOPSIGNAL SIGTERM

WORKDIR /app
COPY app/rest.py app/start.sh ./
CMD /app/start.sh

