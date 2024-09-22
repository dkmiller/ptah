import tomllib
from dataclasses import dataclass
from importlib.metadata import version as import_version

from injector import inject

from ptah.clients.filesystem import Filesystem
from ptah.models import PACKAGE_NAME


@inject
@dataclass
class Version:
    filesystem: Filesystem

    def version(self) -> str:
        pyproject = self.filesystem.pyproject()
        if pyproject.is_file():
            project = tomllib.loads(pyproject.read_text())
            return project["project"]["version"]

        return import_version(PACKAGE_NAME)
