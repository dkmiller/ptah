# Concepts

This page explains some of the key Ptah concepts.

## Project

"Everything needed for a self-contained service"

[ptah.yml reference](../reference/project.md)

Project contains:

- Images
- Kubernetes manifests
- Optional Helmfile
- Optional Kind cluster configuration

## (Docker) Image

`foo/Dockerfile`

`ptah://foo`

Ptah will handle

- (Re)building the image when necessary
- Loading it into the Kind cluster
- Resolving all image identifiers in your K8s manifests

### Copy / sync

``` dockerfile
COPY source /target
```

``` mermaid
graph LR

subgraph dockerfile["Dockerfile"]

  foo
end

subgraph kubernetes["Kubernetes"]

  pod["pod/container: /bar"]

end

foo -->|"COPY foo /bar"| pod
```
