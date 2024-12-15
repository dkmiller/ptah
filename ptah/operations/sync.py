import json
import os
import time
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Optional

from dockerfile_parse import DockerfileParser
from injector import inject
from pathspec import PathSpec
from pathspec.patterns.gitwildmatch import GitWildMatchPattern
from watchdog.events import FileModifiedEvent, FileSystemEventHandler
from watchdog.observers import Observer

from ptah.clients.docker import Docker, DockerImage
from ptah.clients.shell import Shell


class _Handler(FileSystemEventHandler):
    def __init__(
        self,
        source: str,
        pod: str,
        container: str,
        image: DockerImage,
        target: str,
        shell: Shell,
    ):
        print(f"Syncing {source} --> {pod}/{container}:{target}")
        self.source = source
        self.pod = pod
        self.container = container
        self.image = image
        self.target = target
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
        root = self.image.location.parent
        if path.is_relative_to(root):
            if spec := self.dockerignore_spec(root):
                return not spec.match_file(path.relative_to(root))
            return True
        return False

    # TODO (https://github.com/katjuncker/node-kubycat/blob/main/src/Kubycat.ts):
    # - on_created
    # - on_deleted (kubectl exec /bin/bash -c "rm -rf ...")
    # - on_moved

    def on_modified(self, event):
        if not isinstance(event.src_path, str):
            return
        path = Path(event.src_path)
        if isinstance(event, FileModifiedEvent) and self.is_relevant(path):
            relative = path.relative_to(self.image.location.parent)
            target = os.path.join(self.target, relative)
            print(f"{event.src_path} -> {self.pod}/{self.container}:{target}")
            self.shell(
                "kubectl",
                "cp",
                event.src_path,
                f"{self.pod}:{target}",
                "-c",
                self.container,
            )


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

    def pods(self) -> dict:
        # TODO: move this to Kubernetes class.
        return json.loads(self.shell("kubectl", "get", "pods", "-o", "json"))

    def run(self):
        images = self.docker.image_definitions()
        observer = Observer()
        for pod in self.pods()["items"]:
            pod_name = pod["metadata"]["name"]
            for container in pod["spec"]["containers"]:
                container_name = container["name"]
                for image in images:
                    for copy_statement in self.docker.copy_statements(image):
                        # TODO: better logic here.
                        if container["image"].startswith(image.name + ":"):
                            event_handler = _Handler(
                                source=copy_statement.source,
                                pod=pod_name,
                                container=container_name,
                                image=image,
                                target=copy_statement.target,
                                shell=self.shell,
                            )

                            observer.schedule(
                                event_handler,
                                str(image.location.parent),
                                recursive=True,
                            )

        # TODO: context manager.
        observer.start()
        try:
            while True:
                time.sleep(1)
        finally:
            observer.stop()
            observer.join()
