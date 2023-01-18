from prometheus_client.parser import text_string_to_metric_families
import requests, json
import os

def test_API_URL():
    API_URL=os.environ['API_URL'] #example: http://127.0.0.1:8000
    assert API_URL is not None

# methods in requests object:
# https://www.w3schools.com/python/ref_requests_response.asp

def test_server_is_alive():
    response = requests.get(os.environ['API_URL'] + "/health")
    assert response.status_code == 200
    assert response.is_redirect == False

def test_main():
    response = requests.get(os.environ['API_URL'] + "/")
    assert response.status_code == 200 #TODO: should be 302 o.O
    assert response.is_redirect == False  #TODO: should be True

def test_server_404():
    response = requests.get(os.environ['API_URL'] + "/foobar")
    assert response.status_code == 404
    assert response.is_redirect == False

def test_CORS_header():
    response = requests.get(os.environ['API_URL'] + "/data")
    assert "Access-Control-Allow-Origin" in response.headers

def test_post_empty():
    payload = {'': ''}
    response = requests.post(os.environ['API_URL'] + "/data/add", json=payload)
    assert response.status_code == 400
    assert response.is_redirect == False

def test_reset1():
    response = requests.get(os.environ['API_URL'] + "/reset")
    assert response.status_code == 204
    assert response.is_redirect == False

def test_select_cache1():
    response = requests.get(os.environ['API_URL'] + "/cache")
    assert response.status_code == 200
    assert response.json() == []
    assert response.is_redirect == False

def test_select_all1():
    response = requests.get(os.environ['API_URL'] + "/data")
    assert response.status_code == 200
    assert response.is_redirect == False
    result = [['Homer','Simpson'],['Jeffrey','Lebowski'],['Stan','Smith']]
    assert response.json() == result

def test_post1():
    payload = {'Tiger': 'Woods'}
    response = requests.post(os.environ['API_URL'] + "/data/add", json=payload)
    assert response.status_code == 204
    assert response.is_redirect == False

def test_select_all2():
    response = requests.get(os.environ['API_URL'] + "/data")
    assert response.status_code == 200
    assert response.is_redirect == False
    result = [['Homer','Simpson'],['Jeffrey','Lebowski'],['Stan','Smith'],['Tiger','Woods']]
    assert response.json() == result

def test_select_cache2():
    response = requests.get(os.environ['API_URL'] + "/cache")
    assert response.status_code == 200
    assert response.json() == []
    assert response.is_redirect == False

def test_reset2():
    response = requests.get(os.environ['API_URL'] + "/reset")
    assert response.status_code == 204
    assert response.is_redirect == False

def test_select_all3():
    response = requests.get(os.environ['API_URL'] + "/data")
    assert response.status_code == 200
    assert response.is_redirect == False
    result = [['Homer','Simpson'],['Jeffrey','Lebowski'],['Stan','Smith']]
    assert response.json() == result

def test_select_Homer1():
    response = requests.get(os.environ['API_URL'] + "/data/Homer")
    assert response.status_code == 200
    assert response.json()[1] == "Simpson"
    result = ['Homer', 'Simpson']
    assert response.json() == result
    assert response.is_redirect == False

def test_select_cache3():
    response = requests.get(os.environ['API_URL'] + "/cache")
    assert response.status_code == 200
    assert response.is_redirect == False
    result = ['Homer', 'Simpson']
    assert response.json()[0] == result

def test_post2():
    payload = {'Winnie': 'Pooh'}
    response = requests.post(os.environ['API_URL'] + "/data/add", json=payload)
    assert response.status_code == 204
    assert response.is_redirect == False

def test_select_cache4():
    response = requests.get(os.environ['API_URL'] + "/cache")
    assert response.status_code == 200
    assert response.is_redirect == False
    result = ['Homer', 'Simpson']
    assert response.json()[0] == result

def test_select_Winnie():                                                                                                                                                                  
    response = requests.get(os.environ['API_URL'] + "/data/Winnie")                                                                                                                       
    assert response.status_code == 200                                                                                                                                                     
    assert response.json()[1] == "Pooh"                                                                                                                                                 
    result = ['Winnie', 'Pooh']                                                                                                                                                            
    assert response.json() == result                                                                                                                                                    
    assert response.is_redirect == False  

