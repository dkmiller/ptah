import platform
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
        https://helmfile.readthedocs.io/en/latest/#installation
        """
        match self.os:
            case OperatingSystem.MACOS:
                args = ["brew", "install", "helmfile"]
            case OperatingSystem.WINDOWS:
                args = ["scoop", "install", "helmfile"]
            case OperatingSystem.LINUX:
                match platform.uname().machine:
                    case "arm64":
                        suffix = "arm64"
                    case "x86_64":
                        suffix = "amd64"
                    case default:
                        raise RuntimeError(f"Unsupported architecture {default}")
                url = f"https://github.com/helmfile/helmfile/releases/download/v0.169.2/helmfile_0.169.2_linux_{suffix}.tar.gz"
                tarball = self.filesystem.download(url)
                # https://stackoverflow.com/a/56182972
                shutil.unpack_archive(tarball, tarball.parent, filter="tar")
                args = [
                    "sudo",
                    "mv",
                    str(tarball.parent / "helmfile"),
                    "/usr/local/bin/helmfile",
                ]

        self.shell.run(args)
        if "diff" not in self.shell("helm", "plugin", "list"):
            # https://github.com/roboll/helmfile/issues/1182
            self.shell.run(
                ["helm", "plugin", "install", "https://github.com/databus23/helm-diff"]
            )

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
