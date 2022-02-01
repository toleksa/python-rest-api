#!/bin/bash

if [ $# -ne 2 ]; then
  echo "usage: $0 <k> <v>"
  exit 1
fi

curl -X POST -H "Content-Type: application/json" -d "{ \"$1\": \"$2\" }" http://api.kube.ac/data

