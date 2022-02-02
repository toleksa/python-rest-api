#!/bin/bash

if [ $# -ne 1 ]; then
    echo "usage: $0 <install rke2:yes|no>"
    exit 1
fi

if [ "$1" == "yes" ]; then
    echo "installing rke2"
    ../kube/install-kube.sh
    . ~/.bashrc
elif [ "$1" == "no" ]; then
    echo "skipping rke2"
else
    echo "unrecognized option"
    exit 1
fi

echo "installing longhorn"
./install-longhorn.sh

echo "installing metallb"
kubectl apply -f https://raw.githubusercontent.com/metallb/metallb/main/manifests/namespace.yaml
kubectl apply -f https://raw.githubusercontent.com/metallb/metallb/main/manifests/metallb.yaml
METALLB_ADDRESSES=${METALLB_ADDRESSES:=`hostname -I | awk '{print $1"-"$1}'`} envsubst < metallb-configmap.yaml | kubectl apply -f -

echo "deploying app"
kubectl create secret generic mariadb --from-literal=mariadb-password=$(head /dev/urandom | tr -dc A-Za-z0-9 | head -c 12 | base64) --from-literal=mariadb-root-password=$(head /dev/urandom | tr -dc A-Za-z0-9 | head -c 12 | base64)
kubectl apply -f mariadb.yaml
kubectl apply -f python-rest-api.yaml

