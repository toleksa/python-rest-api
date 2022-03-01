# python-rest-api

## app files
docker/app/

    rest.py - actuall app
    
    start.sh - run script
    
    post.sh - example post to push new data
    
    
    
## docker files
docker/

    Dockerfile - :)
    
    run.sh - launch container
    
    build.sh - helper to build image
    
    push.sh - helper to push image
    
    

## kubernetes

there are deployments in three versions:

    kube/ - pure kubectl

    helm/ - helm install

    argo/ - use argocd app of apps



in each case install process is the same - go into directory and execute:


    install.sh - script takes one parameter:

    yes - will install rke2
    
    no - skip installing rke2 - in case kubernetes is already installed

app will be available at **api.kube.ac**



## app

app is implementing key-value dictionary with methods:

    GET api.kube.ac/data - will return all records

    GET api.kube.ac/data?k=<key> - will return record for that key
    
    POST -H "Content-Type: application/json" -d "{ \"<key>\": \"<value>\" }" - adds new record or updates value if record with this key already exists
  
  
  
## bugs

- helm: ```k logs pod/metallb-controller-6db85978c-xql6r
{"branch":"v0.11.0","caller":"level.go:63","commit":"846c55a","goversion":"gc / go1.17.6 / amd64","level":"info","msg":"MetalLB controller starting version 0.11.0 (commit 846c55a, branch v0.11.0)","ts":"2022-03-01T09:26:14.712907063Z","version":"0.11.0"}
{"caller":"level.go:63","configmap":"metallb-system/metallb-config","error":"parsing address pool #1: invalid CIDR \"192.168.0.173-192.168.0.173\" in pool \"default\": invalid IP range \"192.168.0.173-192.168.0.173\": start IP \"192.168.0.173\" is after the end IP \"192.168.0.173\"","event":"configStale","level":"error","msg":"config (re)load failed, config marked stale","ts":"2022-03-01T09:26:14.816651011Z"}
{"caller":"level.go:63","event":"stateSynced","level":"info","msg":"controller synced, can allocate IPs now","ts":"2022-03-01T09:26:14.816772555Z"}```  
  
