import requests, json

# methods in requests object:
# https://www.w3schools.com/python/ref_requests_response.asp

def test_server_is_alive():
    response = requests.get("http://api:5000/health")
    assert response.status_code == 200
    assert response.is_redirect == False

def test_main():
    response = requests.get("http://api:5000/")
    assert response.status_code == 200 #TODO: should be 302 o.O
    assert response.is_redirect == False  #TODO: should be True

def test_server_404():
    response = requests.get("http://api:5000/foobar")
    assert response.status_code == 404
    assert response.is_redirect == False

def test_reset1():
    response = requests.get("http://api:5000/reset")
    assert response.status_code == 204
    assert response.is_redirect == False

def test_select_cache1():
    response = requests.get("http://api:5000/cache")
    assert response.status_code == 200
    assert response.json() == []
    assert response.is_redirect == False

def test_select_all1():
    response = requests.get("http://api:5000/data")
    assert response.status_code == 200
    assert response.is_redirect == False
    result = [['Homer','Simpson'],['Jeffrey','Lebowski'],['Stan','Smith']]
    assert response.json() == result

def test_post1():
    payload = {'Tiger': 'Woods'}
    response = requests.post("http://api:5000/data/add", json=payload)
    assert response.status_code == 204
    assert response.is_redirect == False

def test_select_all2():
    response = requests.get("http://api:5000/data")
    assert response.status_code == 200
    assert response.is_redirect == False
    result = [['Homer','Simpson'],['Jeffrey','Lebowski'],['Stan','Smith'],['Tiger','Woods']]
    assert response.json() == result

def test_select_cache2():
    response = requests.get("http://api:5000/cache")
    assert response.status_code == 200
    assert response.json() == []
    assert response.is_redirect == False

def test_reset2():
    response = requests.get("http://api:5000/reset")
    assert response.status_code == 204
    assert response.is_redirect == False

def test_select_all3():
    response = requests.get("http://api:5000/data")
    assert response.status_code == 200
    assert response.is_redirect == False
    result = [['Homer','Simpson'],['Jeffrey','Lebowski'],['Stan','Smith']]
    assert response.json() == result

def test_select_Homer1():
    response = requests.get("http://api:5000/data/Homer")
    assert response.status_code == 200
    assert response.json()[1] == "Simpson"
    result = ['Homer', 'Simpson']
    assert response.json() == result
    assert response.is_redirect == False

def test_select_cache3():
    response = requests.get("http://api:5000/cache")
    assert response.status_code == 200
    assert response.is_redirect == False
    result = ['Homer', 'Simpson']
    assert response.json()[0] == result

def test_post2():
    payload = {'Winnie': 'Pooh'}
    response = requests.post("http://api:5000/data/add", json=payload)
    assert response.status_code == 204
    assert response.is_redirect == False

def test_select_cache4():
    response = requests.get("http://api:5000/cache")
    assert response.status_code == 200
    assert response.is_redirect == False
    result = ['Homer', 'Simpson']
    assert response.json()[0] == result

def test_select_Winnie():                                                                                                                                                                  
    response = requests.get("http://api:5000/data/Winnie")                                                                                                                       
    assert response.status_code == 200                                                                                                                                                     
    assert response.json()[1] == "Pooh"                                                                                                                                                 
    result = ['Winnie', 'Pooh']                                                                                                                                                            
    assert response.json() == result                                                                                                                                                    
    assert response.is_redirect == False  

def test_select_cache5():                                                                                                                                                                  
    response = requests.get("http://api:5000/cache")
    assert response.status_code == 200
    assert response.is_redirect == False
    result = [['Winnie', 'Pooh'],['Homer', 'Simpson']]
    sorted_result = sorted(result)
    sorted_response = sorted(response.json())
    assert sorted_response == sorted_result

def test_select_all4():
    response = requests.get("http://api:5000/data")
    assert response.status_code == 200
    assert response.is_redirect == False
    result = [['Homer','Simpson'],['Jeffrey','Lebowski'],['Stan','Smith'],['Winnie','Pooh']]
    assert response.json() == result

def test_delete_error1():
    response = requests.delete("http://api:5000/data")
    assert response.status_code == 405
    assert response.is_redirect == False

def test_delete_error2():
    response = requests.delete("http://api:5000/data/del")
    assert response.status_code == 405
    assert response.is_redirect == False

def test_delete1():
    response = requests.delete("http://api:5000/data/del/Winnie")
    assert response.status_code == 204
    assert response.is_redirect == False

def test_delete2():
    response = requests.delete("http://api:5000/data/del/Winnie")
    assert response.status_code == 204
    assert response.is_redirect == False

def test_delete3():
    response = requests.delete("http://api:5000/data")
    assert response.status_code == 405
    assert response.is_redirect == False

def test_select_all5():
    response = requests.get("http://api:5000/data")
    assert response.status_code == 200
    assert response.is_redirect == False
    result = [['Homer','Simpson'],['Jeffrey','Lebowski'],['Stan','Smith']]
    assert response.json() == result

def test_select_cache6():                                                                                                                                                                  
    response = requests.get("http://api:5000/cache")
    assert response.status_code == 200
    assert response.is_redirect == False
    result = [['Homer', 'Simpson']]
    sorted_result = sorted(result)
    sorted_response = sorted(response.json())
    assert sorted_response == sorted_result

def test_put_error1():
    response = requests.put("http://api:5000/data/put")
    assert response.status_code == 405
    assert response.is_redirect == False

def test_put1():
    response = requests.put("http://api:5000/data/put/Marco/value/Chad")
    assert response.status_code == 404
    assert response.is_redirect == False

def test_put2():
    response = requests.put("http://api:5000/data/put/Homer/value/Chad")
    assert response.status_code == 204
    assert response.is_redirect == False

def test_select_Homer2():
    response = requests.get("http://api:5000/data/Homer")
    assert response.status_code == 200
    assert response.json()[1] == "Chad"
    result = ['Homer', 'Chad']
    assert response.json() == result
    assert response.is_redirect == False

def test_select_all6():
    response = requests.get("http://api:5000/data")
    assert response.status_code == 200
    assert response.is_redirect == False
    result = [['Homer','Chad'],['Jeffrey','Lebowski'],['Stan','Smith']]
    assert response.json() == result

def test_put3():
    response = requests.put("http://api:5000/data/put/Homer/value/Simpson")
    assert response.status_code == 204
    assert response.is_redirect == False

def test_select_all7():
    response = requests.get("http://api:5000/data")
    assert response.status_code == 200
    assert response.is_redirect == False
    result = [['Homer','Simpson'],['Jeffrey','Lebowski'],['Stan','Smith']]
    assert response.json() == result

