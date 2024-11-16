import json
import webbrowser
from dataclasses import dataclass

import pyperclip
from injector import inject
from rich.console import Console

from ptah.clients.jsonpath import Jsonpath
from ptah.clients.shell import Shell
from ptah.models import Project


@inject
@dataclass
class Dashboard:
    console: Console
    jsonpath: Jsonpath
    project: Project
    shell: Shell

    def open(self):
        # https://devops.stackexchange.com/a/9051
        output = self.shell(
            "kubectl", "get", "serviceaccounts", "--all-namespaces", "-o", "json"
        )
        service_accounts = json.loads(output)
        namespace = self.jsonpath.find(
            f"$.items[?(@.metadata.name == '{self.project.ui.user}')].metadata.namespace",
            service_accounts,
        )[0]
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
        output = self.shell(
            "kubectl", "get", "services", "--all-namespaces", "-o", "json"
        )
        services = json.loads(output)
        namespace = self.jsonpath.find(
            f"$.items[?(@.metadata.name == '{self.project.ui.service}')].metadata.namespace",
            services,
        )[0]
        return f"http://localhost:{self.project.api_server.port}/api/v1/namespaces/{namespace}/services/https:{self.project.ui.service}:https/proxy/"
