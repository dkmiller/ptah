import re
from dataclasses import dataclass
from pathlib import Path

from inflect import engine
from injector import inject
from rich.console import Console

from ptah.clients.filesystem import Filesystem
from ptah.clients.shell import Shell
from ptah.models import Project


@inject
@dataclass
class Kubernetes:
    console: Console
    engine: engine
    filesystem: Filesystem
    project: Project
    shell: Shell

    def build(self):
        source = self.filesystem.project_root()
        target = source / self.project.build_output
        self.filesystem.delete(target)

        manifests = [
            p
            for p in Path(source).rglob("*")
            if re.match(self.project.manifests, p.name)
        ]
        noun = self.engine.plural("manifest", len(manifests))  # type: ignore
        self.console.print(f"Copying {len(manifests)} {noun} to {target}")

        for manifest in manifests:
            content = manifest.read_text()
            relative = str(manifest.relative_to(source))
            target_path = Path(target) / relative
            target_path.parent.mkdir(parents=True, exist_ok=True)
            target_path.write_text(content)

    def apply(self):
        target = self.filesystem.project_root() / self.project.build_output

        if not any(Path(target).rglob("*.yaml")):
            self.console.print("Empty build target")
            return

        # https://stackoverflow.com/a/59493623
        output = self.shell("kubectl", "apply", "-R", "-f", str(target))
        watch = []
        skip = 0
        # TODO: stream events:
        # https://stackoverflow.com/a/51931477/2543689
        # kubectl get events --field-selector involvedObject.name=ui-deployment-7458788c98-szpxt
        for line in output.splitlines():
            resource, status = line.split(maxsplit=1)
            if resource.startswith("deployment.") and status != "unchanged":
                # https://linuxhint.com/kubectl-list-deployments/
                # kubectl rollout status deployment.apps/ui-deployment
                watch.append(["kubectl", "rollout", "status", resource])
            else:
                skip += 1

        noun = self.engine.plural("resource", len(watch))  # type: ignore
        msg = f"Watching {len(watch)} Kubernetes {noun}"
        if skip:
            msg += f" ({skip} unchanged)"
        self.console.print(msg)

        for w in watch:
            self.shell.run(w)
