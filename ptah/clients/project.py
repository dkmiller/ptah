from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from injector import inject

from ptah.clients.filesystem import Filesystem
from ptah.clients.yaml import Yaml
from ptah.models import Project


@inject
@dataclass
class ProjectClient:
    filesystem: Filesystem
    yaml: Yaml

    def load(self, path: Optional[Path] = None) -> Project:
        path = path or self.filesystem.project_path()
        return self.yaml.load(path, Project)
