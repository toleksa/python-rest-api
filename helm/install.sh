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

echo "installing helm"
curl https://raw.githubusercontent.com/toleksa/kube-system/main/install-helm.sh | bash

echo "installing longhorn"
helm install --create-namespace --namespace longhorn-system longhorn longhorn/longhorn

echo "installing metallb"
helm install --create-namespace --namespace metallb-system  metallb bitnami/metallb -f - <<EOF
configInline:
  address-pools:
  - name: default
    protocol: layer2
    addresses:
    - `hostname -I | awk '{print $1"-"$1}'`
EOF

helm install mariadb bitnami/mariadb -f mariadb-values.yaml
sed -e "s/example.com/`hostname -f`/" python-rest-api-values.yaml | helm install python-rest-api ./python-rest-api -f -

