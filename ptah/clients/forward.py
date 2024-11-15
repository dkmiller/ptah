import json
from dataclasses import dataclass
from typing import List

from injector import inject
from jsonpath_ng import parse
from rich.console import Console

from ptah.clients.process import Process
from ptah.clients.shell import Shell
from ptah.models import Project


@dataclass
class Port:
    args: List[str]


@inject
@dataclass
class Forward:
    """
    Manage port-forwarding
    """

    console: Console
    process: Process
    project: Project
    shell: Shell

    def commands(self) -> List[List[str]]:
        rv = [["kubectl", "proxy", "--port", str(self.project.api_server.port)]]

        # https://stackoverflow.com/a/56259811
        deployments_raw = self.shell("kubectl", "get", "deployments", "-o", "json")
        deployments = json.loads(deployments_raw)
        # TODO: don't assume container ports and metadata names are in the same order.
        # https://stackoverflow.com/a/30683008/
        # TODO: [?(@.protocol=='TCP')]?
        # We assume the first port for a service is the "main" one.
        # Validate these using https://jsonpath.com/ .
        port_path = parse("$..ports[0].containerPort")
        name_path = parse("$..metadata.name")

        ports = [m.value for m in port_path.find(deployments)]
        names = [m.value for m in name_path.find(deployments)]

        assert len(ports) == len(names)

        for index, number in enumerate(ports):
            name = names[index]
            rv.append(
                ["kubectl", "port-forward", f"deployment/{name}", f"{number}:{number}"]
            )

        return rv

    def terminate(self):
        commands = self.commands()
        self.console.print(f"Terminating {len(commands)} port-forwarding processes")
        for args in commands:
            self.process.terminate(args)

    def ensure(self):
        commands = self.commands()
        self.console.print(f"Ensuring {len(commands)} port-forwarding processes")
        for args in commands:
            self.process.ensure(args)
