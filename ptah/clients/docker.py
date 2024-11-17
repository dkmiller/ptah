from dataclasses import dataclass

from cachelib import BaseCache
from injector import inject

from ptah.clients.shell import Shell
from ptah.models import Project


@inject
@dataclass
class Docker:
    cache: BaseCache
    project: Project
    shell: Shell
