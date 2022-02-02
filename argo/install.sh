#!/bin/bash

if [ $# -ne 1 ]; then
    echo "usage: $0 <install rke2:yes|no>"
    exit 1
fi

if [ "$1" == "yes" ]; then
  echo "installing rke2"
  ../kube/install-rke2.sh
  . ~/.bashrc
elif [ "$1" == "no" ]; then
  echo "skipping rke2"
else
  echo "unrecognized option"
  exit 1
fi

echo "installing helm"
curl -fsSL https://raw.githubusercontent.com/helm/helm/master/scripts/get-helm-3 | bash
helm repo add argo-cd https://argoproj.github.io/argo-helm
helm repo update

echo "Waiting for kubernetes to start"
until kubectl get nodes | grep `hostname` | grep " Ready " ; do
  sleep 5s
  echo -n .
done
echo ""
kubectl get nodes
echo ""

helm install --create-namespace --namespace argocd argocd argo-cd/argo-cd

# setting credentials to admin/password <- for simplicity of example, I know it's uglyyy
# bcrypt(password)=$2a$10$rRyBsGSHK6.uc8fntPwVIuLVHgsAhAX7TcdrqW/RADU0uh7CaChLa
kubectl -n argocd patch secret argocd-secret \
  -p '{"stringData": {
    "admin.password": "$2a$10$rRyBsGSHK6.uc8fntPwVIuLVHgsAhAX7TcdrqW/RADU0uh7CaChLa",
    "admin.passwordMtime": "'$(date +%FT%T%Z)'"
  }}'

# install kube-argo app
. ./env ; METALLB_ADDRESSES=${METALLB_ADDRESSES:=`hostname -I | awk '{print $1"-"$1}'`} envsubst < kube-argo.yaml | kubectl apply -f -

# remove argocd entry from helm, now it's selfmanaged
kubectl delete secret -l owner=helm,name=argocd -n argocd

exit 0

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
helm install python-rest-api ./python-rest-api -f python-rest-api-values.yaml

