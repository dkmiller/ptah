import re
from pathlib import Path
from unittest.mock import MagicMock
from uuid import uuid4

import pytest

from ptah.clients import Docker, get
from ptah.models import DockerCopyStatement, DockerImage


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


@pytest.mark.parametrize(
    "path,match,expected",
    [
        (Path("foo/Dockerfile"), re.match(".*", "hi"), "foo"),
        (Path("foo/bar.Dockerfile"), re.match(".*", "hi"), "bar"),
        (Path("foo/bar.Dockerfile"), re.match(r"(?P<name>\w+)", "hi"), "hi"),
    ],
)
def test_image_name(project_cwd, path, match, expected):
    docker = get(Docker)

    assert docker.image_name(path, match) == expected


def test_image_definitions(project_cwd):
    foo = project_cwd / "foo"
    foo.mkdir(parents=True, exist_ok=True)
    (foo / "foo.txt").write_text("foo contents")
    (foo / "Dockerfile").touch()

    bar = project_cwd / "bar"
    bar.mkdir(parents=True, exist_ok=True)
    (bar / "bar.txt").write_text("bar contents")
    (bar / "barname.Dockerfile").touch()

    docker = get(Docker)
    assert sorted(docker.image_definitions(), key=lambda d: d.tag) == [
        DockerImage(foo / "Dockerfile", "foo", "8d36a53"),
        DockerImage(bar / "barname.Dockerfile", "bar", "977e528"),
    ]


def test_build(capsys, project_cwd):
    foo = project_cwd / "foo"
    foo.mkdir(parents=True, exist_ok=True)
    (foo / "foo.txt").write_text("foo contents")
    (foo / "Dockerfile").touch()

    docker = get(Docker)

    docker.shell = MagicMock()

    docker.build()

    bar = project_cwd / "bar"
    bar.mkdir(parents=True, exist_ok=True)
    (bar / "bar.txt").write_text("bar contents")
    (bar / "barname.Dockerfile").touch()

    docker.build()

    lines = capsys.readouterr().out.splitlines()

    assert "Building 1 Docker image" in lines
    assert "Building 1 Docker image (1 already built)" in lines


def test_push(capsys, project_cwd):
    foo = project_cwd / "foo"
    foo.mkdir(parents=True, exist_ok=True)
    (foo / "foo.txt").write_text("foo contents")
    (foo / "Dockerfile").touch()

    docker = get(Docker)

    docker.shell = MagicMock()

    docker.push()

    bar = project_cwd / "bar"
    bar.mkdir(parents=True, exist_ok=True)
    (bar / "bar.txt").write_text("bar contents")
    (bar / "barname.Dockerfile").touch()

    docker.push()

    lines = capsys.readouterr().out.splitlines()

    assert "Pushing 1 image" in lines
    assert "Pushing 1 image (1 already pushed)" in lines


def test_copy_statements_one_copy(project_cwd):
    docker = get(Docker)
    (project_cwd / "foo").mkdir()
    (project_cwd / "foo.Dockerfile").write_text("FROM ubuntu\nCOPY foo /bar")
    docker.project.dockerfiles = r"(?i)(?P<name>\w+)\.Dockerfile"
    images = docker.image_definitions()
    assert len(images) == 1
    assert docker.copy_statements(images[0]) == [DockerCopyStatement("foo", "/bar")]


def test_copy_statements_multiple_copy_statements(project_cwd):
    docker = get(Docker)
    (project_cwd / "foo").mkdir()
    (project_cwd / "foo2").mkdir()
    (project_cwd / "foo3/foo4").mkdir(parents=True)
    (project_cwd / "foo.Dockerfile").write_text(
        """
FROM ubuntu
COPY foo /bar
COPY foo2 /bar2/baz
COPY foo3/foo4 /bar3/bar4
"""
    )
    docker.project.dockerfiles = r"(?i)(?P<name>\w+)\.Dockerfile"
    images = docker.image_definitions()
    assert len(images) == 1
    assert docker.copy_statements(images[0]) == [
        DockerCopyStatement("foo", "/bar"),
        DockerCopyStatement("foo2", "/bar2/baz"),
        DockerCopyStatement("foo3/foo4", "/bar3/bar4"),
    ]


def test_copy_statements_ignores_nonabsolute(project_cwd):
    docker = get(Docker)
    (project_cwd / "foo.Dockerfile").write_text("FROM ubuntu\nCOPY foo bar")
    docker.project.dockerfiles = r"(?i)(?P<name>\w+)\.Dockerfile"
    images = docker.image_definitions()
    assert len(images) == 1
    assert docker.copy_statements(images[0]) == []
