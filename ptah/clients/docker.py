import re
from dataclasses import dataclass
from pathlib import Path

from cachelib import BaseCache
from dirhash import dirhash
from dockerfile_parse import DockerfileParser
from inflect import engine
from injector import inject
from rich.console import Console

from ptah.clients.filesystem import Filesystem
from ptah.clients.kind import Kind
from ptah.clients.shell import Shell
from ptah.models import DockerCopyStatement, DockerImage, Project


@inject
@dataclass
class Docker:
    cache: BaseCache
    console: Console
    engine: engine
    filesystem: Filesystem
    kind: Kind
    project: Project
    shell: Shell

    def copy_statements(self, image: DockerImage) -> list[DockerCopyStatement]:
        parser = DockerfileParser(path=str(image.location))
        copy_statements = [
            statement["value"]
            for statement in parser.structure
            if statement["instruction"] == "COPY"
        ]
        rv = []
        for statement in copy_statements:
            # TODO: https://docs.docker.com/reference/dockerfile/#copy compliant parsing.
            if m := re.match(
                r"(?P<source>[\w|\.|/]+)\s+(?P<target>/[\w|\.|/]+)", statement
            ):
                source = m.group("source")
                target = m.group("target")
                if (image.location.parent / source).is_dir():
                    rv.append(DockerCopyStatement(source, target))
        return rv

    def image_tag(self, location: Path) -> str:
        dockerignore = location.parent / ".dockerignore"

        if dockerignore.exists():
            ignore = dockerignore.read_text().splitlines()
        else:
            ignore = None

        return dirhash(
            str(location.parent.absolute()), self.project.tag_algorithm, ignore=ignore
        )[:7]

    def image_name(self, path: Path, match: re.Match) -> str:
        if rv := match.groupdict().get("name"):
            return rv

        # https://stackoverflow.com/a/35188296
        if path.stem.lower() == "dockerfile" and not path.suffix:
            return path.parent.name
        else:
            return path.stem

    def image_definitions(self) -> list[DockerImage]:
        root = self.filesystem.project_root()
        rv = []
        for path in root.rglob("*"):
            if m := re.match(self.project.dockerfiles, str(path.relative_to(root))):
                image_name = self.image_name(path, m)
                tag = self.image_tag(path)
                rv.append(DockerImage(path, image_name, tag))

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

    def prune(self):
        self.shell("docker", "system", "prune", "-a", "-f", "--volumes")

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
            # Sadly, Kind doesn't support incremental loads:
            # https://github.com/kubernetes-sigs/kind/issues/380
            args = ["kind", "load", "docker-image"] + uris
            args += ["--name", self.kind.cluster_name()]
            self.shell.run(args)
            for uri in uris:
                self.cache.set(f"push__{uri}", "any")
