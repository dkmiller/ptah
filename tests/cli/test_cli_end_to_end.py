import time

import httpx
import pytest
from typer.testing import CliRunner

from ptah.cli import app
from ptah.clients import Shell, get
from ptah.models import OperatingSystem

# https://stackoverflow.com/a/71264963
if get(OperatingSystem) != OperatingSystem.LINUX:
    pytest.skip(reason="unsupported", allow_module_level=True)


@pytest.mark.e2e
@pytest.mark.parametrize("in_project", ["project-with-fastapi"], indirect=True)
@pytest.mark.timeout(60)
def test_build(in_project):
    runner = CliRunner()
    result = runner.invoke(app, ["build"])
    assert result.exit_code == 0
    assert "Building 1 Docker image" in result.stdout
    assert "Copying 1 manifest" in result.stdout


@pytest.mark.e2e
@pytest.mark.parametrize("in_project", ["project-with-fastapi"], indirect=True)
@pytest.mark.timeout(60 * 5)
@pytest.mark.filterwarnings("ignore::pytest.PytestUnraisableExceptionWarning")
def test_deploy(in_project):
    runner = CliRunner()
    result = runner.invoke(app, ["deploy"])
    assert result.exit_code == 0, result.stdout


@pytest.mark.e2e
def test_deployed_service_is_functional():
    # It takes the port-forwarding process a second to boot up.
    time.sleep(1)

    response = httpx.get("http://localhost:8000/probe")
    assert response.is_success
    assert "headers" in response.json()


@pytest.mark.e2e
@pytest.mark.parametrize("in_project", ["project-with-fastapi"], indirect=True)
@pytest.mark.timeout(30)
def test_nuke(in_project):
    runner = CliRunner()
    result = runner.invoke(app, ["nuke"])
    assert result.exit_code == 0, result.stdout

    assert not get(Shell).run(["kind", "get", "clusters"])
