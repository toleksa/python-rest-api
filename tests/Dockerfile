FROM python:3.12.0-bookworm
RUN apt update && apt upgrade -y && apt install -y python3-pytest libmariadb-dev libmariadb3 \
    && pip install --upgrade pip pylint && apt clean && rm -rf /var/lib/apt/lists/*
WORKDIR /pytest
COPY app app/
COPY www www/
COPY tests/unit/test_unit.py ./
RUN pip install -r app/requirements.txt
CMD pylint app/app.py ; pytest --junit-xml=test_unit.xml test_unit.py

