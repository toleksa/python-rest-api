#!/bin/bash

head /dev/urandom | tr -dc A-Za-z0-9 | head -c 12 ; echo '' | base64 | kubectl create secret generic mariadb-secret --from-literal=mariadb-root-password=-
