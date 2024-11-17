import platform
from typing import Type, TypeVar

from cachelib import BaseCache, FileSystemCache
from injector import Injector, Module, provider, singleton
from rich.console import Console

from ptah.clients.filesystem import Filesystem
from ptah.clients.project import Project
from ptah.models import OperatingSystem
from ptah.models import Project as ProjectModel

T = TypeVar("T")


class Builder(Module):
    @singleton
    @provider
    def cache(self, filesystem: Filesystem) -> BaseCache:
        return FileSystemCache(str(filesystem.cache_location()))

    @singleton
    @provider
    def console(self) -> Console:
        return Console()

    @singleton
    @provider
    def operating_system(self) -> OperatingSystem:
        match platform.system().lower():
            case "darwin":
                return OperatingSystem.MACOS
            case "linux":
                return OperatingSystem.LINUX
            case "windows":
                return OperatingSystem.WINDOWS
            case default:
                raise RuntimeError(f"Unknown operating system {default}")

    @singleton
    @provider
    def project(self, client: Project) -> ProjectModel:
        return client.load()


def get(interface: Type[T]) -> T:
    return Injector([Builder()], auto_bind=True).get(interface)