def test_select_cache5():                                                                                                                                                                  
    response = requests.get(os.environ['API_URL'] + "/cache")
    assert response.status_code == 200
    assert response.is_redirect == False
    result = [['Winnie', 'Pooh'],['Homer', 'Simpson']]
    sorted_result = sorted(result)
    sorted_response = sorted(response.json())
    assert sorted_response == sorted_result

def test_select_all4():
    response = requests.get(os.environ['API_URL'] + "/data")
    assert response.status_code == 200
    assert response.is_redirect == False
    result = [['Homer','Simpson'],['Jeffrey','Lebowski'],['Stan','Smith'],['Winnie','Pooh']]
    assert response.json() == result

def test_delete_error1():
    response = requests.delete(os.environ['API_URL'] + "/data")
    assert response.status_code == 405
    assert response.is_redirect == False

def test_delete_error2():
    response = requests.delete(os.environ['API_URL'] + "/data/del")
    assert response.status_code == 405
    assert response.is_redirect == False

def test_delete1():
    response = requests.delete(os.environ['API_URL'] + "/data/del/Winnie")
    assert response.status_code == 204
    assert response.is_redirect == False

def test_delete2():
    response = requests.delete(os.environ['API_URL'] + "/data/del/Winnie")
    assert response.status_code == 204
    assert response.is_redirect == False

def test_delete3():
    response = requests.delete(os.environ['API_URL'] + "/data")
    assert response.status_code == 405
    assert response.is_redirect == False

def test_select_all5():
    response = requests.get(os.environ['API_URL'] + "/data")
    assert response.status_code == 200
    assert response.is_redirect == False
    result = [['Homer','Simpson'],['Jeffrey','Lebowski'],['Stan','Smith']]
    assert response.json() == result

def test_select_cache6():                                                                                                                                                                  
    response = requests.get(os.environ['API_URL'] + "/cache")
    assert response.status_code == 200
    assert response.is_redirect == False
    result = [['Homer', 'Simpson']]
    sorted_result = sorted(result)
    sorted_response = sorted(response.json())
    assert sorted_response == sorted_result

def test_put_error1():
    response = requests.put(os.environ['API_URL'] + "/data/put")
    assert response.status_code == 405
    assert response.is_redirect == False

def test_put1():
    response = requests.put(os.environ['API_URL'] + "/data/put/Marco/value/Chad")
    assert response.status_code == 404
    assert response.is_redirect == False

def test_put2():
    response = requests.put(os.environ['API_URL'] + "/data/put/Homer/value/Chad")
    assert response.status_code == 204
    assert response.is_redirect == False

def test_select_Homer2():
    response = requests.get(os.environ['API_URL'] + "/data/Homer")
    assert response.status_code == 200
    assert response.json()[1] == "Chad"
    result = ['Homer', 'Chad']
    assert response.json() == result
    assert response.is_redirect == False

def test_select_all6():
    response = requests.get(os.environ['API_URL'] + "/data")
    assert response.status_code == 200
    assert response.is_redirect == False
    result = [['Homer','Chad'],['Jeffrey','Lebowski'],['Stan','Smith']]
    assert response.json() == result

def test_put3():
    response = requests.put(os.environ['API_URL'] + "/data/put/Homer/value/Simpson")
    assert response.status_code == 204
    assert response.is_redirect == False

def test_select_all7():
    response = requests.get(os.environ['API_URL'] + "/data")
    assert response.status_code == 200
    assert response.is_redirect == False
    result = [['Homer','Simpson'],['Jeffrey','Lebowski'],['Stan','Smith']]
    assert response.json() == result

def test_metrics1():
    response = requests.get(os.environ['API_URL'] + "/metrics")
    assert response.status_code == 200
    assert response.is_redirect == False
    assert "requests_total" in response.content.decode()
    assert "responses_total" in response.content.decode()
    metrics = text_string_to_metric_families(response.content.decode())
    for metric in metrics:
        #print("Metric name: ", metric.name)
        for sample in metric.samples:
            #print("\tSample: ", sample.name, sample.labels, sample.value)
            if sample.name == "requests_total" and sample.labels == {'endpoint': '/data', 'method': 'GET'}:
                assert sample.value == 50
            if sample.name == "responses_total" and sample.labels == {'endpoint': '/data/del/Winnie', 'status_code': '204'}:
                assert sample.value == 2


