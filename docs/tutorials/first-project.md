# First Ptah project

<!-- https://diataxis.fr/tutorials/ -->

In this tutorial, we will create, deploy, and iterate on our first Ptah project.

## Prerequisites

First, install the [Docker CLI](https://docs.docker.com/engine/install/),
[kubectl](https://kubernetes.io/docs/tasks/tools/), and the
[Ptah CLI](../guides/install.md). It is likely you already have the first two installed, and
simply need to run

``` bash
pip3 install --upgrade ptah-cli

ptah version
```

The output should include a version number.

## Project

Now that we have installed the prerequisites, let's create a
[Ptah project](../reference/project.md). Create a directory to contain it

``` bash
mkdir minimal
cd minimal/
```

then create a file named `ptah.yml`

``` bash
echo '
kind:
  name: minimal
' > ptah.yml
```

then a minimal [Helmfile](https://helmfile.readthedocs.io/en/latest/#getting-started).

the output of `ls -R` should look like

``` log
helmfile.yaml	ptah.yml
```

## Deployment

Run

Must always run `ptah` commands in the context of a `ptah` project, just like the `git` CLI and
Git repos.

``` bash
ptah deploy
```

(this will take 2&ndash;3 minutes)

Let's checked that this worked: run `kubectl get pods`

Then run `ptah forward` and interact with one of the port-forwarded services.

Oops! Need service account: add one, `ptah deploy` again.

Remember that we already deployed the cluster; it should be much faster this time.

You have deployed a Kubernetes cluster, UI, and interacted with these, and made changes.
