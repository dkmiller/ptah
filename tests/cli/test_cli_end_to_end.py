import logging
import time

import httpx
import pytest
from typer.testing import CliRunner

from ptah.cli import app
from ptah.clients import Shell, get
from ptah.models import OperatingSystem

log = logging.getLogger(__name__)

# https://stackoverflow.com/a/38609243
pytestmark = pytest.mark.e2e

# https://stackoverflow.com/a/71264963
if get(OperatingSystem) != OperatingSystem.LINUX:
    pytest.skip(reason="unsupported", allow_module_level=True)


@pytest.mark.parametrize("in_project", ["project-with-fastapi"], indirect=True)
def test_build(in_project):
    runner = CliRunner()
    result = runner.invoke(app, ["build"])
    assert result.exit_code == 0
    assert "Building 1 Docker image" in result.stdout
    assert "Copying 1 manifest" in result.stdout


@pytest.mark.parametrize("in_project", ["project-with-fastapi"], indirect=True)
@pytest.mark.filterwarnings("ignore::pytest.PytestUnraisableExceptionWarning")
def test_deploy(in_project):
    runner = CliRunner()
    result = runner.invoke(app, ["deploy"])
    assert result.exit_code == 0, result.stdout


@pytest.mark.timeout(20)
def test_deployed_service_is_functional():
    # Poor man's external liveness probe.
    success = False
    while not success:
        try:
            response = httpx.get("http://localhost:8000/probe")
            assert response.is_success
            assert "headers" in response.json()
            success = True
        except Exception as e:
            log.warning(e)

            time.sleep(1)


@pytest.mark.parametrize("in_project", ["project-with-fastapi"], indirect=True)
def test_nuke(in_project):
    runner = CliRunner()
    result = runner.invoke(app, ["nuke"])
    assert result.exit_code == 0, result.stdout

    assert not get(Shell).run(["kind", "get", "clusters"])
