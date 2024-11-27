import shutil
from dataclasses import dataclass
from pathlib import Path

from injector import inject
from rich.console import Console

from ptah.clients.filesystem import Filesystem
from ptah.clients.shell import Shell
from ptah.models import OperatingSystem


@inject
@dataclass
class Helmfile:
    """
    Wrap interactions with the [Helmfile](https://github.com/helmfile/helmfile) CLI.
    """

    console: Console
    filesystem: Filesystem
    os: OperatingSystem
    shell: Shell

    def is_installed(self) -> bool:
        return bool(shutil.which(("helmfile")))

    def install(self):
        """
        https://kind.sigs.k8s.io/docs/user/quick-start/#installing-with-a-package-manager
        """
        match self.os:
            case OperatingSystem.MACOS:
                args = ["brew", "install", "helmfile"]
            case OperatingSystem.WINDOWS:
                args = ["scoop", "install", "helmfile"]
            case default:
                raise RuntimeError(f"Unsupported operating system {default}")

        self.shell.run(args)

    def ensure_installed(self):
        if not self.is_installed():
            self.install()

    def path(self) -> Path:
        return self.filesystem.project_root() / "helmfile.yaml"

    def helmfile_exists(self) -> bool:
        return self.path().is_file()

    def sync(self) -> None:
        if self.helmfile_exists():
            self.ensure_installed()
            self.console.print("Syncing Helmfile")
            self.shell("helmfile", "sync", "--file", str(self.path()))

    def apply(self) -> None:
        if self.helmfile_exists():
            self.console.print("Applying Helmfile")
            self.shell("helmfile", "apply", "--file", str(self.path()))
