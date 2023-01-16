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

DEBUG=os.environ.get('DEBUG',0)
if DEBUG=="1" or DEBUG=="true" or DEBUG==1:
    DEBUG=1
elif DEBUG=="0" or DEBUG=="false" or DEBUG==0:
    DEBUG=0
else:
    print(f"ERR: unrecognized DEBUG={DEBUG} value")
    exit(1)
if DEBUG==1:
    print("Enabled DEBUG")

app = Flask(__name__)
cors = CORS(app, resources={r"/*": {"origins": "*"}})
requests = Counter('requests', 'Requests metric', ['endpoint', 'method'])
responses = Counter('responses', 'Responses metric', ['endpoint', 'status_code'])

red = redis.Redis(host=os.environ['REDIS_HOST'], port=int(os.environ['REDIS_PORT']), db=0)
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

pool=None
attempts=1

def create_connection_pool():
    """Creates and returns a Connection Pool"""

    # Create Connection Pool
    pool = mariadb.ConnectionPool(
        user=os.environ['DB_USER'],
        password=os.environ['DB_PASS'],
        host=os.environ['DB_HOST'],
        port=int(os.environ['DB_PORT']),
        database="python_rest_api",
        pool_name="dict",
        pool_size=5)

    # Return Connection Pool
    return pool

while True:
    try:
        pool=create_connection_pool()
        conn = pool.get_connection()
        cur = conn.cursor()
        cur.execute("select 1")
        cur.close()
        conn.close()
    except mariadb.Error as e:
        print(f"Error connecting to MariaDB Platform: {e}")
    if pool is not None:
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
        print("===REQUEST=== [ " + str(request.method) + " " + str(request.path) + " ]")
        print(request.headers)
        print("request path: " + str(request.path))
        print("request url_rule: " + str(request.url_rule))
    requests.labels(request.path, request.method).inc()

@app.after_request
def after_request(response):
    responses.labels(request.path, response.status_code).inc()
    if DEBUG==1:
        print("===RESPONSE===")
        print(response.headers)
    return response

def db_connection(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        conn = pool.get_connection()
        cur = conn.cursor()
        try:
            result = func(cur, *args, **kwargs)
            if cur.rowcount > 0:
                conn.commit()
        finally:
            cur.close()
            conn.close()
        return result
    return wrapper

@app.route('/')
def go_to_data():
    return redirect("/data", code=302)

@app.route('/cache', methods=['GET'])
def select_cache():
    result = []
    keys = red.keys()
    for key in keys:
        value = result.append((key.decode("utf-8"), red.get(key.decode("utf-8")).decode("utf-8")))
    return result, 200

@app.route('/reset', methods=['GET'])
@db_connection
def reset(cur):
    query = 'TRUNCATE TABLE dict'
    cur.execute(query)
    query = "INSERT INTO dict (k, v) VALUES ('Homer','Simpson'),('Jeffrey','Lebowski'),('Stan','Smith')"
    cur.execute(query)
    keys = red.keys()
    for key in keys:
        red.delete(key)
    return '', 204

@app.route('/data', methods=['GET'])
@db_connection
def select_all(cur):
    query = "SELECT * from dict"
    cur.execute(query)
    res = []
    for (k, v) in cur:
        res.append((k,v))
    return jsonify(res), 200

@app.route('/data/<key>', methods=['GET'])
@db_connection
def select(cur,key):
    value = red.get(key)
    if value is None:
        query = f'SELECT v FROM dict WHERE k="{key}"' 
        cur.execute(query)
        result = cur.fetchone()
        if result is not None:
            value = result[0]
            red.set(key,value)
    else:
        value = value.decode("utf-8")
    return jsonify((key, value)), 200

@app.route('/data/add', methods=['POST'])
@db_connection
def insert(cur):
  for k in request.get_json():
    v = request.get_json()[k]
    print("request: ", k, " : ", v)
    if k == "":
        return '', 400
    try:
      cur.execute("INSERT INTO dict (k,v) VALUES (?, ?) ON DUPLICATE KEY UPDATE v=?", (k,v,v))
    except mariadb.Error as e:
      print(f"Error: {e}")
  return '', 204

@app.route('/data/put/<key>/value/<value>', methods=['PUT'])
@db_connection
def update(cur,key,value):
    if key is None or value is None:
        return '', 400, {"Access-Control-Allow-Origin": "*"}
    query = f'UPDATE dict set v="{value}" WHERE k="{key}"'
    cur.execute(query)
    if cur.rowcount == 0:
        return '', 404
    red.delete(key)
    return '', 204

@app.route('/data/del/<key>', methods=['DELETE'])
@db_connection
def delete(cur,key):
    if key is None:
        return '', 400
    query = f'DELETE FROM dict WHERE k="{key}"'
    cur.execute(query)
    red.delete(key)
    return '', 204

@app.route('/health')
def health():
  return '', 200

