# python-rest-api

## app files
rest.py - application

start.sh - start app

post.sh - post data to app

build.sh - build docker image

push.sh - push to docker registry

run.sh - run container locally

## kubernetes

run/deploy using run.sh - script takes one parameter:

yes - will install rke2

no - skip installing rke2 - in case minikube or k3s is already installed

```
cd kube
bash run.sh <yes|no>
```

example execution:

```
bash run.sh yes
installing rke2
[INFO]  finding release for channel stable
[INFO]  using v1.22.5+rke2r1 as release
[INFO]  downloading checksums at https://github.com/rancher/rke2/releases/download/v1.22.5+rke2r1/sha256sum-amd64.txt
[INFO]  downloading tarball at https://github.com/rancher/rke2/releases/download/v1.22.5+rke2r1/rke2.linux-amd64.tar.gz
[INFO]  verifying tarball
[INFO]  unpacking tarball file to /usr/local
Created symlink /etc/systemd/system/multi-user.target.wants/rke2-server.service → /usr/local/lib/systemd/system/rke2-server.service.
installing longhorn
Helm v3.8.0 is already latest
"longhorn" already exists with the same configuration, skipping
Hang tight while we grab the latest from your chart repositories...
...Successfully got an update from the "longhorn" chart repository
Update Complete. ⎈Happy Helming!⎈
namespace/longhorn-system created
W0128 13:48:59.942072    1568 warnings.go:70] policy/v1beta1 PodSecurityPolicy is deprecated in v1.21+, unavailable in v1.25+
W0128 13:49:01.310843    1568 warnings.go:70] policy/v1beta1 PodSecurityPolicy is deprecated in v1.21+, unavailable in v1.25+
NAME: longhorn
LAST DEPLOYED: Fri Jan 28 13:48:58 2022
NAMESPACE: longhorn-system
STATUS: deployed
REVISION: 1
TEST SUITE: None
NOTES:
Longhorn is now installed on the cluster!

Please wait a few minutes for other Longhorn components such as CSI deployments, Engine Images, and Instance Managers to be initialized.

Visit our documentation at https://longhorn.io/docs/
installing metallb
namespace/metallb-system created
Warning: policy/v1beta1 PodSecurityPolicy is deprecated in v1.21+, unavailable in v1.25+
podsecuritypolicy.policy/controller created
podsecuritypolicy.policy/speaker created
serviceaccount/controller created
serviceaccount/speaker created
clusterrole.rbac.authorization.k8s.io/metallb-system:controller created
clusterrole.rbac.authorization.k8s.io/metallb-system:speaker created
role.rbac.authorization.k8s.io/config-watcher created
role.rbac.authorization.k8s.io/pod-lister created
role.rbac.authorization.k8s.io/controller created
clusterrolebinding.rbac.authorization.k8s.io/metallb-system:controller created
clusterrolebinding.rbac.authorization.k8s.io/metallb-system:speaker created
rolebinding.rbac.authorization.k8s.io/config-watcher created
rolebinding.rbac.authorization.k8s.io/pod-lister created
rolebinding.rbac.authorization.k8s.io/controller created
daemonset.apps/speaker created
deployment.apps/controller created
helmchartconfig.helm.cattle.io/rke2-ingress-nginx created
configmap/config created
deploying app
6RpwAg17VAeUsecret/mariadb-secret created
persistentvolumeclaim/mariadb-pvc created
configmap/mariadb-configmap created
statefulset.apps/mariadb-statefulset created
service/mariadb-service created
deployment.apps/python-rest-api-deployment created
service/python-rest-api-service created
ingress.networking.k8s.io/python-rest-api-ingress created
root@ubuntu:~/python-rest-api/kube#

```