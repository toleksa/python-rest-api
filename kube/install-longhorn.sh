#!/bin/bash

#install helm
curl -fsSL https://raw.githubusercontent.com/helm/helm/master/scripts/get-helm-3 | bash
helm repo add longhorn https://charts.longhorn.io
helm repo update

#install longhorn - storage provider
kubectl create namespace longhorn-system
helm install longhorn longhorn/longhorn --namespace longhorn-system -f longhorn-values.yaml

