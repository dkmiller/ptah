import os
from pathlib import Path

import pytest
from pytest import fixture

from ptah.cli import build, project
from ptah.clients import get
from ptah.models import OperatingSystem

# https://stackoverflow.com/a/71264963
if get(OperatingSystem) != OperatingSystem.MACOS:
    pytest.skip(reason="unsupported", allow_module_level=True)


@fixture
def test_project_cwd():
    cwd = Path.cwd()
    target_path = Path(__file__).parents[1] / "test-project"
    os.chdir(target_path)
    yield target_path
    os.chdir(cwd)


def test_project(test_project_cwd):
    project()


def test_build(test_project_cwd):
    build()
