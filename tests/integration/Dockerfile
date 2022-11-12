FROM alpine:3.16.0
RUN apk add --no-cache python3 py3-pytest py3-requests

WORKDIR /pytest
COPY app app/
COPY tests/integration/test_integration.py ./
CMD pytest --junit-xml=test_integration.xml test_integration.py


