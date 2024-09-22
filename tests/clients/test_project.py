from ptah.clients import ProjectClient, get
from ptah.models import Project


def test_project_load(tmp_path):
    path = tmp_path / "ptah.yml"
    path.write_text("""
kind:
  name: some-name
    """)
    client = get(ProjectClient)
    project = client.load(path)
    assert isinstance(project, Project)
    assert project.kind.name == "some-name"
