import os
from pathlib import Path

import pytest
from pytest import fixture

from ptah.cli import build, deploy, nuke, project
from ptah.clients import get
from ptah.models import OperatingSystem

# TODO: systematic way of skipping the slow tests by default.

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


def test_deploy(test_project_cwd):
    assert os.system("brew install docker") == 0
    assert os.system("brew install kubectl") == 0
    deploy()


def test_nuke(test_project_cwd):
    nuke()


# TODO: https://kubernetes.io/docs/tasks/tools/install-kubectl-macos/#install-with-homebrew-on-macos

# @pytest.mark.timeout(60)
