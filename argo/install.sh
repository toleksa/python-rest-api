#!/bin/bash

set -e

if [ $# -ne 1 ]; then
    echo "usage: $0 <install rke2:yes|no>"
    exit 1
fi

if [ "$1" == "yes" ]; then
  echo "installing rke2"
  curl https://raw.githubusercontent.com/toleksa/kube-system/main/install-rke2.sh | bash
  curl https://raw.githubusercontent.com/toleksa/kube-system/main/install-bash.sh | bash
  . ~/.bashrc
elif [ "$1" == "no" ]; then
  echo "skipping rke2"
else
  echo "unrecognized option"
  exit 1
fi

#check if kubectl installed
kubectl &> /dev/null
if [ $? -ne 0 ]; then
  echo "ERR: check kubectl installation"
  exit 1
fi 

echo "installing helm"
curl https://raw.githubusercontent.com/toleksa/kube-system/main/install-helm.sh | bash

echo "installing argocd"
curl https://raw.githubusercontent.com/toleksa/kube-system/main/install-argo.sh | bash

echo "installing python-rest-api"
sed -e "s/example.com/`hostname -f`/" python-rest-api-main.yaml | kubectl apply -f -

