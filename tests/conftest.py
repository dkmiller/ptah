import os
from collections.abc import Generator
from pathlib import Path

from pytest import fixture


@fixture
def tmp_cwd(tmp_path: Path) -> Generator[Path, None, None]:
    tmp_path.mkdir(parents=True, exist_ok=True)
    cwd = Path.cwd()
    os.chdir(tmp_path)
    yield tmp_path
    os.chdir(cwd)
