#!/bin/bash

if [ $# -ne 1 ]; then
    echo "usage: $0 <install rke2:yes|no>"
    exit 1
fi

if [ "$1" == "yes" ]; then
  echo "installing rke2"
  curl -sfL https://get.rke2.io | sh -
  systemctl enable rke2-server.service
  systemctl start rke2-server.service
  echo "export PATH=\$PATH:/var/lib/rancher/rke2/bin" >> ~/.bashrc
  echo "export KUBECONFIG=/etc/rancher/rke2/rke2.yaml" >> ~/.bashrc
  . ~/.bashrc
elif [ "$1" == "no" ]; then
  echo "skipping rke2"
else
  echo "unrecognized option"
  exit 1
fi

echo "installing helm"
curl -fsSL https://raw.githubusercontent.com/helm/helm/master/scripts/get-helm-3 | bash
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo add longhorn https://charts.longhorn.io
helm repo update

echo "installing longhorn"
helm install --create-namespace longhorn longhorn/longhorn --namespace longhorn-system

echo "installing metallb"
kubectl apply -f https://raw.githubusercontent.com/metallb/metallb/v0.10.2/manifests/namespace.yaml
kubectl apply -f https://raw.githubusercontent.com/metallb/metallb/v0.10.2/manifests/metallb.yaml
kubectl apply -f config-ingress.yaml
METALLB_ADDRESSES=${METALLB_ADDRESSES:=`hostname -I | awk '{print $1"-"$1}'`} envsubst < metallb-configmap.yaml | kubectl apply -f -

helm install mariadb bitnami/mariadb -f values.yaml
kubectl apply -f python-rest-api.yaml
