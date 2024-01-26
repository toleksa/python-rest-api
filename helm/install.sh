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

echo "installing longhorn"
helm install --create-namespace --namespace longhorn-system longhorn longhorn/longhorn

echo "installing metallb"
helm install --create-namespace --namespace metallb-system metallb bitnami/metallb
#kubectl wait --for=condition=Ready -n metallb-system pod `kubectl -n metallb-system get pods | grep metallb-controller | gawk '{ print $1 }'`
kubectl -n metallb-system rollout status deployment metallb-controller
kubectl -n metallb-system apply -f - <<EOF
apiVersion: metallb.io/v1beta1
kind: IPAddressPool
metadata:
  name: metallb-pool-default
  namespace: metallb-system
spec:
  addresses:
  - `hostname -I | awk '{print $1"/32"}'`
EOF

echo "installing kube-prometheus-stack"
sed -e "s/example.com/`hostname -d`/" monitoring-values.yaml | helm install --create-namespace --namespace monitoring kube-prometheus-stack prometheus-community/kube-prometheus-stack -f -

echo "installing python-rest-api"
helm install --create-namespace --namespace python-rest-api python-rest-api-mariadb bitnami/mariadb -f mariadb-values.yaml
helm install --namespace python-rest-api python-rest-api-redis bitnami/redis -f redis-values.yaml --version 18.7.0
helm install --namespace python-rest-api python-rest-api-statsd prometheus-community/prometheus-statsd-exporter
sed -e "s/example.com/`hostname -d`/" python-rest-api-values.yaml | helm install --create-namespace --namespace python-rest-api python-rest-api ./python-rest-api -f -

