# First Ptah project

In this tutorial, we will...

TODO: https://diataxis.fr/tutorials/

## Prerequisites

First [Install Ptah](../guides/install.md) and Docker?

## Files

Create a "project" directory and a minimal
[project file](../reference/project.md)

then a minimal [Helmfile](https://helmfile.readthedocs.io/en/latest/#getting-started).

## Deployment

Run

```bash
ptah deploy
```

(this will take 2&ndash;3 minutes)

You may run `kubectl get pods` to verify things have worked.

Then run `ptah forward` and interact with one of the port-forwarded services.

You have deployed a Kubernetes cluster, UI, and interacted with these.
