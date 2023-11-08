import requests, json
import os

def test_API_URL():
    API_URL=os.environ['API_URL'] #example: http://127.0.0.1:8000
    assert API_URL is not None

def test_WWW_URL():
    WWW_URL=os.environ['WWW_URL'] #example: http://127.0.0.1:8000
    assert WWW_URL is not None

# methods in requests object:
# https://www.w3schools.com/python/ref_requests_response.asp

def test_server_is_alive():
    response = requests.get(os.environ['WWW_URL'])
    assert response.status_code == 200
    assert response.is_redirect == False

def test_API_URL():
    response = requests.get(os.environ['WWW_URL'] + "/api_url.js")
    assert response.status_code == 200
    assert response.is_redirect == False
    assert os.environ['API_URL'] in response.content.decode()


