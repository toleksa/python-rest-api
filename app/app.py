"""Simple rest api with key-value database"""
import os
import sys
import time
import random
from functools import wraps
from werkzeug.middleware.dispatcher import DispatcherMiddleware

import mariadb
import redis

from flask import Flask, jsonify, request, redirect, Response
from flask_cors import CORS

from prometheus_client import make_wsgi_app, Counter

from utils import setting_statsd, StatsdMiddleware

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.instrumentation.flask import FlaskInstrumentor

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

def configure_opentelemetry():
    """Configure OpenTelemetry with Jaeger exporter"""
    trace.set_tracer_provider(
        TracerProvider(
            resource=Resource.create({SERVICE_NAME: "python-rest-api"})
        )
    )
    if "JAEGER_HOST" in os.environ and "JAEGER_PORT" in os.environ:
        if DEBUG == 1:
            print(f"DEBUG: starting JaegerExporter to {os.environ['JAEGER_HOST']}:{os.environ['JAEGER_PORT']}")
        jaeger_exporter = JaegerExporter(
            agent_host_name=os.environ["JAEGER_HOST"],
            agent_port=int(os.environ["JAEGER_PORT"]),
        )
        trace.get_tracer_provider().add_span_processor(
            BatchSpanProcessor(jaeger_exporter)
        )
    else:
        print("INFO: Jaeger ENVs not set, JaegerExporter disabled")

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
    print("ERR: " + str(attempts + 1) + " attempts failed, exiting")
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
    print("ERR: " + str(attempts + 1) + " attempts failed, exiting")
    sys.exit(1)


setting_statsd()
# Add prometheus wsgi middleware to route /metrics requests
dispatcher_middleware = DispatcherMiddleware(app.wsgi_app, {"/metrics": make_wsgi_app()})
statsd_middleware = StatsdMiddleware(dispatcher_middleware, "flask-monitoring")
app.wsgi_app = statsd_middleware

# Configure OpenTelemetry when the app starts
configure_opentelemetry()
FlaskInstrumentor().instrument_app(app)
tracer = trace.get_tracer(__name__)

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

@app.route("/random_status")
def random_status():
    """generates random status response - for generating nice graphs in grafana"""
    status_code = random.choice([200] * 6 + [300, 400, 400, 500])
    return Response("random status", status=status_code)

@app.route("/random_calls")
def random_calls():
    """calls couple subfunctions with random wait times to generate traces for Jaeger"""
    call_one()
    call_three()
    return "", 200

def call_one():
    """Simple function to generate traces for Jaeger"""
    with tracer.start_as_current_span("call_one"):
        time.sleep(0.001 * random.randrange(9))
        call_two()
        call_two()

def call_two():
    """Simple function to generate traces for Jaeger"""
    with tracer.start_as_current_span("call_two"):
        time.sleep(0.001 * random.randrange(3))

def call_three():
    """Simple function to generate traces for Jaeger"""
    with tracer.start_as_current_span("call_three"):
        time.sleep(0.001 * random.randrange(9))
        call_two()
