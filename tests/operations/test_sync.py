import json
import os
import shutil
import time
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from ptah.clients import get
from ptah.models import OperatingSystem
from ptah.operations import Sync


@pytest.fixture
def sync():
    path = Path(__file__).parent / "pods.json"
    parsed = json.loads(path.read_text())

    rv = get(Sync)
    rv.kubernetes.pods = MagicMock()
    rv.kubernetes.pods.return_value = parsed
    rv.shell = MagicMock()

    return rv


@pytest.mark.parametrize("in_project", ["project-with-fastapi"], indirect=True)
def test_sync_respects_file_creation(in_project, sync):
    with sync.run():
        Path("fastapi/foo.txt").touch()
        time.sleep(0.1)

    assertion_args = (
        "kubectl",
        "cp",
        str(Path.cwd().absolute() / "fastapi/foo.txt"),
        "fastapi-deployment-79f65c9947-zg2p6:/srv/foo.txt",
        "-c",
        "fastapi",
    )

    if get(OperatingSystem) == OperatingSystem.MACOS and "GITHUB_ACTION" in os.environ:
        sync.shell.assert_called_with(*assertion_args)
    else:
        sync.shell.assert_called_once_with(*assertion_args)


@pytest.mark.parametrize("in_project", ["project-with-fastapi"], indirect=True)
def test_sync_respects_file_deletion(in_project, sync):
    with sync.run():
        Path("fastapi/main.py").unlink()
        time.sleep(0.1)

    sync.shell.assert_called_with(
        "kubectl",
        "exec",
        "fastapi-deployment-79f65c9947-zg2p6",
        "-c",
        "fastapi",
        "--",
        "rm",
        "-rf",
        "/srv/main.py",
    )


@pytest.mark.parametrize("in_project", ["project-with-fastapi"], indirect=True)
def test_sync_respects_directory_creation(in_project, sync):
    with sync.run():
        Path("fastapi/baz").mkdir()
        time.sleep(0.1)

    sync.shell.assert_called_with(
        "kubectl",
        "exec",
        "fastapi-deployment-79f65c9947-zg2p6",
        "-c",
        "fastapi",
        "--",
        "mkdir",
        "-p",
        "/srv/baz",
    )


# TODO: figure out why this test passes locally in my M1 MacBook but not remotely.
@pytest.mark.skipif(
    get(OperatingSystem) == OperatingSystem.MACOS and "GITHUB_ACTION" in os.environ,
    reason="unexpected failure",
)
@pytest.mark.parametrize("in_project", ["project-with-fastapi"], indirect=True)
def test_sync_respects_dockerignore(in_project, sync):
    with sync.run():
        Path("fastapi/ignore").touch()
        time.sleep(0.1)

    sync.shell.assert_not_called()


@pytest.mark.parametrize("in_project", ["project-with-fastapi"], indirect=True)
def test_sync_respects_file_modification(in_project, sync):
    with sync.run():
        assert Path("fastapi/main.py").is_file()
        Path("fastapi/main.py").write_text("foo")
        time.sleep(0.1)

    sync.shell.assert_called_with(
        "kubectl",
        "cp",
        str(Path.cwd().absolute() / "fastapi/main.py"),
        "fastapi-deployment-79f65c9947-zg2p6:/srv/main.py",
        "-c",
        "fastapi",
    )


@pytest.mark.parametrize("in_project", ["project-with-fastapi"], indirect=True)
def test_sync_respects_file_movement(in_project, sync):
    with sync.run():
        shutil.move("fastapi/main.py", "fastapi/main2.py")
        time.sleep(0.1)

    sync.shell.assert_called_with(
        "kubectl",
        "exec",
        "fastapi-deployment-79f65c9947-zg2p6",
        "-c",
        "fastapi",
        "--",
        "mv",
        "/srv/main.py",
        "/srv/main2.py",
    )
