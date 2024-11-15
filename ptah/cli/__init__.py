import typer

from ptah.clients import Forward, Helmfile, Kind, ProjectClient, Version, get

app = typer.Typer()


@app.command()
def project():
    """
    Echo the current project configuration, including default values, to standard output.
    """
    print(get(ProjectClient).load())


@app.command()
def version():
    """
    Current version of the Ptah CLI.
    """
    print(get(Version).version())


@app.command()
def deploy():
    kind = get(Kind)
    kind.ensure_installed()
    project = get(ProjectClient).load()
    kind.create(project)

    helm = get(Helmfile)
    helm.ensure_installed()
    helm.build()
    helm.apply()


@app.command()
def forward(kill: bool = False):
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
def nuke():
    """
    Forcibly delete the Kind cluster and all related resources.
    """
    kind = get(Kind)
    project = get(ProjectClient).load()
    kind.delete(project)
