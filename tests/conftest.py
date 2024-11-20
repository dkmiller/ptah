import os
import random
from collections.abc import Generator
from pathlib import Path

from pytest import fixture


@fixture
def port() -> int:
    return random.randint(49152, 65535)


@fixture
def project_cwd(tmp_cwd) -> Generator[Path, None, None]:
    (tmp_cwd / "ptah.yml").write_text("kind: {name: foo}")
    yield tmp_cwd


@fixture
def tmp_cwd(tmp_path: Path) -> Generator[Path, None, None]:
    tmp_path.mkdir(parents=True, exist_ok=True)
    cwd = Path.cwd()
    os.chdir(tmp_path)
    yield tmp_path
    os.chdir(cwd)
