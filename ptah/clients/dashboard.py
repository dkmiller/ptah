import webbrowser
from dataclasses import dataclass

import pyperclip
from injector import inject
from rich.console import Console

from ptah.clients.shell import Shell
from ptah.models import Project


@inject
@dataclass
class Dashboard:
    console: Console
    project: Project
    shell: Shell

    def open(self):
        # https://devops.stackexchange.com/a/9051
        namespace = self.shell(
            "kubectl",
            "get",
            "serviceaccounts",
            "--all-namespaces",
            "--field-selector",
            f"metadata.name={self.project.ui.user}",
            # https://stackoverflow.com/a/72493020
            # https://kubernetes.io/docs/reference/kubectl/jsonpath/
            "-o",
            "jsonpath={.items[0].metadata.namespace}",
        )

        token = self.shell(
            "kubectl", "-n", namespace, "create", "token", self.project.ui.user
        )

        url = self.url()
        self.console.print(
            f"Copy/pasting the token below and opening the URL:\n\n\t{token}\n\n\t{url}\n"
        )
        pyperclip.copy(token)
        webbrowser.open(url)

    def url(self) -> str:
        namespace = self.shell(
            "kubectl",
            "get",
            "services",
            "--all-namespaces",
            "--field-selector",
            f"metadata.name={self.project.ui.service}",
            "-o",
            "jsonpath={.items[0].metadata.namespace}",
        )
        return f"http://localhost:{self.project.api_server.port}/api/v1/namespaces/{namespace}/services/https:{self.project.ui.service}:https/proxy/"
