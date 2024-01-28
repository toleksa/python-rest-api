#!/bin/bash

APPS="
bitnami/mariadb python-rest-api-mariadb
bitnami/redis python-rest-api-redis
prometheus-community/prometheus-statsd-exporter python-rest-api-statsd
"

helm repo update &> /dev/null
cd templates
while read -r REPO MANIFEST; do
  if [ -z "$REPO" ] && [ -z "$MANIFEST" ]; then
    echo ""
    continue
  fi

  COLOR='\033[00m'
  SUFFIX=''

  REPO_VER=$(helm search repo "$REPO" | grep -E "^$REPO " | gawk '{ print $2 }')
  GIT_VER=$(grep targetRevision "${MANIFEST}.yaml" | grep -v \# | gawk '{ print $2 }')

  if [ "$REPO_VER" != "$GIT_VER" ]; then
    COLOR='\033[01;31m'
    SUFFIX="!!"
  fi
  echo -e "$REPO ${COLOR}${REPO_VER}\033[00m $GIT_VER $SUFFIX"
done <<< "$APPS"
