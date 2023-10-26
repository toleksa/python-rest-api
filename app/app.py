"""Simple rest api with key-value database"""
import sys
import os
import time
from functools import wraps
from werkzeug.middleware.dispatcher import DispatcherMiddleware

import mariadb
import redis
from flask import Flask, jsonify, request, redirect
from prometheus_client import make_wsgi_app, Counter
from flask_cors import CORS

DEBUG = os.environ.get("DEBUG", 0)
if DEBUG in ["1", True, "true", 1]:
    DEBUG = 1
elif DEBUG in ["0", False, "false", 0]:
    DEBUG = 0
else:
    print(f"ERR: unrecognized DEBUG={DEBUG} value")
    sys.exit(1)
if DEBUG == 1:
    print("Enabled DEBUG")

app = Flask(__name__)
cors = CORS(app, resources={r"/*": {"origins": "*"}})
requests = Counter(
    "python_rest_api_requests", "Requests metric", ["endpoint", "method"]
)
responses = Counter(
    "python_rest_api_responses", "Responses metric", ["endpoint", "status_code"]
)

myRedis = redis.Redis(
    host=os.environ["REDIS_HOST"], port=int(os.environ["REDIS_PORT"]), db=0
)


for attempts in range(5):   #6 attempts, 30 seconds
    try:
        myRedis.info()
        break
    except redis.exceptions.ConnectionError as e:
        print(f"Error connecting to  Redis: {e}")
    time.sleep(5)
else:
    print("ERR: " + str(attempts - 1) + " attempts failed, exiting")
    sys.exit(1)


pool = None

def create_connection_pool():
    """Creates and returns a Connection Pool"""
    # Return Connection Pool
    return mariadb.ConnectionPool(
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASS"],
        host=os.environ["DB_HOST"],
        port=int(os.environ["DB_PORT"]),
        database=os.environ["DB_DATABASE"],
        pool_name="dict",
        pool_size=5,
    )


for attempts in range(5):   #6 attempts, 30 seconds
    try:
        pool = create_connection_pool()
        test_conn = pool.get_connection()
        test_cur = test_conn.cursor()
        test_cur.execute("select 1")
        test_cur.close()
        test_conn.close()
    except mariadb.Error as e:
        print(f"Error connecting to MariaDB Platform: {e}")
    if pool is not None:
        break
    time.sleep(5)
else:
    print("ERR: " + str(attempts - 1) + " attempts failed, exiting")
    sys.exit(1)


# Add prometheus wsgi middleware to route /metrics requests
app.wsgi_app = DispatcherMiddleware(app.wsgi_app, {"/metrics": make_wsgi_app()})


@app.before_request
def before_request():
    """metrics for prometheus - requests"""
    if DEBUG == 1:
        print("===REQUEST=== [ " + str(request.method) + " " + str(request.path) + " ]")
        print(request.headers)
        print("request path: " + str(request.path))
        print("request url_rule: " + str(request.url_rule))
    requests.labels(request.path, request.method).inc()


@app.after_request
def after_request(response):
    """metrics for prometheus - responses"""
    responses.labels(request.path, response.status_code).inc()
    if DEBUG == 1:
        print("===RESPONSE===")
        print(response.headers)
    return response


def db_connection(func):
    """execute query on db"""

    @wraps(func)
    def wrapper(*args, **kwargs):
        conn = pool.get_connection()
        conn.auto_reconnect = True
        cursor = conn.cursor()
        try:
            result = func(cursor, *args, **kwargs)
        finally:
            if cursor.rowcount > 0:
                conn.commit()
            cursor.close()
            conn.close()
        return result

    return wrapper


@app.route("/")
def go_to_data():
    """/ -> redirect to /data"""
    return redirect("/data", code=302)


@app.route("/cache", methods=["GET"])
def select_cache():
    """get what is in cache"""
    result = []
    keys = myRedis.keys()
    for key in keys:
        result.append(
            (key.decode("utf-8"), myRedis.get(key.decode("utf-8")).decode("utf-8"))
        )
    return result, 200


@app.route("/reset", methods=["GET"])
@db_connection
def reset(cursor):
    """reset DB state to initial"""
    query = "TRUNCATE TABLE dict"
    cursor.execute(query)
    try:
        with open("init.sql", "r", encoding="utf-8") as init_file:
            for line in init_file:
                if not line.startswith(("create", "CREATE")):
                    cursor.execute(line)
    except FileNotFoundError as e:
        print(f"ERR /reset: init.sql not found: {e}")
        sys.exit(2)
    keys = myRedis.keys()
    for key in keys:
        myRedis.delete(key)
    requests._metrics.clear()
    responses._metrics.clear()
    return "", 204


@app.route("/data", methods=["GET"])
@db_connection
def select_all(cursor):
    """get all entries"""
    query = "SELECT * from dict"
    cursor.execute(query)
    res = []
    for key, value in cursor:
        res.append((key, value))
    return jsonify(res), 200


@app.route("/data/<key>", methods=["GET"])
@db_connection
def select(cursor, key):
    """get one value"""
    value = myRedis.get(key)
    if value is None:
        query = f'SELECT v FROM dict WHERE k="{key}"'
        cursor.execute(query)
        result = cursor.fetchone()
        if result is not None:
            value = result[0]
            myRedis.set(key, value)
    else:
        value = value.decode("utf-8")
    return jsonify((key, value)), 200


@app.route("/data/add", methods=["POST"])
@db_connection
def insert(cursor):
    """add entry to DB"""
    for key in request.get_json():
        value = request.get_json()[key]
        print("request: ", key, " : ", value)
        if key == "":
            return "", 400
        try:
            cursor.execute(
                "INSERT INTO dict (k,v) VALUES (?, ?) ON DUPLICATE KEY UPDATE v=?",
                (key, value, value),
            )
        except mariadb.Error as e:
            print(f"Error: {e}")
    return "", 204


@app.route("/data/put/<key>/value/<value>", methods=["PUT"])
@db_connection
def update(cursor, key, value):
    """update value"""
    if key is None or value is None:
        return "", 400, {"Access-Control-Allow-Origin": "*"}
    query = f'UPDATE dict set v="{value}" WHERE k="{key}"'
    cursor.execute(query)
    if cursor.rowcount == 0:
        return "", 404
    myRedis.delete(key)
    return "", 204


@app.route("/data/del/<key>", methods=["DELETE"])
@db_connection
def delete(cursor, key):
    """delete entry"""
    if key is None:
        return "", 400
    query = f'DELETE FROM dict WHERE k="{key}"'
    cursor.execute(query)
    myRedis.delete(key)
    return "", 204


@app.route("/health")
def health():
    """health endpoint"""
    return "", 200


@app.route("/id")
@db_connection
def get_ids(cursor):
    """get hostnames of backend machines"""
    api_host = os.uname()[1]
    query = "select @@hostname;"
    cursor.execute(query)
    db_host = cursor.fetchone()
    result = {"api_host": api_host, "db_host": db_host[0]}
    return jsonify(result), 200
