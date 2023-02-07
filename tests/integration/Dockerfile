FROM alpine:3.16.0
RUN apk add --no-cache python3 py3-pytest py3-requests py3-prometheus-client curl

WORKDIR /pytest
COPY tests/integration/test_integration.py tests/integration/test_www.py tests/integration/test_prometheus.py ./
CMD pytest --junit-xml=test_integration.xml test_integration.py ; pytest --junit-xml=test_www.xml test_www.py ; pytest --junit-xml=test_prometheus.xml test_prometheus.py

