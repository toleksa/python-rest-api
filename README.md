# python-rest-api       

## app

### description

Simple Python/Flask app that is implementing key-value dictionary available via REST api

### methods

`GET /data` - will return all records

`GET /data/<key>` - will return record for that \<key\>
    
`POST -H "Content-Type: application/json" -d "{ \"<key>\": \"<value>\" }" /data/add` - adds new record or updates value if record with this \<key\> already exists

`PUT /data/put/<key>/value/<value>` - updates \<key\> with \<value\>

`DELETE /data/del/<key>` - deletes \<key\> entry

</br>

`GET /health` - endpoint for health state

`GET /metrics` - metrics for Prometheus

</br>

`GET /id` - returns hostnames of API and DB machines (for debugging)

`GET /cache` - shows entries stored in Redis cache

`GET /reset` - restores initial DB state, cleares cache and resets metrics

## files

### application files

`app/app.py` - actuall app

`app/init.sql` - initial SQL file for DB
    
`app/post.sh` - example post to push new data

`app/requirements.txt` - requirements file for python/pip

`app/start.sh` - run script
       
### docker files

`Dockerfile` - dockerfile to build app

`docker-compose.yaml` - standard config to run app    

`docker-compose.test.yaml` - additionally starts also container with integration-tests

### kubernetes

there are deployments in three versions:

`kube/` - pure kubectl

`helm/` - helm install

`argo/` - use argocd app of apps

### jenkins

`jenkins/Jenkinsfile` - pipeline definition

`jenkins/config.xml` - jenkins project dump
  
## run

### standalone

dependencies:

Fedora - `dnf install mariadb-connector-c-devel python3-devel`

Ubuntu - `apt install libmariadb-dev`

Python - `pip install -r app/requirements.txt`

run:

```
cd app
./start.sh
```
Parameters can be configured via ENV variables:

```
REDIS_HOST=127.0.0.1 REDIS_PORT=6379 DB_HOST=127.0.0.1 DB_PORT=3306 DB_DATABASE=python_rest_api API_PORT=5000 DB_USER=user DB_PASS=password ./start.sh
```

### docker-compose

`docker-compose up` to start app

`docker-compose -f docker-compose.yaml -f docker-compose.test.yaml up` to start app and test container

### kubernetes

there are deployments in three versions:

`kube/` - pure kubectl

`helm/` - helm install

`argo/` - use argocd app of apps



in each case install process is the same - go into directory and execute:


`install.sh <yes|no>` - script takes one parameter:

`yes` - will install rke2
    
`no` - skip installing rke2 - in case kubernetes is already installed

app will be available at **python-rest-api.\`hostname -d\`**

### ChatGPT description:

This is a Python code for a Flask web service. It has some middleware for handling CORS, Redis, and Prometheus metrics. On the app initialization, it is trying to connect to Redis and MariaDB, and it retries if the connection fails.
It also creates an endpoint '/metrics' that returns Prometheus metrics. The root '/' redirects to '/data'. There are several routes defined, such as '/cache' that returns all the key-value pairs stored in Redis, '/reset' that truncates a table in MariaDB and inserts default values into it and '/data' that allows to perform some CRUD operations with the data in MariaDB. It also has a middleware function 'before_request' that increments a Prometheus counter for requests and 'after_request' that increments a Prometheus counter for responses and sets headers for CORS.
 
