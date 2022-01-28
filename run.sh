#!/bin/bash

docker stop python-rest-api
docker rm python-rest-api

docker run -d -p 5001:5000 --name python-rest-api localhost/python-rest-api:latest

