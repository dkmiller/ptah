from uuid import uuid4

import pytest

from ptah.cli import project
from ptah.models import Serialization


@pytest.mark.parametrize("format", [Serialization.json, Serialization.yaml])
def test_cli_project(format, capsys, tmp_cwd):
    random = str(uuid4())
    (tmp_cwd / "ptah.yml").write_text(f"kind: {{name: {random}}}")
    project(output=format)
    assert random in capsys.readouterr().out
