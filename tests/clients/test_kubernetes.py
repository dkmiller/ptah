from pathlib import Path
from uuid import uuid4

from ptah.clients import Kubernetes, get


def test_build(tmp_cwd):
    build_output = str(uuid4())
    (tmp_cwd / "ptah.yml").write_text(
        f"""
kind:
  name: some-name

build_output: {build_output}
manifests: foo
"""
    )
    (tmp_cwd / "foo").touch()
    (tmp_cwd / "bar").touch()

    get(Kubernetes).build()

    output_path = Path(build_output)
    assert output_path.is_dir()

    assert list(output_path.glob("*")) == [output_path / "foo"]
