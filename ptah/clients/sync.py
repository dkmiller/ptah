import time
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Optional

from dockerfile_parse import DockerfileParser
from injector import inject
from pathspec import PathSpec
from pathspec.patterns.gitwildmatch import GitWildMatchPattern
from watchdog.events import FileSystemEvent, FileSystemEventHandler
from watchdog.observers import Observer

from ptah.clients.docker import Docker, DockerImage
from ptah.clients.filesystem import Filesystem


class _Handler(FileSystemEventHandler):
    def __init__(self, images: list[DockerImage]) -> None:
        # TODO: take for a _specific_ image:
        # - source (dir) --> target mappings (possibly one, possibly many)
        # - info about target pod / application?
        # - dockerignore
        self.images = images
        # super().__init__(
        #     patterns=[],
        #     ignore_patterns=[],
        #     ignore_directories=True,
        #     case_sensitive=True,
        # )

    @lru_cache
    def dockerignore_spec(self, image_root: Path) -> Optional[PathSpec]:
        dockerignore_path = image_root / ".dockerignore"
        if dockerignore_path.is_file():
            lines = dockerignore_path.read_text().splitlines()
            # https://dev.to/waylonwalker/python-respect-the-gitignore-h9
            spec = PathSpec.from_lines(GitWildMatchPattern, lines)
            return spec

    def is_relevant(self, path: Path) -> bool:
        # rv = False
        # TODO: cache image definition --> Dockerignore spec logic.
        for image in self.images:
            # dockerignore_path = image.location.parent / ".dockerignore"
            # print(f"{path.is_relative_to(image.location.parent)=}")
            # print(f"{dockerignore_path.is_file()=}")
            if path.is_relative_to(image.location.parent):
                if spec := self.dockerignore_spec(image.location.parent):
                    return not spec.match_file(path.relative_to(image.location.parent))
                #     pass
                # if dockerignore_path.is_file():
                #     lines = dockerignore_path.read_text().splitlines()
                #     import pathspec
                #     from pathspec.patterns.gitwildmatch import GitWildMatchPattern
                #     spec = pathspec.PathSpec.from_lines(GitWildMatchPattern, lines)
                #     print(lines)
                #     return not spec.match_file(path.relative_to(image.location.parent))
                return True
        return False

    def on_any_event(self, event: FileSystemEvent) -> None:
        print(f"{event.src_path} {event.event_type} -> {self.is_relevant( Path(event.src_path))}")

@inject
@dataclass(frozen=True)
class Sync:
    docker: Docker
    filesystem: Filesystem
    parser: DockerfileParser

    def foo(self, image: DockerImage):
        self.parser.content = image.location.read_text()
        copy_statements = [x["value"] for x in self.parser.structure if x["instruction"] == "COPY"]
        dir_copy_statements = []
        for statement in copy_statements:
            # TODO: https://docs.docker.com/reference/dockerfile/#copy compliant parsing.
            source, target = statement.split(" ")
            if (image.location.parent / source).is_dir():
                dir_copy_statements.append(statement)
        raise Exception(dir_copy_statements)


# from dockerfile_parse import DockerfileParser
# from pathlib import Path

# dfp = DockerfileParser()
# dfp.content = Path("/Users/dan/src/ptah/examples/fastapi/fastapi/Dockerfile").read_text()

# # Look for "COPY" from "." to something...
# dfp.structure[-2]
# {'instruction': 'COPY', 'startline': 8, 'endline': 8, 'content': 'COPY . /src/\n', 'value': '. /src/'}

    def run(self):
        # for image in self.docker.image_definitions():
        #     self.foo(image)
        observer = Observer()
        event_handler = _Handler(images=self.docker.image_definitions())
        observer.schedule(event_handler, str(self.filesystem.project_root()), recursive=True)
        observer.start()
        try:
            while True:
                time.sleep(1)
        finally:
            observer.stop()
            observer.join()
