from uuid import uuid4

import pytest

from ptah.clients import Filesystem, PtahPanic, get
from ptah.models import PACKAGE_NAME


def test_delete_when_target_does_not_exist(tmp_path):
    path = tmp_path / str(uuid4())
    get(Filesystem).delete(path)


def test_package_root_contains_clients():
    filesystem = get(Filesystem)
    clients = filesystem.package_root() / "clients"
    assert clients.is_dir()


def test_pyproject():
    filesystem = get(Filesystem)
    pyproject = filesystem.pyproject()
    assert pyproject.is_file()
    assert PACKAGE_NAME in pyproject.read_text()


def test_project_path_when_none_exists():
    filesystem = get(Filesystem)

    with pytest.raises(PtahPanic) as exc_info:
        filesystem.project_path()

    assert exc_info.value.args[0] == 1


@pytest.mark.parametrize("depth", [1, 5, 10])
def test_project_path_in_subdirectory(depth, tmp_path):
    filesystem = get(Filesystem)

    project_path = tmp_path / "ptah.yml"
    project_path.touch()
    location = tmp_path

    for _ in range(depth):
        location = location / str(uuid4())[:8]

    location.mkdir(parents=True)

    assert filesystem.project_path(location) == project_path
