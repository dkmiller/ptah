# Concepts

This page explains the key concepts you will encounter while doing Kubernetes development with Ptah.

## Project

A _Ptah project_ is a self-contained set of Kubernetes configuration, centered around a
`ptah.yml` file. See the [ptah.yml reference](../reference/project.md) for a complete set of
configuration options, but in general a project contains:

- Docker image definitions (`Dockerfile`s that will be built on the fly)
- Kubernetes manifests, optionally referencing the Docker image definitions
- A [Helmfile](https://helmfile.readthedocs.io/) referencing external Helm charts
- [Kind cluster configuration](https://kind.sigs.k8s.io/docs/user/configuration/), e.g. local
  volume mounts / port forwarding.

Here are some examples of Ptah projects:

- [Kubernetes dashboard + service account](https://github.com/dkmiller/ptah/tree/main/examples/minimal)
- [FastAPI-defined REST API](https://github.com/dkmiller/ptah/tree/main/examples/fastapi)
- [FastAPI REST API + MySQL database](https://github.com/dkmiller/ptah/tree/main/examples/db)

## (Docker) Image

Have you ever felt frustrated at the repeated sequence of building a local Docker image,
copy/pasting its tag into your pod spec, loading the image into your Kind cluster, then finally
applying your Kubernetes manifests? Then Ptah's Docker image URIs are just for you!

Within a Ptah project, you may define Docker images by putting a Dockerfile in a folder:

```
myimage/
  Dockerfile
```

... and then putting a URI like this in your Kubernetes manifest.

``` yaml
image: ptah://myimage
```

When you run `deploy`, the Ptah CLI will handle:

- Creating an image URI like `myimage:b3c3fbc`, where the tag is computed using the
  [dirhash](https://github.com/andhus/dirhash) of the directory containing the `Dockerfile`
- Building the image if necessary, and loading it into the local Kind cluster.
- Replacing all Kubernetes manifest references `ptah://myimage` with the image URI before applying
  them.

### Copy / sync

Many application frameworks (e.g., [FastAPI](https://fastapi.tiangolo.com/)) support "hot reload",
immediately picking up changes to their local source code.

If a Docker image in your Ptah project has a copy statement like this one (note the absolute
target)

``` dockerfile
COPY source /target
```

then the [`ptah sync` and `ptah deploy --sync` command](../reference/cli.md) will synchronize your
local folder `source` (relative to the directory containing the Dockerfile) and `/target` in all
(pod, container) combinations referencing that Docker image. This way, changes to your local source
code will propagate to the running Docker containers.

``` mermaid
graph LR

subgraph local["Local filesystem"]
  dockerfile["Dockerfile <br /> COPY source /target"]

  source["./source"]
end

subgraph kubernetes["Kubernetes"]

  subgraph pod
    container["container <br /> /target"]
  end

end

source -->|synchronize| container
```
