#!/bin/bash

if [ $# -ne 1 ]; then
    echo "usage: $0 <install rke2:yes|no>"
    exit 1
fi

if [ "$1" == "yes" ]; then
    echo "installing rke2"
    ./install-kube.sh
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
kubectl apply -f https://raw.githubusercontent.com/metallb/metallb/v0.10.2/manifests/namespace.yaml
kubectl apply -f https://raw.githubusercontent.com/metallb/metallb/v0.10.2/manifests/metallb.yaml
kubectl apply -f config-ingress.yaml
METALLB_ADDRESSES=${METALLB_ADDRESSES:=`hostname -I | awk '{print $1"-"$1}'`} envsubst < metallb-configmap.yaml | kubectl apply -f -

echo "deploying app"
./deploy.sh

