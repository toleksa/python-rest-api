#!/bin/bash

if [ $# -ne 1 ]; then
    echo "usage: $0 <install rke2:yes|no>"
    exit 1
fi

if [ "$1" == "yes" ]; then
    echo "installing rke2"
    chmod +x ./install-kube.sh
    ./install-kube.sh
elif [ "$1" == "no" ]; then
    echo "skipping rke2"
else
    echo "unrecognized option"
    exit 1
fi

echo "installing longhorn"
chmod +x ./install-longhorn.sh
./install-longhorn.sh

echo "deploying app"
chmod +x ./deploy.sh
./deploy.sh

