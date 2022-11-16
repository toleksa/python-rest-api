#!/bin/bash

docker stop python-rest-api python-rest-api-db
docker rm python-rest-api python-rest-api-db

docker network create python-rest-api
docker run -d \
  --name python-rest-api-db \
  --network python-rest-api \
  --hostname db \
  -e MARIADB_PASSWORD=password \
  -e MARIADB_USER=user \
  -e MARIADB_DATABASE=python_rest_api \
  -e MARIADB_ROOT_PASSWORD=password \
  --mount type=bind,source=${PWD}/../app/init.sql,target=/docker-entrypoint-initdb.d/init.sql \
  mariadb:10.10.2

docker run -d \
  -p 5000:5000 \
  --name python-rest-api \
  --network python-rest-api \
  --hostname webserver \
  -e DB_PASS=password \
  -e DB_USER=user \
  -e DB_HOST=db \
  toleksa/python-rest-api:latest

