from ptah.clients import Project, get
from ptah.models import Project as Model


def test_project_load(tmp_path):
    path = tmp_path / "ptah.yml"
    path.write_text("""
kind:
  name: some-name
    """)
    client = get(Project)
    project = client.load(path)
    assert isinstance(project, Model)
    assert project.kind.name == "some-name"


def test_project_load_api_server(tmp_path):
    path = tmp_path / "ptah.yml"
    path.write_text("""
kind:
  name: some-name
api_server:
  port: 9263
    """)
    client = get(Project)
    project = client.load(path)
    assert isinstance(project, Model)
    assert project.api_server.port == 9263
