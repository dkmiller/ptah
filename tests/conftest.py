import os
import random
import shutil
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


@fixture
def in_project(request, tmp_cwd):
    """
    Run tests using this fixture inside a temporary current working directory with a full copy
    of the configured test project directory, via a decorator like:

    ```python
    @pytest.mark.parametrize("in_project", ["name-of-directory"], indirect=True)
    ```

    ([More on indirect parameterization](https://stackoverflow.com/a/33879151).)
    """
    source = Path(__file__).parent / "projects" / request.param
    # https://stackoverflow.com/a/12687372
    shutil.copytree(source, Path.cwd(), dirs_exist_ok=True)
    yield
