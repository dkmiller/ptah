import re
from pathlib import Path
from uuid import uuid4

import pytest

from ptah.clients import Docker, get


def test_image_tag_is_consistent(project_cwd):
    (project_cwd / "foo.txt").write_text("bar")
    docker = get(Docker)
    tag = docker.image_tag(project_cwd / "Dockerfile")
    assert tag == "b3c3fbc"


def test_image_tag_respects_dockerignore(project_cwd):
    (project_cwd / "foo.txt").write_text("bar")
    (project_cwd / "bar.txt").write_text(str(uuid4()))
    (project_cwd / ".dockerignore").write_text("bar.txt")
    docker = get(Docker)
    assert docker.image_tag(project_cwd / "Dockerfile") == "3a36db7"


@pytest.mark.parametrize("path,match,expected", [
    (Path("foo/Dockerfile"), re.match(".*", "hi"), "foo"),
    (Path("foo/bar.Dockerfile"), re.match(".*", "hi"), "bar"),
    (Path("foo/bar.Dockerfile"), re.match(r"(?P<name>\w+)", "hi"), "hi"),
])
def test_image_name(project_cwd, path, match, expected):
    docker = get(Docker)

    assert docker.image_name(path, match) == expected
