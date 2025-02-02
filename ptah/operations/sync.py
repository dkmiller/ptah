import os
from contextlib import contextmanager
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Optional

from injector import inject
from pathspec import PathSpec
from pathspec.patterns.gitwildmatch import GitWildMatchPattern
from rich.console import Console
from watchdog import events
from watchdog.events import FileModifiedEvent, FileSystemEventHandler
from watchdog.observers import Observer

from ptah.clients import Docker, Kubernetes, Panic, PtahPanic, Shell
from ptah.models import DockerImage


@dataclass
class _Handler(FileSystemEventHandler):
    """
    Propagate file system changes from

    > `(Docker image root) / (source) ↦ (pod : container) / (target)`

    Imitates: https://github.com/katjuncker/node-kubycat/blob/main/src/Kubycat.ts
    """

    source: str
    pod: str
    container: str
    image: DockerImage
    target: str
    shell: Shell

    # https://stackoverflow.com/a/52390734
    def __hash__(self):
        return (
            hash(self.source)
            + hash(self.pod)
            + hash(self.container)
            + hash(self.target)
        )

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
        if path.is_relative_to(root) and path != root:
            if spec := self.dockerignore_spec(root):
                return not spec.match_file(path.relative_to(root))
            return True
        return False

    def relevant_target(self, pathish: bytes | str) -> Optional[str]:
        if not isinstance(pathish, str):
            self.shell.console.print(f"⚠️ Ignoring non-string path {pathish}")
            return
        path = Path(pathish)
        if self.is_relevant(path):
            relative = path.relative_to(self.image.location.parent)
            return os.path.join(self.target, relative)

    def copy(self, pathish: bytes | str):
        if target := self.relevant_target(pathish):
            self.shell.console.print(
                f"{pathish} ↦ {self.pod}/{self.container}:{target}"
            )
            self.safely_shell(
                "kubectl",
                "cp",
                pathish,
                f"{self.pod}:{target}",
                "-c",
                self.container,
            )

    def safely_shell(self, *args):
        """
        Some IDEs create "ephemeral" files, e.g. `4913`
        (Vim: https://github.com/neovim/neovim/issues/3460) or `.swp` that dissapear between a
        changed event and this library's attempt to copy / move it in the remote container.
        """
        try:
            self.shell(*args)
        except PtahPanic:
            pass

    def exec(self, *args):
        self.safely_shell(
            "kubectl", "exec", self.pod, "-c", self.container, "--", *args
        )

    def on_created(self, event):
        if isinstance(event, events.FileCreatedEvent):
            self.copy(event.src_path)
        elif isinstance(event, events.DirCreatedEvent):
            if target := self.relevant_target(event.src_path):
                self.exec("mkdir", "-p", target)

    def on_deleted(self, event):
        if target := self.relevant_target(event.src_path):
            self.exec("rm", "-rf", target)

    def on_modified(self, event):
        if isinstance(event, FileModifiedEvent):
            self.copy(event.src_path)

    def on_moved(self, event):
        if (source := self.relevant_target(event.src_path)) and (
            target := self.relevant_target(event.dest_path)
        ):
            self.shell.console.print(
                f"{self.pod}/{self.container}:({source} ↦ {target})"
            )
            self.safely_shell(
                "kubectl",
                "exec",
                self.pod,
                "-c",
                self.container,
                "--",
                "mv",
                source,
                target,
            )


@inject
@dataclass
class Sync:
    """
    Manages synchronization between local and remote filesystems.

    Algorithm:
    - Find all "container -> Docker image" mappings.
        - Need namespace + pod(s) ...
    - Find all "Docker image -> (copy: source -> target)" mappings.
    - For each (container, Docker image, copy: source -> target) spawn a filesystem event handler.
        - Handler watches (image root) / source for changes that pass the .dockerignore
        - Handler propagates the change via kubectl ... commands to the (namespace + pod + container).
    """

    console: Console
    docker: Docker
    kubernetes: Kubernetes
    panic: Panic
    shell: Shell

    @contextmanager
    def run(self):
        images = self.docker.image_definitions()
        observer = Observer()
        for pod in self.kubernetes.pods()["items"]:
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
                            self.console.print(
                                f"Syncing {copy_statement.source} ↦ {pod_name}/{container_name}:{copy_statement.target}"
                            )
                            observer.schedule(
                                event_handler,
                                str(image.location.parent),
                                recursive=True,
                            )
        if not observer._handlers:
            self.panic(
                "No Docker COPY statements with absolute statements found or used"
            )

        observer.start()
        try:
            yield
        finally:
            observer.stop()
            observer.join()
