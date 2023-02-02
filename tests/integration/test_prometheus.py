import requests, json
import os

def test_PROMETHEUS_URL():
    PROMETHEUS_URL=os.environ['PROMETHEUS_URL'] #example: http://127.0.0.1:9090
    assert PROMETHEUS_URL is not None

def test_prometheus():
    response = requests.get(os.environ['PROMETHEUS_URL'] + "/api/v1/query?query=python_rest_api_responses_total")
    assert response.status_code == 200
    assert response.is_redirect == False
    results = response.json()['data']['result']
    assert results != []
    for result in results:
      if result['metric']['endpoint'] == "/cache":
        assert result['value'][1] == '4'
      if result['metric']['endpoint'] == "/data":
        if result['metric']['status_code'] == 200:
          assert result['value'][1] == '5'
        if result['metric']['status_code'] == 405:
          assert result['value'][1] == '2'

