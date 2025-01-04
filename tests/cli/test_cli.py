import re

from click import BaseCommand
from typer.testing import CliRunner

from ptah.cli import app


def test_cli_click_object():
    from ptah.cli import ptah

    assert isinstance(ptah, BaseCommand)


def test_cli_version():
    runner = CliRunner()
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert re.match(r"\d+\.\d+\.\d+", result.stdout)
