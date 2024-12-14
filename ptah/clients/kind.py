import shutil
from dataclasses import dataclass
from pathlib import Path

from injector import inject

from ptah.clients.filesystem import Filesystem
from ptah.clients.shell import Shell
from ptah.clients.yaml import Yaml
from ptah.models import OperatingSystem, Project


@inject
@dataclass
class Kind:
    """
    Wrap interactions with the Kind CLI.
    """

    filesystem: Filesystem
    os: OperatingSystem
    project: Project
    shell: Shell
    yaml: Yaml

    def path(self) -> Path | None:
        if self.project.kind.config:
            return self.filesystem.project_root() / self.project.kind.config

    def cluster_name(self):
        if rv := self.project.kind.name:
            return rv
        path = self.path()
        if path and path.is_file() and (rv := self.yaml.parse(path).get("name")):
            return rv

        raise RuntimeError("Cluster name must be defined in ptah.yml or Kind config")

    def ensure_installed(self):
        if not self.is_installed():
            self.install()

    def is_installed(self) -> bool:
        return bool(shutil.which(("kind")))

    def install(self):
        """
        https://kind.sigs.k8s.io/docs/user/quick-start/#installing-with-a-package-manager
        """
        match self.os:
            case OperatingSystem.MACOS:
                args = ["brew", "install", "kind"]
            case OperatingSystem.WINDOWS:
                args = ["winget", "install", "Kubernetes.kind"]
            # TODO: https://medium.com/@binitabharati/setting-up-kind-cluster-9393aacbef43
            case default:
                raise RuntimeError(f"Unsupported operating system {default}")

        self.shell.run(args)

    def clusters(self) -> list[str]:
        return self.shell("kind", "get", "clusters").splitlines()

    def create(self):
        name = self.cluster_name()
        if name not in self.clusters():
            args = ["kind", "create", "cluster"]
            if self.project.kind.name:
                args += ["--name", self.project.kind.name]
            if self.project.kind.config:
                args += [
                    f"--config={self.filesystem.project_root() / self.project.kind.config}"
                ]
            args += ["--wait", "2m"]
            self.shell(*args)

    def delete(self):
        self.shell("kind", "delete", "clusters", self.cluster_name())
