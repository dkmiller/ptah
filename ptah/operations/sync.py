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
from watchdog import events
from watchdog.events import DirMovedEvent, FileDeletedEvent, FileMovedEvent, FileModifiedEvent, FileSystemEventHandler
from watchdog.observers import Observer

from ptah.clients.docker import Docker, DockerImage
from ptah.clients.shell import Shell, PtahShellError


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

    def on_any_event(self, event) -> None:
        print(event)

    def is_relevant(self, path: Path) -> bool:
        root = self.image.location.parent
        if path.is_relative_to(root):
            if spec := self.dockerignore_spec(root):
                return not spec.match_file(path.relative_to(root))
            return True
        return False

    # TODO (https://github.com/katjuncker/node-kubycat/blob/main/src/Kubycat.ts):
    # - on_deleted (kubectl exec /bin/bash -c "rm -rf ...")
    # - on_moved

    def foo__(self, pathish: bytes | str) -> Optional[str]:
        if not isinstance(pathish, str):
            # TODO: warning.
            return
        path = Path(pathish)
        if self.is_relevant(path):
            relative = path.relative_to(self.image.location.parent)
            return os.path.join(self.target, relative)

    # TODO:
    # no "file" operations can assume the source file still exists; it may have been deleted by
    # an editor like Vim before Python has a chance to do anything with it:
    # https://github.com/neovim/neovim/issues/3460

    def copy(self, pathish: bytes | str):
        if target := self.foo__(pathish):
            # if not Path(target).is_file() and not Path(target).is_dir():
            #     return
            print(f"{pathish} -> {self.pod}/{self.container}:{target}")
            try:
                self.shell(
                    "kubectl",
                    "cp",
                    pathish,
                    f"{self.pod}:{target}",
                    "-c",
                    self.container,
                )
            except PtahShellError:
                pass

    def delete(self, pathish: bytes | str):
        if target := self.foo__(pathish):
            self.exec("rm", "-rf", target)

    def exec(self, *args):
        print(args)
        try:
            self.shell(
                "kubectl",
                "exec",
                self.pod,
                "-c",
                self.container,
                "--",
                *args
            )
        except PtahShellError:
            pass

    def on_created(self, event):
        if isinstance(event, FileModifiedEvent):
            self.copy(event.src_path)
        elif isinstance(event, events.DirCreatedEvent):
            if target := self.foo__(event.src_path):
                self.exec("mkdir", "-p", target)

    def on_deleted(self, event):
        if isinstance(event, FileDeletedEvent):
            self.delete(event.src_path)

    def on_modified(self, event):
        if isinstance(event, FileModifiedEvent):
            self.copy(event.src_path)

    def on_moved(self, event: DirMovedEvent | FileMovedEvent):
        if not isinstance(event.src_path, str) or not isinstance(event.dest_path, str):
            # TODO: warning.
            return
        source_path = Path(event.src_path)
        target_path = Path(event.dest_path)
        if self.is_relevant(source_path):
            source_relative = source_path.relative_to(self.image.location.parent)
            target_relative = target_path.relative_to(self.image.location.parent)
            source = os.path.join(self.target, source_relative)
            target = os.path.join(self.target, target_relative)
            print(f"{self.pod}/{self.container}:({source} -> {target})")
            self.shell(
                "kubectl",
                "exec",
                self.pod,
                "-c",
                self.container,
                "--",
                "mv",
                source,
                target
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
