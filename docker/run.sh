#!/bin/bash

for IMG in python-rest-api python-rest-api-db python-rest-api-redis
do
  docker stop $IMG
  docker rm $IMG
done

docker network create python-rest-api
docker run -d \
  --name python-rest-api-db \
  --network python-rest-api \
  --hostname db \
  -e MARIADB_PASSWORD=password \
  -e MARIADB_USER=user \
  -e MARIADB_DATABASE=python_rest_api \
  -e MARIADB_ROOT_PASSWORD=password \
  -v ${PWD}/../app/init.sql:/docker-entrypoint-initdb.d/init.sql:Z \
  mariadb:10.10.2

docker run -d \
  -p 6379:6379 \
  --name python-rest-api-redis \
  --network python-rest-api \
  --hostname redis \
  redis:7.0.5-alpine

docker run -d \
  -p 5000:5000 \
  --name python-rest-api \
  --network python-rest-api \
  --hostname webserver \
  -e DB_PASS=password \
  -e DB_USER=user \
  -e DB_HOST=db \
  toleksa/python-rest-api:latest

