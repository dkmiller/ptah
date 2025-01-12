import json
import time
from dataclasses import asdict

import typer
from typer.main import get_command

from ptah.clients import (
    Dashboard,
    Docker,
    Filesystem,
    Forward,
    Helmfile,
    Kind,
    Kubernetes,
    Project,
    Ssh,
    Version,
    Yaml,
    get,
)
from ptah.models import Serialization
from ptah.operations import Sync

app = typer.Typer(pretty_exceptions_enable=False)


def version(value: bool):
    """
    Current version of the Ptah CLI.
    """
    if value:
        print(get(Version).version())
        raise typer.Exit()


@app.callback()
def common(
    ctx: typer.Context,
    version: bool = typer.Option(None, "--version", callback=version),
):
    """
    https://stackoverflow.com/a/71008105
    """
    pass


@app.command()
def project(output: Serialization = Serialization.yaml):
    """
    Echo the current project configuration, including default values, to standard output using
    the specified format.
    """
    deserialized = get(Project).load()
    match output:
        case Serialization.json:
            serialized = json.dumps(asdict(deserialized), indent=3)
        case Serialization.yaml:
            serialized = get(Yaml).dumps(deserialized)
    print(serialized)


@app.command(name="build")
def _build():
    """
    Copy all Kubernetes manifests from the current project into the `build_output` directory.
    """
    docker = get(Docker)
    docker.build()

    k8s = get(Kubernetes)
    k8s.build()


@app.command()
def deploy(build: bool = True, forward: bool = True, sync: bool = False):
    """
    Build the project, ensure the Kind CLI and cluster exit, sync and apply Helm charts, apply
    Kubernetes manifests, and set up port-forwarding from the cluster to localhost.
    """
    if build:
        _build()

    kind = get(Kind)
    kind.ensure_installed()
    kind.create()

    helm = get(Helmfile)
    helm.sync()
    helm.apply()

    docker = get(Docker)
    docker.push()
    get(Kubernetes).apply()

    if forward:
        _forward(kill=True)
        _forward(kill=False)

    if sync:
        _sync()


@app.command(name="forward")
def _forward(kill: bool = False):
    """
    Forward the Kubernetes API server and all deployment ports to localhost; alternatively kill
    all active "port forward" sessions.
    """
    forward = get(Forward)
    if kill:
        forward.terminate()
    else:
        forward.ensure()


@app.command()
def dashboard():
    """
    Open the Kubernetes dashboard with a prepared bearer token for authentication.
    """
    get(Dashboard).open()


@app.command()
def nuke(docker: bool = True, kind: bool = True):
    """
    Forcibly delete the Kind cluster, all related resources, and prune dangling Docker images.
    """
    _forward(kill=True)

    if docker:
        get(Docker).prune()

    if kind:
        get(Kind).delete()

    filesystem = get(Filesystem)
    filesystem.delete(filesystem.cache_location())


@app.command(name="sync")
def _sync():
    """
    Find all Ptah-managed Docker images containing copy statements like

    > COPY source /target

    and synchronize the contents of the source directory with the target directory in all running
    pods using that image.
    """
    with get(Sync).run():
        while True:
            time.sleep(1)


@app.command()
def ssh(app: str):
    """
    Find the first pod with provided app name; then SSH (`kubectl exec`) into it.
    """
    get(Ssh).run(app)


# Create a "nicely named" Click command object for generated docs.
ptah = get_command(app)
