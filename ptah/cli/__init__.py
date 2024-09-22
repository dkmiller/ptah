import typer

from ptah.clients import Kind, ProjectClient, get

app = typer.Typer()


@app.command()
def project():
    print(get(ProjectClient).load())


@app.command()
def version():
    pass


@app.command()
def deploy():
    kind = get(Kind)
    if not kind.is_installed():
        kind.install()
    project = get(ProjectClient).load()
    kind.create(project)
