FROM alpine:3.18.4
RUN apk add --no-cache python3 py3-pytest py3-pylint

WORKDIR /pytest
COPY app app/
COPY www www/
COPY tests/unit/test_unit.py ./
CMD pylint app/app.py ; pytest --junit-xml=test_unit.xml test_unit.py

