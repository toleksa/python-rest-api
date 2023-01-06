from flask import Flask, jsonify, request, redirect
from prometheus_client import make_wsgi_app, Counter
from flask_cors import CORS
from functools import wraps
from werkzeug.middleware.dispatcher import DispatcherMiddleware
import mariadb
import redis
import sys
import os
import time

DEBUG=0

app = Flask(__name__)
cors = CORS(app, resources={r"/*": {"origins": "*"}})
#cors = CORS(app, resources={r"/*": {"origins": "*", "methods": "GET, POST, PUT, OPTIONS, DELETE"}})
requests = Counter('requests', 'Requests metric', ['endpoint', 'method'])
responses = Counter('responses', 'Responses metric', ['endpoint', 'status_code'])

red = redis.Redis(host=os.environ['REDIS_HOST'], port=6379, db=0)
attempts=1

while True:
    try:
        red.info()
        break
    except redis.exceptions.ConnectionError as e:
        print(f"Error connecting to  Redis: {e}")
    attempts+=1
    if attempts > 5:
        print("ERR: " + str(attempts - 1) + " attempts failed, exiting")
        sys.exit(1)
    time.sleep(3)

conn=None
attempts=1

while True:
    try:
        conn = mariadb.connect(
            user=os.environ['DB_USER'],
            password=os.environ['DB_PASS'],
            host=os.environ['DB_HOST'],
            port=3306,
            database="python_rest_api"
        )
    except mariadb.Error as e:
        print(f"Error connecting to MariaDB Platform: {e}")
    if conn is not None:
        break
    attempts+=1
    if attempts > 5:
        print("ERR: " + str(attempts - 1) + " attempts failed, exiting")
        sys.exit(1)
    time.sleep(3)

# Add prometheus wsgi middleware to route /metrics requests
app.wsgi_app = DispatcherMiddleware(app.wsgi_app, {
    '/metrics': make_wsgi_app()
})

@app.before_request
def before_request():
    if DEBUG==1:
        print(request.headers)
        print(request.path)
        print(request.url_rule)
    requests.labels(request.path, request.method).inc()

@app.after_request
def after_request(response):
    responses.labels(request.path, response.status_code).inc()
    #TODO: should be handled by CORS above, but doesn't work for OPTIONS request with origin headers
    #response.headers.add('Access-Control-Allow-Origin', '*')
    #response.headers.add('Access-Control-Allow-Headers', 'content-type')
    #response.headers.add('Access-Control-Allow-Methods', 'GET, POST, PUT, OPTIONS, DELETE')
    if DEBUG==1:
        print(response.headers)
    return response

@app.route('/')
def go_to_data():
    return redirect("/data", code=302)

@app.route('/cache', methods=['GET'])
def select_cache():
    res = []
    keys = red.keys()
    for key in keys:
        value = res.append((key.decode("utf-8"), red.get(key.decode("utf-8")).decode("utf-8")))
    return res, 200

@app.route('/reset', methods=['GET'])
def reset():
    query = 'TRUNCATE TABLE dict'
    cur = conn.cursor()
    cur.execute(query)
    query = "INSERT INTO dict (k, v) VALUES ('Homer','Simpson'),('Jeffrey','Lebowski'),('Stan','Smith')"
    cur.execute(query)
    conn.commit()
    keys = red.keys()
    for key in keys:
        red.delete(key)
    return '', 204

@app.route('/data', methods=['GET'])
def select_all():
    cur = conn.cursor()
    query = "SELECT * from dict"
    k =request.args.get('k')
    if k is not None:
        query += " WHERE k='" + str(request.args.get('k')) +"'"
    cur.execute(query)
    res = []
    for (k, v) in cur:
        res.append((k,v))
    return jsonify(res), 200

@app.route('/data/<key>', methods=['GET'])
def select(key):
    value = red.get(key)
    if value is None:
        query = f'SELECT v FROM dict WHERE k="{key}"' 
        cur = conn.cursor()
        cur.execute(query)
        result = cur.fetchone()
        if result is not None:
            value = result[0]
            red.set(key,value)
    else:
        value = value.decode("utf-8")
    return jsonify((key, value)), 200

@app.route('/data/add', methods=['POST'])
def insert():
  for k in request.get_json():
    v = request.get_json()[k]
    print("request: ", k, " : ", v)
    if k == "":
        return '', 400
    cur = conn.cursor()
    try:
      cur.execute("INSERT INTO dict (k,v) VALUES (?, ?) ON DUPLICATE KEY UPDATE v=?", (k,v,v))
    except mariadb.Error as e:
      print(f"Error: {e}")
    conn.commit()
  return '', 204

@app.route('/data/put/<key>/value/<value>', methods=['PUT'])
def update(key,value):
    if key is None or value is None:
        return '', 400, {"Access-Control-Allow-Origin": "*"}
    query = f'UPDATE dict set v="{value}" WHERE k="{key}"'
    cur = conn.cursor()
    cur.execute(query)
    if cur.rowcount == 0:
        return '', 404
    conn.commit()
    red.delete(key)
    return '', 204

@app.route('/data/del/<key>', methods=['DELETE'])
def delete(key):
    if key is None:
        return '', 400
    query = f'DELETE FROM dict WHERE k="{key}"'
    cur = conn.cursor()
    cur.execute(query)
    red.delete(key)
    return '', 204

@app.route('/health')
def health():
  return '', 200

