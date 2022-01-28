#!/bin/bash

kubectl create secret generic mariadb-secret --from-literal=password=$(head /dev/urandom | tr -dc A-Za-z0-9 | head -c 12 | base64)
kubectl apply -f mariadb.yaml
kubectl apply -f python-rest-api.yaml
