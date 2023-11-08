FROM python:3.12.0-bookworm
RUN apt update && apt upgrade -y && apt install -y libmariadb-dev libmariadb3 curl\
    && pip install --upgrade pip pylint pytest requests && apt clean && rm -rf /var/lib/apt/lists/*
WORKDIR /pytest
COPY app app/
COPY www www/
COPY tests/test* ./
RUN pip install -r app/requirements.txt
CMD pylint app/app.py ;\
 pytest --junit-xml=test_unit.xml test_unit.py ;\
 pytest --junit-xml=test_integration.xml test_integration.py ;\
 pytest --junit-xml=test_www.xml test_www.py ;\
 pytest --junit-xml=test_prometheus.xml test_prometheus.py

