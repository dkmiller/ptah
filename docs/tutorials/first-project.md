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

Project configuration isn't very useful on its own. let's add a
[Helmfile](https://helmfile.readthedocs.io/en/latest/#getting-started) provisioning the
[Kubernetes dashboard UI](https://artifacthub.io/packages/helm/k8s-dashboard/kubernetes-dashboard/6.0.8).

```yaml
repositories:
- name: k8s-dashboard
  url: https://kubernetes.github.io/dashboard
releases:
- name: kubernetes-dashboard
  chart: k8s-dashboard/kubernetes-dashboard
  version: 6.0.8
  values:
  - name:
      fullnameOverride: kubernetes-dashboard
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
NAME                                  READY   STATUS    RESTARTS   AGE
kubernetes-dashboard-57b69f47-f7n8z   1/1     Running   0          3m
```

While `kubectl` is adequate for basic debugging, it can be nice to leverage the Kubernetes UI for
viewing cluster state. Let's add a file `admin.yaml` to our Ptah project with contents
from [sa_cluster_admin.yaml](https://github.com/justmeandopensource/kubernetes/blob/e506f1abf9728a646ce29addce9f21432c6c2eb7/dashboard/sa_cluster_admin.yaml), and tell Ptah the service running the UI and the service account
needed to access it by adding this to `ptah.yml`.

``` yaml
ui:
  service: kubernetes-dashboard
  user: dashboard-admin
```

Let's run `ptah deploy` again; notice it is much faster this time. Now, we'll run

``` bash
ptah forward
```

to open the Kubernetes UI in our browser with an auth token copied to the clipboard. Now, we can
use the UI to browse logs, pod state, etc.!

## Cleaning up

Finally, run `ptah nuke` to clean up your Kind cluster and port-forwarding background processes.

Congratulations, you have deployed a Kind cluster along with some resources, interacted with
those via port-forwarding, and cleaned everything up.
