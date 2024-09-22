import platform
from typing import Type, TypeVar

from injector import Injector, Module, provider, singleton

from ptah.models import OperatingSystem

T = TypeVar("T")


class Builder(Module):
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


def get(interface: Type[T]) -> T:
    return Injector([Builder()], auto_bind=True).get(interface)
