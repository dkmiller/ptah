from unittest.mock import MagicMock
from uuid import uuid4

import pytest

from ptah.clients import Kind, get


def test_install(tmp_cwd):
    (tmp_cwd / "ptah.yml").write_text("kind: {name: foo}")
    kind = get(Kind)
    kind.shell = MagicMock()

    kind.install()

    kind.shell.run.assert_called_once()


def test_create(tmp_cwd):
    name = str(uuid4())
    (tmp_cwd / "ptah.yml").write_text(f"kind: {{name: {name}}}")
    kind = get(Kind)
    kind.clusters = lambda: ["c1", "c3"]
    kind.shell = MagicMock()

    kind.create()

    assert name in kind.shell.call_args.args


@pytest.mark.parametrize("in_project", ["project-with-kind-config"], indirect=True)
def test_kind_path(in_project):
    kind = get(Kind)
    path = kind.path()

    assert path
    assert path.name == "kind.yml"


@pytest.mark.parametrize("in_project", ["project-with-kind-config"], indirect=True)
def test_cluster_name(in_project):
    kind = get(Kind)
    assert kind.cluster_name() == "some-kind-cluster-name"
