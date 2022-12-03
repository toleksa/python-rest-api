from flask import Flask, jsonify, request, redirect
import mariadb
import redis
import sys
import os
import time

app = Flask(__name__)

red = redis.Redis(host=os.environ['REDIS_HOST'], port=6379, db=0)

attempts=1
conn=None

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


@app.route('/')
def go_to_data():
    return redirect("/data", code=302)

@app.route('/cache', methods=['GET'])
def select_cache():
    res = []
    keys = red.keys()
    for key in keys:
        value = res.append((key.decode("utf-8"), red.get(key.decode("utf-8")).decode("utf-8")))
    return res

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
    return res

@app.route('/data', methods=['GET'])
def select():
    res = []

    key = request.args.get("key")
    if key is None:
        res=select_all()
    else:
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
        res.append((key, value))
    return jsonify(res)

@app.route('/data', methods=['POST'])
def insert():
  for k in request.get_json():
    v = request.get_json()[k]
    print("request: ", k, " : ", v)
    cur = conn.cursor()
    try:
      cur.execute("INSERT INTO dict (k,v) VALUES (?, ?) ON DUPLICATE KEY UPDATE v=?", (k,v,v))
    except mariadb.Error as e:
      print(f"Error: {e}")
    conn.commit()
    #TODO: add to redis
  return '', 204

@app.route('/health')
def health():
  return '', 200
