import re
from dataclasses import dataclass
from pathlib import Path

from cachelib import BaseCache
from dirhash import dirhash
from inflect import engine
from injector import inject
from rich.console import Console

from ptah.clients.filesystem import Filesystem
from ptah.clients.shell import Shell
from ptah.models import Project


@dataclass
class ImageDefinition:
    """
    Local definition of Docker image.
    """

    location: Path
    name: str
    algorithm: str = "md5"

    @property
    def tag(self):
        dockerignore = self.location.parent / ".dockerignore"

        if dockerignore.exists():
            ignore = dockerignore.read_text().splitlines()
        else:
            ignore = None

        return dirhash(
            str(self.location.parent.absolute()), self.algorithm, ignore=ignore
        )[:7]

    @property
    def uri(self):
        return f"{self.name}:{self.tag}"


@inject
@dataclass
class Docker:
    cache: BaseCache
    console: Console
    engine: engine
    filesystem: Filesystem
    project: Project
    shell: Shell

    def image_name(self, path: Path, match: re.Match) -> str:
        if rv := match.groupdict().get("name"):
            return rv

        # https://stackoverflow.com/a/35188296
        if path.stem.lower() == "dockerfile" and not path.suffix:
            return path.parent.name
        else:
            return path.stem

    def image_definitions(self) -> list[ImageDefinition]:
        root = self.filesystem.project_root()
        rv = []
        for path in root.rglob("*"):
            if m := re.match(self.project.dockerfiles, str(path.relative_to(root))):
                image_name = self.image_name(path, m)
                rv.append(ImageDefinition(path, image_name))

        return rv

    def build(self) -> None:
        build = []
        skip = 0

        for image in self.image_definitions():
            if self.cache.has(f"build__{image.uri}"):
                skip += 1
            else:
                build.append(image)

        noun = self.engine.plural("image", len(build))  # type: ignore
        msg = f"Building {len(build)} Docker {noun}"
        if skip:
            msg += f" ({skip} already built)"
        self.console.print(msg)

        for image in build:
            path = str(image.location.parent)
            self.shell.run(["docker", "build", "-t", image.uri, path])
            self.cache.set(f"build__{image.uri}", "any")

    def push(self) -> None:
        push = []
        skip = 0
        for image in self.image_definitions():
            if self.cache.has(f"push__{image.uri}"):
                skip += 1
            else:
                push.append(image)

        uris = [i.uri for i in push]

        noun = self.engine.plural("image", len(uris))  # type: ignore
        msg = f"Pushing {len(uris)} {noun}"
        if skip:
            msg += f" ({skip} already pushed)"
        self.console.print(msg)

        if push:
            # TODO: handle pushing to a remote registry.
            # https://codeberg.org/hjacobs/pytest-kind/src/branch/main/pytest_kind/cluster.py
            # Sadly, Kind doesn't support incremental loads:
            # https://github.com/kubernetes-sigs/kind/issues/380
            args = ["kind", "load", "docker-image"] + uris
            args += ["--name", self.project.kind.name]
            self.shell.run(args)
            for uri in uris:
                self.cache.set(f"push__{uri}", "any")
