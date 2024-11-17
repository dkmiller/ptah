from unittest.mock import MagicMock
from uuid import uuid4

import pytest

from ptah.clients import Kind, get
from ptah.models import OperatingSystem


@pytest.mark.skipif(get(OperatingSystem) == OperatingSystem.LINUX, reason="unsupported")
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
