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

then create a file named `ptah.yml`

``` bash
echo '
kind:
  name: minimal
' > ptah.yml
```

then a minimal [Helmfile](https://helmfile.readthedocs.io/en/latest/#getting-started). Let's check
that we have a valid project: the command

``` bash
ptah project
```

should print something including the `name` you specified above.

## Deployment

Now that we have created a Ptah project, we can deploy it. We must always run `ptah ...` commands
in a (sub)directory of the folder containing `ptah.yml`, just like `git` commands only work inside
a Git repo.

Run the command below; this will take 2&ndash;3 minutes to complete.

``` bash
ptah deploy
```

Let's checked that this worked: run `kubectl get pods`; the output should look something like
this.

``` log
NAME                                  READY   STATUS    RESTARTS   AGE
kubernetes-dashboard-57b69f47-f7n8z   1/1     Running   0          31m
```

Then, run `ptah forward` and interact with one of the port-forwarded services.

Finally, run `ptah nuke` to clean up your Kind cluster and port-forwarding background processes.

dashboard: https://stackoverflow.com/a/60264070 sign out then retry.

Congratulations, you have deployed a Kind cluster along with some resources, interacted with
those via port-forwarding, and cleaned everything up.
