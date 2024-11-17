import subprocess
import sys
from dataclasses import dataclass
from typing import List

from injector import inject
from rich.console import Console
from rich.syntax import Syntax


@inject
@dataclass
class Shell:
    """
    Handle interactions with the shell.

    Ptah heavily leverages CLIs like `kubectl` instead of the underlying REST APIs to provide
    easily copy/pasteable commands to users.
    """

    console: Console

    def __call__(self, *args: str) -> str:
        return self.run(list(args))

    def run(self, args: List[str]) -> str:
        """
        Run the provided set of arguments, providing a friendly "in progress" message to the
        console, then return the (stripped and decoded) standard output.

        TODO: follow https://janakiev.com/blog/python-shell-commands/ and stream output.
        """
        syntax = Syntax(" ".join(args), "bash")
        with self.console.status(syntax):
            result = subprocess.run(
                args, stderr=subprocess.PIPE, stdout=subprocess.PIPE
            )

            if result.returncode != 0:
                # https://johnlekberg.com/blog/2020-04-03-codec-errors.html
                self.console.print(result.stdout.decode(errors="replace"))
                self.console.print(result.stderr.decode(errors="replace"))
                self.console.print(
                    f"[red]💥 The command below exited with status {result.returncode}:[/red]"
                )
                self.console.print(syntax)
                sys.exit(result.returncode)

        return result.stdout.decode(errors="replace").strip()
