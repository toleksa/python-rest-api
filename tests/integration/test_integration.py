import requests

# methods in requests object:
# https://www.w3schools.com/python/ref_requests_response.asp

def test_server_is_alive():
    response = requests.get("http://webserver:5000/health")
    assert response.status_code == 200

def test_server_logo():
    response = requests.get("http://webserver:5000/logo.png")
    assert response.status_code == 404
#    assert len(response.content) == 11543
#    assert response.ok
#    assert response.is_redirect == False

#def test_server_404():
#    response = requests.get("http://webserver:5000/foobar")
#    assert response.status_code == 404


