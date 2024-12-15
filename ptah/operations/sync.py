import time
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Optional

from dockerfile_parse import DockerfileParser
from injector import inject
from pathspec import PathSpec
from pathspec.patterns.gitwildmatch import GitWildMatchPattern
from watchdog.events import FileModifiedEvent, FileSystemEvent, FileSystemEventHandler
from watchdog.observers import Observer

from ptah.clients.docker import Docker, DockerImage
from ptah.clients.shell import Shell


@dataclass
class Mapping:
    pod: str
    container: str
    image: DockerImage
    source: str
    """
    Source directory, relative to the Docker image definition root.
    """
    target: str
    """
    Target directory in the Docker container.
    """

    def absolute_source(self):
        return self.image.location.parent / self.source
    

class _Handler(FileSystemEventHandler):
    def __init__(self, mapping: Mapping, shell: Shell) -> None:
        # TODO: take for a _specific_ image:
        # - source (dir) --> target mappings (possibly one, possibly many)
        # - info about target pod / application?
        # - dockerignore
        self.mapping = mapping
        self.shell = shell

    @lru_cache
    def dockerignore_spec(self, image_root: Path) -> Optional[PathSpec]:
        dockerignore_path = image_root / ".dockerignore"
        if dockerignore_path.is_file():
            lines = dockerignore_path.read_text().splitlines()
            # https://dev.to/waylonwalker/python-respect-the-gitignore-h9
            spec = PathSpec.from_lines(GitWildMatchPattern, lines)
            return spec

    def is_relevant(self, path: Path) -> bool:
        root = self.mapping.image.location.parent
        if path.is_relative_to(root):
            if spec := self.dockerignore_spec(root):
                return not spec.match_file(path.relative_to(root))
            return True
        return False

    # TODO: imititate
    # https://github.com/katjuncker/node-kubycat/blob/main/src/Kubycat.ts#L244

    def on_any_event(self, event: FileSystemEvent) -> None:
        print(f"{event.src_path} {event.event_type} -> {self.is_relevant( Path(event.src_path))}")
        # Changed / created: kubectl cp
        # Deleted: kubectl exec /bin/bash -c "rm -rf ..."
        #   kubectl cp /tmp/foo <some-pod>:/tmp/bar -c <specific-container>

    def on_modified(self, event):
        path = Path(event.src_path)
        if isinstance(event, FileModifiedEvent) and self.is_relevant(path):
            relative = path.relative_to(self.mapping.image.location.parent)
            import os
            target = os.path.join(self.mapping.target, relative)
            print(f"{event.src_path} -> {target}")
            self.shell("kubectl", "cp", event.src_path, f"{self.mapping.pod}:{target}", "-c", self.mapping.container)

@inject
@dataclass
class Sync:
    """
    ALGO:
    - Find all "container -> Docker image" mappings.
        - Need namespace + pod(s) ...
    - Find all "Docker image -> (copy: source -> target)" mappings.
    - For each (container, Docker image, copy: source -> target) spawn a filesystem event handler.
        - Handler watches (image root) / source for changes that pass the .dockerignore
        - Handler propagates the change via kubectl ... commands to the (namespace + pod + container).
    """
    docker: Docker
    parser: DockerfileParser
    shell: Shell

    def run(self):
        images = self.docker.image_definitions()
        import json
        pods = json.loads(self.shell("kubectl", "get", "pods", "-o", "json"))
        stuff_to_do: list[Mapping] = []
        for pod in pods["items"]:
            for container in pod["spec"]["containers"]:
                for image in images:
                    for copy_statement in self.docker.copy_statements(image):
                        if container["image"].startswith(image.name + ":"):
                            stuff_to_do.append(
                                Mapping(
                                    pod=pod["metadata"]["name"],
                                    container=container["name"],
                                    image=image,
                                    source=copy_statement.source,
                                    target=copy_statement.target,
                                ))
        observer = Observer()
        for mapping in stuff_to_do:
            print(f"{mapping.absolute_source()} --> {mapping.pod}/{mapping.container}:{mapping.target}")
            event_handler = _Handler(mapping=mapping, shell=self.shell)
            observer.schedule(event_handler, str(mapping.image.location.parent), recursive=True)

        observer.start()
        try:
            while True:
                time.sleep(1)
        finally:
            observer.stop()
            observer.join()
