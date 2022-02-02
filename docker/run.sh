#!/bin/bash

docker stop python-rest-api
docker rm python-rest-api

docker run -d -p 5000:5000 --name python-rest-api python-rest-api:latest

