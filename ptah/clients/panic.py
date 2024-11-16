from dataclasses import dataclass

from injector import inject
from rich.console import Console


class PtahPanic(SystemExit):
    pass


@inject
@dataclass
class Panic:
    console: Console

    def __call__(self, message: str):
        self.console.print(f"[bold red]{message}[/bold red]")
        raise PtahPanic(1)
