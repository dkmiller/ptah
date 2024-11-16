import typer
from typer.main import get_command

from ptah.clients import Forward, Helmfile, Kind, Project, Version, get

app = typer.Typer()


@app.command()
def project():
    """
    Echo the current project configuration, including default values, to standard output.
    """
    print(get(Project).load())


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
    project = get(Project).load()
    kind.create(project)

    helm = get(Helmfile)
    helm.ensure_installed()
    helm.build()
    helm.apply()

    # TODO: kill and then re-forward?


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
    forward = get(Forward)
    forward.terminate()

    kind = get(Kind)
    project = get(Project).load()
    kind.delete(project)


# Create a "nicely named" Click command object for generated docs.
ptah = get_command(app)
