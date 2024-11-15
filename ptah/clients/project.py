from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from injector import inject

from ptah.clients.filesystem import Filesystem
from ptah.clients.yaml import Yaml
from ptah.models import Project as Model


@inject
@dataclass
class Project:
    filesystem: Filesystem
    yaml: Yaml

    def load(self, path: Optional[Path] = None) -> Model:
        path = path or self.filesystem.project_path()
        return self.yaml.load(path, Model)
