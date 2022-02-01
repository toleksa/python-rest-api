#!/bin/bash

#docker login docker.io / toleksa

docker tag python-rest-api:latest toleksa/python-rest-api:latest
docker push toleksa/python-rest-api:latest

