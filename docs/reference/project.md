# Project configuration

The root of every Ptah project is defined by the presence of a configuration file named
`ptah.yml`.

Here is an example illustrating the expected structure, including a
[Kind](https://kind.sigs.k8s.io/docs/user/configuration/) cluster name and
[Kubernetes API](https://kubernetes.io/docs/concepts/overview/kubernetes-api/) port.

``` yaml
kind:
  name: your_kind_cluster_name

api_server:
  port: 9263 # Port for the Kubernetes API server

ui:
  service: kubernetes-dashboard # Name of the service hosting the Kubernetes UI
  user: dashboard-admin # Name of the user to log into the Kubernetes UI with.

manifests: ^(?!helmfile).*\.yaml # Regular expression of Kubernetes manifest files.

build_output: .build # Where to copy rendered manifest files before applying them.
```
