import httpx
import pytest
from typer.testing import CliRunner

from ptah.cli import app
from ptah.clients import get
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
    assert result.exit_code == 0, f"STDOUT: {result.stdout} + STDERR: {result.stderr}"


@pytest.mark.e2e
@pytest.mark.timeout(30)
def test_deployed_service_is_functional():
    success = False
    while not success:
        try:
            response = httpx.get("http://localhost:8000/probe")
            assert response.is_success
            assert "headers" in response.json()
            success = True
        except Exception as e:
            print(e)
            import time

            time.sleep(1)


@pytest.mark.e2e
@pytest.mark.parametrize("in_project", ["project-with-fastapi"], indirect=True)
@pytest.mark.timeout(30)
def test_nuke(in_project):
    runner = CliRunner()
    result = runner.invoke(app, ["nuke"])
    assert result.exit_code == 0, f"STDOUT: {result.stdout} + STDERR: {result.stderr}"

    # TODO: assert no running Kind clusters.
