import shutil
from dataclasses import dataclass

import httpx
from injector import inject

from ptah.clients.shell import Shell
from ptah.models import OperatingSystem


@inject
@dataclass
class Ksync:
    """
    https://ksync.github.io/ksync/
    """

    os: OperatingSystem
    shell: Shell

    def is_installed(self) -> bool:
        return bool(shutil.which("ksync"))

    def install(self):
        """
        https://kind.sigs.k8s.io/docs/user/quick-start/#installing-with-a-package-manager
        """
        match self.os:
            case OperatingSystem.LINUX | OperatingSystem.MACOS:
                response = httpx.get("https://ksync.github.io/gimme-that/gimme.sh")
                response.raise_for_status()
                install_script = response.text
                args = ["/bin/bash", "-c", install_script]
            case default:
                raise RuntimeError(f"Unsupported operating system {default}")

        self.shell.run(args)

    def ensure_installed(self):
        if not self.is_installed():
            self.install()
