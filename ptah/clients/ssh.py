import os
from dataclasses import dataclass

from injector import inject

from ptah.clients.shell import Shell


@inject
@dataclass
class Ssh:
    shell: Shell

    def run(self, app_name: str) -> None:
        """
        Follows:
        - https://stackoverflow.com/a/55897287
        - https://stackoverflow.com/a/52691455
        """
        pod_name = self.shell(
            "kubectl",
            "get",
            "pods",
            f"--selector=app={app_name}",
            "-o",
            "jsonpath={.items[0].metadata.name}",
        )
        command = f"kubectl exec -it {pod_name} -- /bin/bash"
        print(f"Running command\n\n\t{command}\n")
        os.system(command)
