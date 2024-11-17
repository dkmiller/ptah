from unittest.mock import MagicMock, patch
from uuid import uuid4

from rich.console import Console

from ptah.clients import Dashboard
from ptah.models.kind import KindCluster
from ptah.models.project import ApiServer, Project


@patch(f"{Dashboard.__module__}.webbrowser.open")
def test_open(mock_open):
    project = Project(KindCluster("name"))
    shell = MagicMock()
    dashboard = Dashboard(Console(), project, shell=shell)
    dashboard.url = lambda: "https://foo"

    dashboard.open()

    assert mock_open.call_args.args == ("https://foo",)
    assert len(shell.call_args_list) == 2


def test_url(port):
    project = Project(KindCluster("name"), ApiServer(port))
    namespace = str(uuid4())
    shell = MagicMock()
    dashboard = Dashboard(Console(), project, shell=shell)

    shell.return_value = namespace
    url = dashboard.url()
    assert f":{port}" in url
    assert f"/namespaces/{namespace}/" in url
