import shutil
from dataclasses import dataclass

from injector import inject

from ptah.clients.shell import ShellClient
from ptah.models import OperatingSystem, Project


@inject
@dataclass
class Kind:
    """
    Wrap interactions with the Kind CLI.
    """

    os: OperatingSystem
    shell: ShellClient

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
            case default:
                raise RuntimeError(f"Unsupported operating system {default}")

        self.shell.run(args)

    def clusters(self) -> list[str]:
        return self.shell("kind", "get", "clusters").splitlines()

    def create(self, project: Project):
        if project.kind.name not in self.clusters():
            self.shell(
                "kind", "create", "cluster", "--name", project.kind.name, "--wait", "2m"
            )
