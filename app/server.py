from flask import Flask, jsonify, request, redirect
import mariadb
import redis
import sys
import os
import time

app = Flask(__name__)

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

red = redis.Redis(host='localhost', port=63799, db=0)

@app.route('/')
def go_to_data():
    return redirect("/data", code=302)

@app.route('/data', methods=['GET'])
def select():
  cur = conn.cursor()
  query = "SELECT * from dict"
  k =request.args.get('k')
  if k is not None:
    query += " WHERE k='" + str(request.args.get('k')) +"'"
  cur.execute(query)
  res = []
  for (k, v) in cur:
    res.append((k,v))
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
  return '', 204

@app.route('/health')
def health():
  return '', 200

