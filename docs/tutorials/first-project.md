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

Now, let's create a [Ptah project](../reference/project.md). Create a directory to contain it

``` bash
mkdir minimal
cd minimal/
```

then create a file named `ptah.yml` with these contents.

``` yaml
kind:
  name: minimal
```

Next, let's check that we have a valid project: the command

``` bash
ptah project
```

should print something including the `name` you specified above.

## Application

Project configuration isn't very useful on its own. Let's add an application (Docker image +
Kubernetes deployment) of our own. The framework / programming language doesn't matter; it just
needs to be able to run in a Docker container and expose a port.
[FastAPI](https://fastapi.tiangolo.com/) is particularly easy to Dockerize, but you could use
[Flask](https://flask.palletsprojects.com/en/stable/),
[Express.js](https://medium.com/@skhans/building-a-restful-api-with-express-js-a-beginners-guide-dcb1a1e3520d),
etc.


Your project's directory structure should look like below, where `Dockerfile` is our Docker image
definition and `appname.yaml` is a
[Kubernetes deployment](https://spacelift.io/blog/kubernetes-deployment-yaml).

```
ptah.yml
appname/
  Dockerfile
  ...
appname.yaml
```

Let's not worry about manually creating a tag for our Docker image; instead put a reference to our
image inside the Kubernetes deployment spec.

``` yaml
spec:
  containers:
  - name: appname
    image: ptah://appname
```

## Deployment

Now that we have created a Ptah project, we can deploy it. We must always run `ptah ...` commands
in a (sub)directory of the folder containing `ptah.yml`, just like `git` commands only work inside
a Git repo.

Run the command below; this will take 2&ndash;3 minutes to complete.

``` bash
ptah deploy
```

Let's checked that this worked: run `kubectl get pods`. The output should look something like
this.

``` log
NAME                     READY   STATUS    RESTARTS   AGE
appname-57b69f47-f7n8z   1/1     Running   0          3m
```

While `kubectl` is adequate for basic debugging, it can be nice to leverage the Kubernetes UI for
viewing cluster state. Let's add a
[Helmfile](https://helmfile.readthedocs.io/en/latest/#getting-started) provisioning the
[Kubernetes dashboard UI](https://artifacthub.io/packages/helm/k8s-dashboard/kubernetes-dashboard/6.0.8)
and a service account.

``` yaml
repositories:
- name: k8s-dashboard
  url: https://kubernetes.github.io/dashboard
- name: dkmiller
  url: https://dkmiller.github.io/helm-charts/

releases:
- name: kubernetes-dashboard
  chart: k8s-dashboard/kubernetes-dashboard
  version: 6.0.8
- name: admin
  chart: dkmiller/service-account-with-role
  version: 0.0.3
```

Run

``` bash
ptah deploy
```

again to deploy the new changes. Notice the command does not rebuild our Docker image; that will
only happen if we change the underlying definition.

We'll run

``` bash
ptah forward
```

to open the Kubernetes UI in our browser with an auth token copied to the clipboard. Now, we can
use the UI to browse logs from our application, pod state, etc.!

It's a bit slow to rebuild Docker images and redeploy Kubernetes pods every time we want to make
a small change to our application, especially when many frameworks like FastAPI support hot reload.

Let's run the command below.

``` bash
ptah sync
```

Now, any changes you make to your local app definition will be immediately copied over to the
running Docker container.

!!! note "Copy statements must be directories with absolute targets"
    Hot reload only works for `COPY` statements in your Dockerfiles with directory sources and
    absolute targets, e.g. `COPY . /src/`.

## Cleaning up

Finally, run `ptah nuke` to clean up your Kind cluster and port-forwarding background processes.

Congratulations, you have deployed a Kind cluster along with some resources, interacted with
those via port-forwarding, and cleaned everything up.
