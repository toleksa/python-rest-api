# python-rest-api

## app

### description

app is implementing key-value dictionary via REST api

### methods

`GET api.kube.ac/data` - will return all records

`GET api.kube.ac/data/<key>` - will return record for that key
    
`POST -H "Content-Type: application/json" -d "{ \"<key>\": \"<value>\" }"` - adds new record or updates value if record with this key already exists

#TODO: document remaining methods

## files

### app
app/

`app.py` - actuall app
    
`start.sh` - run script
    
`post.sh` - example post to push new data
       
### docker tools
docker/

`run.sh` - launch container (doesn't work on Fedora 36+ - use podman-compose)
    
`build.sh` - helper to build image
    
`push.sh` - helper to push image
    
### docker compose

`docker-compose.yaml` - standard config to run app    

`docker-compose.test.yaml` - additionally starts also container with integration-tests

### kubernetes

there are deployments in three versions:

`kube/` - pure kubectl

`helm/` - helm install

`argo/` - use argocd app of apps

  
## dependencies

Python - `pip install -r app/requirements.txt`

Fedora - `dnf install mariadb-connector-c-devel python3-devel`
  
## run

### standalone

```
cd app
./start.sh
```

### podman-compose

```podman-compose up``` to start app

```podman-compose -f docker-compose.yaml -f docker-compose.test.yaml up``` to start app and test container

### kubernetes

there are deployments in three versions:

`kube/` - pure kubectl

`helm/` - helm install

`argo/` - use argocd app of apps



in each case install process is the same - go into directory and execute:


`install.sh` - script takes one parameter:

`yes` - will install rke2
    
`no` - skip installing rke2 - in case kubernetes is already installed

app will be available at **api.kube.ac**

### ChatGPT description:

This is a Python code for a Flask web service. It has some middleware for handling CORS, Redis, and Prometheus metrics. On the app initialization, it is trying to connect to Redis and MariaDB, and it retries if the connection fails.
It also creates an endpoint '/metrics' that returns Prometheus metrics. The root '/' redirects to '/data'. There are several routes defined, such as '/cache' that returns all the key-value pairs stored in Redis, '/reset' that truncates a table in MariaDB and inserts default values into it and '/data' that allows to perform some CRUD operations with the data in MariaDB. It also has a middleware function 'before_request' that increments a Prometheus counter for requests and 'after_request' that increments a Prometheus counter for responses and sets headers for CORS.
