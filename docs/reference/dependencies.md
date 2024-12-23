# Dependencies

The Ptah CLI leverages many other tools. When possible, if they are not already installed it will
do so on the fly. However, if you wish to control the installation of those tools, here is a
complete list of what Ptah might expect to be installed.

[Docker](https://docs.docker.com/engine/install/) &mdash; if your project has any local Docker image
definitions.

``` bash
docker --version
```

[Helm](https://helm.sh/docs/intro/install/),
[Helmfile](https://helmfile.readthedocs.io/en/latest/#installation)
&mdash; if your project has a `helmfile.yaml` in its root.

``` bash
helm version
helmfile --version
```

[Kind](https://kind.sigs.k8s.io/docs/user/quick-start/#installation) &mdash; local Kubernetes
cluster.

``` bash
kind --version
```

[Kubectl](https://kubernetes.io/docs/tasks/tools/) &mdash; for interacting with Kubernetes.

``` bash
kubectl version
```
