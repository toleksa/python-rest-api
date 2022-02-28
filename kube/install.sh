#!/bin/bash

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

echo "installing longhorn"
kubectl create namespace longhorn-system
kubectl apply -f https://raw.githubusercontent.com/longhorn/longhorn/master/deploy/longhorn.yaml

echo "installing metallb"
kubectl apply -f https://raw.githubusercontent.com/metallb/metallb/main/manifests/namespace.yaml
kubectl apply -f https://raw.githubusercontent.com/metallb/metallb/main/manifests/metallb.yaml
kubectl apply -f - <<EOF
apiVersion: v1
kind: ConfigMap
metadata:
  namespace: metallb-system
  name: config
data:
  config: |
    address-pools:
    - name: default
      protocol: layer2
      addresses:
      - `hostname -I | awk '{print $1"-"$1}'`
EOF

echo "deploying app"
kubectl create ns python-rest-api
kubectl -n python-rest-api create secret generic mariadb --from-literal=mariadb-password=$(head /dev/urandom | tr -dc A-Za-z0-9 | head -c 12 | base64) --from-literal=mariadb-root-password=$(head /dev/urandom | tr -dc A-Za-z0-9 | head -c 12 | base64)
kubectl -n python-rest-api create configmap mariadb-init --from-literal=init.sql="create table python_rest_api.dict(k varchar(50) primary key,v varchar (50)); insert into python_rest_api.dict (k,v) values ('Homer','Simpson'); insert into python_rest_api.dict (k,v) values ('Jeffrey','Lebowski'); insert into python_rest_api.dict (k,v) values ('Stan','Smith');"
kubectl -n python-rest-api apply -f mariadb.yaml
kubectl -n python-rest-api apply -f python-rest-api.yaml

