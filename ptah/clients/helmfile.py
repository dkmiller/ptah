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

    def helmfile_exists(self, target: Path) -> bool:
        helmfile = target / "helmfile.yaml"
        return helmfile.is_file()

    def sync(self, target: Path | None = None) -> None:
        target = target or self.filesystem.project_root()
        if self.helmfile_exists(target):
            self.ensure_installed()
            self.console.print("Syncing Helmfile")
            self.shell("helmfile", "sync")

    def apply(self, target: Path | None = None) -> None:
        target = target or self.filesystem.project_root()
        if self.helmfile_exists(target):
            self.console.print("Applying Helmfile")
            self.shell("helmfile", "apply")
