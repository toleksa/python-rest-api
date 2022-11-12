import requests

# methods in requests object:
# https://www.w3schools.com/python/ref_requests_response.asp

def test_server_is_alive():
    response = requests.get("http://webserver/health")
    assert response.status_code == 200

def test_server_logo():
    response = requests.get("http://webserver/logo.png")
    assert response.status_code == 200
    assert len(response.content) == 11543
    assert response.ok
    assert response.is_redirect == False

def test_server_404():
    response = requests.get("http://webserver/foobar")
    assert response.status_code == 404


